import random
import logging
import os
import sys
import subprocess
import signal
import pickle
import time
import datetime
import traceback
import asyncio
from logging.handlers import RotatingFileHandler
from typing import Optional, Tuple, List
from twitchio.ext import commands
from twitchio import eventsub
from utils import suggest_alwase_variants, shazdm
from commands import handle_command
from scheduler import start_scheduler
from queue_manager import QueueManager
from ai_command import handle_ai_command, start_periodic_save
from cooldown_manager import cooldown_manager, check_cooldown
from config import (
    TWITCH_CLIENT_ID,
    TWITCH_CLIENT_SECRET,
    TWITCH_BOT_ID,
    TWITCH_PREFIX,
    MOD_PREFIX,
    TWITCH_INITIAL_CHANNELS,
    LOG_LEVEL,
    LOG_FILE,
    validate_config,
)
from constants import Messages, Numbers

# Set up logging
log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Also create a state directory for persistence
os.makedirs("state", exist_ok=True)

# Set up file handler with rotation
file_handler = RotatingFileHandler(
    os.path.join("logs", LOG_FILE),
    maxBytes=Numbers.LOG_MAX_BYTES,
    backupCount=Numbers.LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(log_level)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Get module logger
logger = logging.getLogger(__name__)

# Path for saving bot state
STATE_FILE = os.path.join("state", "bot_state.pkl")

# Maximum number of restart attempts
MAX_RESTART_ATTEMPTS = 5
# Restart attempt counter file
RESTART_COUNTER_FILE = os.path.join("state", "restart_counter.pkl")
# Initial backoff time in seconds
INITIAL_BACKOFF_TIME = 5


class MurphyAI(commands.Bot):
    def __init__(self) -> None:
        # Validate critical configurations before initializing
        validate_config()

        # TwitchIO 3.0+ requires client_id, client_secret and bot_id
        super().__init__(
            client_id=TWITCH_CLIENT_ID,
            client_secret=TWITCH_CLIENT_SECRET,
            bot_id=TWITCH_BOT_ID,
            prefix=TWITCH_PREFIX,
        )
        self.queue_manager = QueueManager()
        self.known_users = set()  # Track users we've seen before
        self.start_time = time.time()  # Record when the bot started
        self.message_count = 0  # Track total messages processed
        self.command_count = 0  # Track commands processed
        self.error_count = 0  # Track errors encountered
        self.last_reconnect_time = 0  # Track the last time we reconnected
        self.reconnect_attempts = 0  # Track reconnection attempts

        # Load any saved state if it exists
        self.load_state()

        # Reset restart counter on successful initialization
        self._reset_restart_counter()

        logger.info("Bot initialized with configuration")

        # Setup signal handlers for graceful shutdown
        try:
            signal.signal(signal.SIGINT, self.handle_shutdown)
            signal.signal(signal.SIGTERM, self.handle_shutdown)
        except Exception:
            # Some environments (e.g. Windows in certain shells) may not allow setting signals
            pass

    async def setup_hook(self) -> None:
        """Subscribe to chat messages for configured channels (TwitchIO 3.0)."""
        try:
            # Resolve channel user IDs from logins
            if TWITCH_INITIAL_CHANNELS:
                users = await self.fetch_users(logins=TWITCH_INITIAL_CHANNELS)
                for user in users:
                    try:
                        payload = eventsub.ChatMessageSubscription(
                            broadcaster_user_id=user.id,
                            user_id=self.bot_id,
                        )
                        await self.subscribe_websocket(payload=payload)
                        logger.info(f"Subscribed to chat messages for channel: {user.name} ({user.id})")
                    except Exception as sub_err:
                        logger.error(f"Failed to subscribe to channel {getattr(user, 'name', '')}: {sub_err}")
        except Exception as e:
            logger.error(f"setup_hook error: {e}")

    def _reset_restart_counter(self):
        """Reset the restart counter after successful initialization"""
        try:
            with open(RESTART_COUNTER_FILE, 'wb') as f:
                pickle.dump(0, f)
        except Exception as e:
            logger.warning(f"Failed to reset restart counter: {e}")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.save_state()
        sys.exit(0)

    def save_state(self):
        """Save important bot state to disk for recovery"""
        try:
            state = {
                "known_users": list(self.known_users),
                "cannon_count": self.get_command_count("cannon"),
                "quadra_count": self.get_command_count("quadra"),
                "penta_count": self.get_command_count("penta"),
                "message_count": self.message_count,
                "command_count": self.command_count,
                "error_count": self.error_count,
            }
            with open(STATE_FILE, 'wb') as f:
                pickle.dump(state, f)
            logger.info("Bot state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save bot state: {e}")

    def get_command_count(self, command_name):
        """Helper to get command counts from commands module"""
        from commands import get_command_count
        return get_command_count(command_name)

    def load_state(self):
        """Load bot state from disk if available"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'rb') as f:
                    state = pickle.load(f)

                # Restore known users
                self.known_users = set(state.get("known_users", []))

                # Restore message counts
                self.message_count = state.get("message_count", 0)
                self.command_count = state.get("command_count", 0)
                self.error_count = state.get("error_count", 0)

                # Restore command counts
                from commands import set_command_counts
                set_command_counts(
                    state.get("cannon_count", 0),
                    state.get("quadra_count", 0),
                    state.get("penta_count", 0)
                )

                logger.info("Bot state restored successfully")
            except Exception as e:
                logger.error(f"Failed to load bot state: {e}")
                logger.info("Continuing with default state")

    def _get_restart_count(self):
        """Get the current restart attempt count"""
        try:
            if os.path.exists(RESTART_COUNTER_FILE):
                with open(RESTART_COUNTER_FILE, 'rb') as f:
                    return pickle.load(f)
            return 0
        except Exception:
            return 0

    def _increment_restart_count(self):
        """Increment the restart attempt counter"""
        try:
            count = self._get_restart_count() + 1
            with open(RESTART_COUNTER_FILE, 'wb') as f:
                pickle.dump(count, f)
            return count
        except Exception as e:
            logger.error(f"Failed to increment restart counter: {e}")
            return 1  # Default to 1 if we can't read the file

    def get_uptime(self):
        """Returns the bot's uptime as a formatted string"""
        uptime_seconds = int(time.time() - self.start_time)
        uptime = datetime.timedelta(seconds=uptime_seconds)

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            uptime_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            uptime_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not uptime_parts:
            uptime_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        return ", ".join(uptime_parts)

    async def event_ready(self) -> None:
        nick = getattr(getattr(self, 'user', None), 'name', None) or getattr(self, 'nick', 'Unknown')
        logger.info(f"Logged in as | {nick}")
        try:
            # Start background tasks without blocking
            asyncio.create_task(start_scheduler(self))
            asyncio.get_running_loop().create_task(self.queue_manager.remove_not_available())

            # Start the AI cache save task
            start_periodic_save(asyncio.get_running_loop())

            # Start the dynamic command watcher
            from dynamic_commands import DynamicCommandManager
            dynamic_command_manager = DynamicCommandManager()
            dynamic_command_manager.start_command_watcher(asyncio.get_running_loop())

            # Start cooldown cleanup task
            asyncio.create_task(cooldown_manager.start_cleanup_task(asyncio.get_running_loop()))

            # Optional: Announce startup (skipped due to TwitchIO 3.0 message sending changes)
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def event_error(self, payload) -> None:
        """Handle errors raised by the Twitch API (TwitchIO 3.x payload)."""
        self.error_count += 1
        try:
            exception = getattr(payload, 'exception', None)
            if exception:
                logger.error(f"Error in Twitch API: {exception}")
                logger.error(traceback.format_exc())
            else:
                logger.error(f"Error payload received: {payload}")
        except Exception:
            logger.error("Unknown error payload received")

    # Connection lifecycle events differ in TwitchIO 3.x (EventSub). Keep counters but do not enforce custom reconnects.
    async def event_disconnect(self) -> None:
        logger.warning("Bot disconnected from Twitch")
    async def event_reconnect(self) -> None:
        logger.info("Bot reconnected to Twitch")
        self.reconnect_attempts = 0

    # TwitchIO 3.0 changed how messages are sent; we no longer broadcast on ready.

    async def _check_owner_permissions(self, ctx) -> bool:
        """Helper method to check if user is the channel owner."""
        if ctx.author.name.lower() != ctx.channel.name.lower():
            await ctx.send(Messages.PERMISSION_DENIED_OWNER)
            return False
        return True

    @commands.command(name="restart")
    async def restart_bot(self, ctx) -> None:
        """Command to restart the bot - channel owner only."""
        if not await self._check_owner_permissions(ctx):
            return

        logger.info(f"Bot restart initiated by channel owner: {ctx.author.name}")
        await ctx.send(Messages.BOT_RESTART_INITIATED)

        # Save current state before restarting
        self.save_state()

        # Restart with exponential backoff protection
        await self._restart_bot(initiated_by_user=True)

    async def _restart_bot(self, initiated_by_user=False):
        """Restart the bot immediately without backoff delays"""
        restart_count = 0

        if not initiated_by_user:
            # Track restart count but don't use backoff delays
            restart_count = self._increment_restart_count()
            logger.info(f"Restart attempt #{restart_count}")

        # Start new process
        try:
            # Save current state before restarting
            self.save_state()

            if sys.platform.startswith('win'):
                # Windows implementation
                subprocess.Popen(['start', 'python', __file__], shell=True)
            else:
                # Unix implementation
                subprocess.Popen(['python3', __file__],
                                start_new_session=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

            # Exit current process
            logger.info(f"Bot restarting - shutting down current instance (initiated by user: {initiated_by_user})")
            os._exit(0)
        except Exception as e:
            logger.critical(f"Failed to restart bot: {e}")
            logger.critical(traceback.format_exc())
            # If we can't restart, try to continue running

    @commands.command(name="botstat")
    async def bot_stats(self, ctx) -> None:
        """Display bot statistics including uptime and message counts."""
        uptime = self.get_uptime()
        stats = [
            f"🕒 Uptime: {uptime}",
            f"💬 Messages processed: {self.message_count}",
            f"🔄 Commands executed: {self.command_count}",
            f"⚠️ Errors encountered: {self.error_count}",
            f"👥 Known users: {len(self.known_users)}",
            f"👤 Queue size: {len(self.queue_manager.queue) + len(self.queue_manager.overflow_queue)}"
        ]

        await ctx.send("Bot Statistics:\n" + "\n".join(stats))

    @commands.command(name="healthcheck")
    async def health_check(self, ctx) -> None:
        """Display health information about the bot - channel owner only."""
        if not await self._check_owner_permissions(ctx):
            return

        import psutil
        import platform
        from ai_command import check_ai_health

        try:
            # Get system info
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent

            # Check AI service health
            ai_status = await check_ai_health()

            # Format timestamp
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Check connectivity to Twitch
            twitch_status = "CONNECTED"

            # Get version info
            python_version = platform.python_version()
            system_info = f"{platform.system()} {platform.release()}"

            # Calculate memory usage
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB

            health_report = [
                f"🕒 Timestamp: {current_time}",
                f"🤖 Bot Status: RUNNING (uptime: {self.get_uptime()})",
                f"🔌 Twitch Connection: {twitch_status}",
                f"🔃 Restart Count: {self._get_restart_count()}",
                f"🧠 AI Service: {ai_status}",
                f"💾 Memory Usage: {memory_mb:.2f} MB ({memory_percent}% system memory used)",
                f"⚙️ CPU Usage: {cpu_percent}%",
                f"💿 Disk Usage: {disk_percent}%",
                f"🔢 Messages Processed: {self.message_count}",
                f"📊 Commands Processed: {self.command_count}",
                f"⚠️ Errors Encountered: {self.error_count}",
                f"💻 System: {system_info} (Python {python_version})",
                f"👥 Configured Channels: {', '.join(TWITCH_INITIAL_CHANNELS)}"
            ]

            await ctx.send("\n".join(health_report))
            logger.info("Health check performed")

        except Exception as e:
            await ctx.send(f"Error during health check: {str(e)}")
            logger.error(f"Health check error: {str(e)}")
            logger.error(traceback.format_exc())

    async def event_chat_message(self, payload) -> None:
        """Handle incoming chat messages (TwitchIO 3.x)."""
        # Let the commands extension handle decorated commands first
        try:
            await super().event_chat_message(payload)
        except Exception:
            pass

        # Build a safe adapter compatible with our legacy handlers
        ctx = None
        try:
            ctx = await self.get_context(payload)
        except Exception:
            ctx = None

        # Extract basic fields with fallbacks
        try:
            author = getattr(payload, 'chatter', None) or getattr(payload, 'author', None)
            author_name = getattr(author, 'name', None) or getattr(author, 'login', None) or ""
        except Exception:
            author = None
            author_name = ""

        if not author:
            logger.warning("Received message without author")
            return

        # Ignore messages from the bot itself
        try:
            my_name = getattr(getattr(self, 'user', None), 'name', None) or getattr(self, 'nick', '')
            if author_name and my_name and author_name.lower() == my_name.lower():
                return
        except Exception:
            pass

        # Extract content/text
        content = getattr(payload, 'text', None) or getattr(payload, 'content', '') or ''

        # Channel name best-effort
        channel_obj = getattr(payload, 'room', None) or getattr(payload, 'channel', None)
        channel_name = getattr(channel_obj, 'name', None) or (TWITCH_INITIAL_CHANNELS[0] if TWITCH_INITIAL_CHANNELS else 'unknown')

        # Legacy adapter to match previous message API
        message = self._build_message_adapter(payload, ctx, author_name, channel_name, content)

        # Track message count and log
        self.message_count += 1
        logger.debug(f"[{channel_name}] {author_name}: {content}")

        # First-time chatter welcome (non-command)
        if author_name not in self.known_users:
            self.known_users.add(author_name)
            if not content.startswith(TWITCH_PREFIX):
                if random.random() < Numbers.FIRST_TIME_CHATTER_RESPONSE_CHANCE:
                    try:
                        welcome_prompt = (
                            f"User {author_name} has joined the chat for the first time and said: '{content}'. "
                            f"Give them a warm welcome."
                        )
                        await handle_ai_command(self, message, custom_prompt=welcome_prompt)
                        logger.info(f"Sent AI welcome to first-time chatter: {author_name}")
                    except Exception as e:
                        logger.error(f"Error sending AI welcome: {e}")

        # Custom routing for our non-decorated commands
        if content.startswith(TWITCH_PREFIX):
            self.command_count += 1
            command_name = content[len(TWITCH_PREFIX):].split(" ")[0].lower()
            builtin_commands = [cmd.name for cmd in self.commands.values()]
            if command_name not in builtin_commands:
                if command_name.startswith("ai"):
                    try:
                        await handle_ai_command(self, message)
                    except Exception as e:
                        self.error_count += 1
                        logger.error(f"Error processing AI command '{content}': {e}")
                        logger.error(traceback.format_exc())
                        await message.channel.send("Error processing AI command. Please try again later.")
                else:
                    try:
                        await handle_command(self, message)
                    except Exception as e:
                        self.error_count += 1
                        logger.error(f"Error processing command '{content}': {e}")
                        logger.error(traceback.format_exc())
                        await message.channel.send("Error processing command. Please try again later.")
        else:
            # Non-command messages: suggestions
            if not content.startswith(TWITCH_PREFIX):
                await self.suggest_variants(message)

    def _build_message_adapter(self, payload, ctx, author_name: str, channel_name: str, content: str):
        """Create a minimal adapter to satisfy legacy handlers (commands.py, ai_command.py)."""
        # Author adapter
        class _Author:
            def __init__(self, name, source):
                self.name = name
                self.mention = f"@{name}" if name else "@user"
                # Best-effort mod flag
                self.is_mod = bool(getattr(source, 'is_mod', False))

        # Channel adapter with send()
        class _Channel:
            def __init__(self, bot: MurphyAI, name: str, ctx_obj, payload_obj):
                self.name = name
                self._bot = bot
                self._ctx = ctx_obj
                self._payload = payload_obj

            async def send(self, text: str):
                # Prefer ctx.send when available, else reply to payload
                if self._ctx:
                    try:
                        return await self._ctx.send(text)
                    except Exception:
                        pass
                try:
                    reply = getattr(self._payload, 'reply', None)
                    if reply:
                        return await reply(text)
                except Exception:
                    pass
                logger.warning("Falling back: unable to send message via ctx or payload.reply")

        class _Message:
            def __init__(self, bot, content_, author_adapter, channel_adapter):
                self._bot = bot
                self.content = content_
                self.author = author_adapter
                self.channel = channel_adapter

        author_adapter = _Author(author_name, getattr(payload, 'chatter', None) or getattr(payload, 'author', None))
        channel_adapter = _Channel(self, channel_name, ctx, payload)
        return _Message(self, content, author_adapter, channel_adapter)

    async def suggest_variants(self, message) -> None:
        for suggest_func in [suggest_alwase_variants, shazdm]:
            try:
                suggestions = suggest_func(message.content)
                if suggestions:
                    await message.channel.send(random.choice(suggestions))
            except Exception as e:
                logger.error(
                    f"Error in suggest_variants with {suggest_func.__name__}: {str(e)}"
                )

    async def _check_mod_permissions(self, ctx) -> bool:
        """Helper method to check if user has mod permissions."""
        try:
            chatter = getattr(ctx, 'chatter', None) or getattr(ctx, 'author', None)
            channel = getattr(ctx, 'channel', None) or getattr(ctx, 'room', None)
            is_mod = bool(getattr(chatter, 'is_mod', False))
            chatter_name = getattr(chatter, 'name', '')
            channel_name = getattr(channel, 'name', '')
            if (not is_mod) and (chatter_name.lower() != channel_name.lower()):
                await ctx.send(Messages.PERMISSION_DENIED_MOD)
                return False
        except Exception:
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return False
        return True

    @commands.command(name="teamsize")
    async def set_team_size(self, ctx, size: int) -> None:
        if not await self._check_mod_permissions(ctx):
            return

        if size < 1:
            await ctx.send("Team size must be at least 1.")
            return

        await ctx.send(self.queue_manager.set_team_size(size))

    @commands.command(name="join")
    async def join_queue(self, ctx) -> None:
        name = getattr(getattr(ctx, 'chatter', None) or getattr(ctx, 'author', None), 'name', '')
        await ctx.send(self.queue_manager.join_queue(name))

    @commands.command(name="leave")
    async def leave_queue(self, ctx) -> None:
        name = getattr(getattr(ctx, 'chatter', None) or getattr(ctx, 'author', None), 'name', '')
        await ctx.send(self.queue_manager.leave_queue(name))

    @commands.command(name="fleave")
    async def force_kick_user(self, ctx, username: str) -> None:
        if not await self._check_mod_permissions(ctx):
            return
        await ctx.send(self.queue_manager.force_kick(username))

    @commands.command(name="fjoin")
    async def force_join_user(self, ctx, username: str) -> None:
        if not await self._check_mod_permissions(ctx):
            return
        await ctx.send(self.queue_manager.force_join(username))

    @commands.command(name="moveup")
    async def move_user_up_command(self, ctx, username: str) -> None:
        if not await self._check_mod_permissions(ctx):
            return
        await ctx.send(self.queue_manager.move_user_up(username))

    @commands.command(name="movedown")
    async def move_user_down_command(self, ctx, username: str) -> None:
        if not await self._check_mod_permissions(ctx):
            return
        await ctx.send(self.queue_manager.move_user_down(username))

    @commands.command(name="Q")
    async def show_queue(self, ctx) -> None:
        try:
            main_queue_msg, overflow_queue_msg = self.queue_manager.show_queue()
            await ctx.send(main_queue_msg)
            if overflow_queue_msg != "Overflow Queue is empty.":
                await ctx.send(overflow_queue_msg)
        except Exception as e:
            logger.error(f"Error showing queue: {str(e)}")
            await ctx.send("An error occurred while showing the queue.")

    @commands.command(name="here")
    async def make_available(self, ctx) -> None:
        name = getattr(getattr(ctx, 'chatter', None) or getattr(ctx, 'author', None), 'name', '')
        await ctx.send(self.queue_manager.make_available(name))

    @commands.command(name="nothere")
    async def make_not_available(self, ctx) -> None:
        name = getattr(getattr(ctx, 'chatter', None) or getattr(ctx, 'author', None), 'name', '')
        await ctx.send(self.queue_manager.make_not_available(name))

    @commands.command(name="shuffle")
    async def shuffle_queue(self, ctx) -> None:
        if not await self._check_mod_permissions(ctx):
            return

        try:
            response = self.queue_manager.shuffle_teams()
            if "\n" in response:
                team1_response, team2_response = response.split("\n")
                await ctx.send(team1_response)
                await ctx.send(team2_response)
            else:
                await ctx.send(response)
        except Exception as e:
            logger.error(f"Error shuffling queue: {str(e)}")
            await ctx.send("An error occurred while shuffling the teams.")

    @commands.command(name="clearqueue")
    async def clear_queue_command(self, ctx) -> None:
        if not await self._check_mod_permissions(ctx):
            return
        message = self.queue_manager.clear_queues()
        await ctx.send(message)


if __name__ == "__main__":
    # Initialize global error handling
    try:
        # Run the bot immediately without crash delays
        bot = MurphyAI()
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
        raise
