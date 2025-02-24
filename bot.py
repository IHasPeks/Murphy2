import random
import logging
import os
import sys
import subprocess
import signal
import pickle
import time
import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Tuple, List
from twitchio.ext import commands
from utils import suggest_alwase_variants, shazdm
from commands import handle_command
from scheduler import start_scheduler
from queue_manager import QueueManager
from ai_command import handle_ai_command
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


class MurphyAI(commands.Bot):
    def __init__(self) -> None:
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

        # Load any saved state if it exists
        self.load_state()

        logger.info("Bot initialized with configuration")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

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
            welcome_message = (
                "Murphy2 initialized. Murphy2 is in alpha and may break anytime. "
                "See known issues here: https://github.com/IHasPeks/Murphy2/issues. "
                "use ?about for more info"
            )
            await self._send_to_all_channels(welcome_message)
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            raise

    async def event_error(self, error: Exception, data=None) -> None:
        """Handle errors raised by the Twitch API."""
        self.error_count += 1
        logger.error(f"Error in Twitch API: {str(error)}")

    async def event_connection_error(self, connection_error) -> None:
        """Handle connection errors and attempt to reconnect."""
        self.error_count += 1
        logger.error(f"Connection error: {str(connection_error)}")
        logger.info("Attempting to reconnect...")

    async def event_disconnect(self) -> None:
        """Handle disconnection events."""
        logger.warning("Bot disconnected from Twitch")

    async def event_reconnect(self) -> None:
        """Handle reconnection events."""
        logger.info("Bot reconnected to Twitch")

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

        # Start new process
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
        logger.info("Bot restarting - shutting down current instance")
        os._exit(0)

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
        """Check the health status of various bot components."""
        if not await self._check_owner_permissions(ctx):
            return

        health_report = []

        # Check OpenAI connection
        try:
            from ai_command import check_ai_health
            ai_status = await check_ai_health()
            health_report.append(f"AI Service: {ai_status}")
        except Exception as e:
            health_report.append(f"AI Service: ERROR ({str(e)})")

        # Check Twitch connection
        try:
            # Simple check - if we can run this command, Twitch connection is working
            health_report.append("Twitch Connection: OK")
        except Exception as e:
            health_report.append(f"Twitch Connection: ERROR ({str(e)})")

        # Check queue system
        try:
            queue_size = len(self.queue_manager.queue) + len(self.queue_manager.overflow_queue)
            health_report.append(f"Queue System: OK ({queue_size} users in queue)")
        except Exception as e:
            health_report.append(f"Queue System: ERROR ({str(e)})")

        # Check system resources
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
            cpu_usage = process.cpu_percent(interval=0.5)
            health_report.append(f"Memory Usage: {memory_usage:.2f} MB")
            health_report.append(f"CPU Usage: {cpu_usage:.1f}%")
        except ImportError:
            health_report.append("System Resources: psutil not installed")
        except Exception as e:
            health_report.append(f"System Resources: ERROR ({str(e)})")

        # Send report
        await ctx.send("Bot Health Report:\n" + "\n".join(health_report))

    async def event_message(self, message) -> None:
        if message.echo:
            return

        # Increment message counter
        self.message_count += 1
        logger.info(f"Message from {message.author.name}: {message.content}")

        try:
            # Check for first-time chatters
            if message.author.name not in self.known_users:
                self.known_users.add(message.author.name)
                welcome_msg = f"Welcome {message.author.name} to the stream! 🎉"
                await message.channel.send(welcome_msg)
                ai_msg = message.content
                if not ai_msg.startswith(f"{TWITCH_PREFIX}ai "):
                    ai_msg = f"{TWITCH_PREFIX}ai Welcome this new viewer and suggest some stream commands they might enjoy based on: {message.content}"
                    await handle_ai_command(self, message, ai_msg)

            # Handle mod commands first
            if message.content.startswith(MOD_PREFIX):
                if not (
                    message.author.is_mod
                    or message.author.name.lower() == message.channel.name.lower()
                ):
                    await message.channel.send(
                        "You don't have permission to use mod commands!"
                    )
                    return

                command = message.content[len(MOD_PREFIX) :].split(" ")[0].lower()
                args = message.content[len(MOD_PREFIX) + len(command) :].strip()

                # Increment command counter
                self.command_count += 1

                if command in self.mod_commands:
                    await self.mod_commands[command](message, args)
                    return
                else:
                    await message.channel.send(f"Unknown mod command: {command}")
                    return

            # Handle regular commands
            if message.content.startswith(TWITCH_PREFIX):
                # Increment command counter
                self.command_count += 1

            await self.handle_commands(message)

            if message.content.startswith(TWITCH_PREFIX):
                command = message.content[len(TWITCH_PREFIX) :].split(" ")[0].lower()
                args = message.content[len(TWITCH_PREFIX) + len(command) :].strip()

                if command == "ai":
                    await handle_ai_command(self, message)
                else:
                    await handle_command(self, message)

            await self.suggest_variants(message)
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing message: {str(e)}")
            await message.channel.send(
                "An error occurred while processing your message."
            )

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
