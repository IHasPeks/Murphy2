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
from logging.handlers import RotatingFileHandler
from typing import Optional, Tuple, List
from twitchio.ext import commands
from utils import suggest_alwase_variants, shazdm
from commands import handle_command
from scheduler import start_scheduler
from queue_manager import QueueManager
from ai_command import handle_ai_command, start_periodic_save
from config import (
    TWITCH_TOKEN,
    TWITCH_CLIENT_ID,
    TWITCH_PREFIX,
    MOD_PREFIX,
    TWITCH_INITIAL_CHANNELS,
    LOG_LEVEL,
    LOG_FILE,
)

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
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
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
        self._validate_config()

        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix=TWITCH_PREFIX,
            mod_prefix=MOD_PREFIX,
            initial_channels=TWITCH_INITIAL_CHANNELS,
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
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def _validate_config(self):
        """Validate critical configuration parameters before starting the bot"""
        missing_configs = []

        if not TWITCH_TOKEN:
            missing_configs.append("TWITCH_TOKEN")

        if not TWITCH_CLIENT_ID:
            missing_configs.append("TWITCH_CLIENT_ID")

        if not TWITCH_INITIAL_CHANNELS:
            missing_configs.append("TWITCH_INITIAL_CHANNELS")

        if missing_configs:
            error_msg = f"Missing critical configuration parameters: {', '.join(missing_configs)}"
            logger.critical(error_msg)
            raise ValueError(error_msg)

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
        from commands import cannon_count, quadra_count, penta_count
        if command_name == "cannon":
            return cannon_count
        elif command_name == "quadra":
            return quadra_count
        elif command_name == "penta":
            return penta_count
        return 0

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
        logger.info(f"Logged in as | {self.nick}")
        try:
            await start_scheduler(self)
            self.queue_manager.start_cleanup_task(self.loop)

            # Start the AI cache save task
            start_periodic_save(self.loop)

            # Start the dynamic command watcher
            from dynamic_commands import DynamicCommandManager
            dynamic_command_manager = DynamicCommandManager()
            dynamic_command_manager.start_command_watcher(self.loop)

            welcome_message = (
                "Murphy2 initialized. Murphy2 is in alpha and may break anytime. "
                "See known issues here: https://github.com/IHasPeks/Murphy2/issues. "
                "use ?about for more info"
            )
            await self._send_to_all_channels(welcome_message)
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def event_error(self, error: Exception, data=None) -> None:
        """Handle errors raised by the Twitch API."""
        self.error_count += 1

        # Log the full traceback for debugging
        error_msg = f"Error in Twitch API: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())

        # For critical errors that might require a restart
        if isinstance(error, (ConnectionError, TimeoutError)) or "connection" in str(error).lower():
            logger.warning("Connection-related error detected. Will attempt reconnection.")

    async def event_connection_error(self, connection_error) -> None:
        """Handle connection errors and attempt to reconnect with improved retry logic."""
        self.error_count += 1

        # Log the error with traceback
        logger.error(f"Connection error: {str(connection_error)}")
        logger.error(traceback.format_exc())

        # Check if we're reconnecting too quickly
        current_time = time.time()
        if current_time - self.last_reconnect_time < 60:  # If last reconnect was less than a minute ago
            self.reconnect_attempts += 1
        else:
            self.reconnect_attempts = 1

        self.last_reconnect_time = current_time

        # If we've had too many rapid reconnection attempts, restart the bot
        if self.reconnect_attempts >= 3:
            logger.warning(f"Too many reconnection attempts ({self.reconnect_attempts}). Restarting bot...")
            await self._restart_bot()
        else:
            logger.info(f"Attempting to reconnect... (attempt {self.reconnect_attempts})")

    async def event_disconnect(self) -> None:
        """Handle disconnection events."""
        logger.warning("Bot disconnected from Twitch")
        # We don't need to take action here as TwitchIO will attempt reconnection
        # If it fails, event_connection_error will be triggered

    async def event_reconnect(self) -> None:
        """Handle reconnection events."""
        logger.info("Bot reconnected to Twitch")
        # Reset the reconnection attempts counter on successful reconnect
        self.reconnect_attempts = 0

    async def _send_to_all_channels(self, message: str) -> None:
        """Helper method to send a message to all initial channels."""
        for channel in TWITCH_INITIAL_CHANNELS:
            try:
                channel_obj = self.get_channel(channel)
                if channel_obj:
                    await channel_obj.send(message)
                else:
                    logger.warning(f"Failed to get channel {channel}")
            except Exception as e:
                logger.error(f"Failed to send message to channel {channel}: {str(e)}")

    async def _check_owner_permissions(self, ctx) -> bool:
        """Helper method to check if user is the channel owner."""
        if ctx.author.name.lower() != ctx.channel.name.lower():
            await ctx.send("Sorry, this command is restricted to the channel owner only.")
            return False
        return True

    @commands.command(name="restart")
    async def restart_bot(self, ctx) -> None:
        """Command to restart the bot - channel owner only."""
        if not await self._check_owner_permissions(ctx):
            return

        logger.info(f"Bot restart initiated by channel owner: {ctx.author.name}")
        await ctx.send("Bot restart initiated. The bot will be back in a few seconds...")

        # Save current state before restarting
        self.save_state()

        # Restart with exponential backoff protection
        await self._restart_bot(initiated_by_user=True)

    async def _restart_bot(self, initiated_by_user=False):
        """Restart the bot with exponential backoff to prevent restart loops"""
        restart_count = 0

        if not initiated_by_user:
            # Only use backoff when not initiated by a user
            restart_count = self._increment_restart_count()

            # If we've restarted too many times, delay longer to prevent restart loops
            if restart_count > MAX_RESTART_ATTEMPTS:
                backoff_time = INITIAL_BACKOFF_TIME * (2 ** min(restart_count - 1, 10))  # Cap at 2^10
                logger.warning(f"Too many restart attempts ({restart_count}). Backing off for {backoff_time} seconds")

                try:
                    for channel in TWITCH_INITIAL_CHANNELS:
                        channel_obj = self.get_channel(channel)
                        if channel_obj:
                            await channel_obj.send(f"Bot experiencing issues. Backing off for {backoff_time} seconds before restart.")
                except Exception:
                    pass  # Ignore any error while trying to send messages before restart

                time.sleep(backoff_time)

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
            twitch_status = "CONNECTED" if self.is_ready() else "DISCONNECTED"

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
                f"👥 Connected Channels: {', '.join([ch for ch in self.connected_channels])}"
            ]

            await ctx.send("\n".join(health_report))
            logger.info("Health check performed")

        except Exception as e:
            await ctx.send(f"Error during health check: {str(e)}")
            logger.error(f"Health check error: {str(e)}")
            logger.error(traceback.format_exc())

    async def event_message(self, message) -> None:
        """Handle incoming chat messages."""
        # Ignore messages from the bot itself
        if message.author and message.author.name.lower() == self.nick.lower():
            return

        # Track message count and log
        self.message_count += 1

        # Log the message for debugging
        logger.debug(f"[{message.channel.name}] {message.author.name}: {message.content}")

        # Check if this is a new user we haven't seen before
        is_first_time_chatter = False
        if message.author and message.author.name not in self.known_users:
            self.known_users.add(message.author.name)
            is_first_time_chatter = True
            logger.info(f"New user detected: {message.author.name}")

            # If this is their first message and not a command, potentially respond with AI
            if not message.content.startswith(TWITCH_PREFIX) and not message.content.startswith(MOD_PREFIX):
                # Only respond to first-time chatters with a 25% chance to avoid spamming
                if random.random() < 0.25:
                    try:
                        # Create a welcome prompt based on their message
                        welcome_prompt = f"User {message.author.name} has joined the chat for the first time and said: '{message.content}'. Give them a warm welcome."

                        # Use the AI to generate a welcome message
                        from ai_command import handle_ai_command
                        await handle_ai_command(self, message, custom_prompt=welcome_prompt)
                        logger.info(f"Sent AI welcome to first-time chatter: {message.author.name}")
                    except Exception as e:
                        logger.error(f"Error sending AI welcome: {e}")
                        # Don't raise the exception - if AI fails, just continue

        # Process commands
        if message.content.startswith(TWITCH_PREFIX):
            self.command_count += 1
            try:
                if message.content[len(TWITCH_PREFIX):].lower().startswith("ai "):
                    # Handle AI command
                    from ai_command import handle_ai_command
                    await handle_ai_command(self, message)
                else:
                    # Handle other commands
                    from commands import handle_command
                    await handle_command(self, message)
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error processing command '{message.content}': {e}")
                logger.error(traceback.format_exc())
                await message.channel.send("Error processing command. Please try again later.")

        # Process mod commands
        elif message.content.startswith(MOD_PREFIX):
            if message.author.is_mod or message.author.name.lower() == message.channel.name.lower():
                self.command_count += 1
                try:
                    # Strip the prefix and extract the command
                    mod_command = message.content[len(MOD_PREFIX):].split(" ")[0].lower()

                    # Special case for restart command (should go through the command)
                    if mod_command == "restart" and message.author.name.lower() == message.channel.name.lower():
                        await self.restart_bot(message)
                    # Handle other mod commands
                    else:
                        # Call the appropriate method for this command
                        await self._handle_mod_command(message, mod_command)
                except Exception as e:
                    self.error_count += 1
                    logger.error(f"Error processing mod command '{message.content}': {e}")
                    logger.error(traceback.format_exc())
                    await message.channel.send("Error processing mod command. Please try again later.")
            else:
                await message.channel.send("Sorry, only moderators can use mod commands.")

        # Handle non-command messages - suggest variants for some common misspellings
        elif not message.content.startswith(TWITCH_PREFIX) and not message.content.startswith(MOD_PREFIX):
            await self.suggest_variants(message)

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
        if (
            not ctx.author.is_mod
            and ctx.author.name.lower() != ctx.channel.name.lower()
        ):
            await ctx.send("Sorry, this command is restricted to moderators only.")
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
        await ctx.send(self.queue_manager.join_queue(ctx.author.name))

    @commands.command(name="leave")
    async def leave_queue(self, ctx) -> None:
        await ctx.send(self.queue_manager.leave_queue(ctx.author.name))

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
        await ctx.send(self.queue_manager.make_available(ctx.author.name))

    @commands.command(name="nothere")
    async def make_not_available(self, ctx) -> None:
        await ctx.send(self.queue_manager.make_not_available(ctx.author.name))

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

    async def _handle_mod_command(self, message, mod_command):
        """Handle moderator-only commands"""
        # Extract command arguments
        args = message.content[len(MOD_PREFIX) + len(mod_command):].strip()

        # Convert to a command method name (e.g. 'fleave' -> 'force_kick_user')
        command_methods = {
            'fleave': self.force_kick_user,
            'fjoin': self.force_join_user,
            'moveup': self.move_user_up_command,
            'movedown': self.move_user_down_command,
            'teamsize': self.set_team_size,
            'shuffle': self.shuffle_queue,
            'clearqueue': self.clear_queue_command
        }

        if mod_command in command_methods:
            # Call the appropriate command method
            if args:
                await command_methods[mod_command](message, args)
            else:
                await command_methods[mod_command](message)
        else:
            await message.channel.send(f"Unknown mod command: {mod_command}")

if __name__ == "__main__":
    # Initialize global error handling
    try:
        # Add recovery mechanism - if the bot crashes repeatedly, wait longer before trying again
        crash_count_file = os.path.join("logs", "crash_count.txt")
        crash_count = 0

        if os.path.exists(crash_count_file):
            try:
                with open(crash_count_file, 'r') as f:
                    crash_count = int(f.read().strip())
            except:
                crash_count = 0

        # If we've crashed more than 5 times, add delay
        if crash_count > 5:
            wait_time = min(300, crash_count * 10)  # Max 5 minutes wait
            logger.warning(f"Multiple crashes detected. Waiting {wait_time} seconds before starting...")
            import time
            time.sleep(wait_time)

        # Track crash for future recovery
        with open(crash_count_file, 'w') as f:
            f.write(str(crash_count + 1))

        # Run the bot
        bot = MurphyAI()
        bot.run()

        # If we reach here without exception, reset crash count
        with open(crash_count_file, 'w') as f:
            f.write("0")

    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
        raise
