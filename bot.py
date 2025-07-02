"""
Main bot module for the MurphyAI Twitch Bot.

This module contains the core bot class and event handlers for
Twitch chat interactions, queue management, and bot administration.
"""

import datetime
import logging
import os
import pickle
import random
import signal
import subprocess
import sys
import time
import traceback
from logging.handlers import RotatingFileHandler
from twitchio.ext import commands

from config import (
    TWITCH_TOKEN,
    TWITCH_CLIENT_ID,
    TWITCH_PREFIX,
    MOD_PREFIX,
    TWITCH_INITIAL_CHANNELS,
    LOG_LEVEL,
    LOG_FILE,
)
from ai_command import handle_ai_command, start_periodic_save
from commands import handle_command
from cooldown_manager import cooldown_manager
from queue_manager import QueueManager
from scheduler import start_scheduler

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
    """
    Main bot class for MurphyAI Twitch Bot.
    
    Handles Twitch chat interactions, queue management, AI responses,
    and bot administration commands.
    """

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
            logger.warning("Failed to reset restart counter: %s", e)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received signal %s. Shutting down gracefully...", signum)
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
            logger.error("Failed to save bot state: %s", e)

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
                logger.error("Failed to load bot state: %s", e)
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
            logger.error("Failed to increment restart counter: %s", e)
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
        """Handle bot ready event and initialize services"""
        logger.info("Logged in as | %s", self.nick)
        try:
            await start_scheduler(self)
            self.queue_manager.start_cleanup_task(self.loop)

            # Start the AI cache save task
            start_periodic_save(self.loop)

            # Start the dynamic command watcher
            from dynamic_commands import DynamicCommandManager
            dynamic_command_manager = DynamicCommandManager()
            dynamic_command_manager.start_command_watcher(self.loop)

            # Start cooldown cleanup task
            await cooldown_manager.start_cleanup_task(self.loop)

            welcome_message = (
                "Murphy2 initialized. Murphy2 is in alpha and may break anytime. "
                "See known issues here: https://github.com/IHasPeks/Murphy2/issues. "
                "use ?about for more info"
            )
            await self._send_to_all_channels(welcome_message)
        except Exception as e:
            logger.error("Error during initialization: %s", str(e))
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
        logger.error("Connection error: %s", str(connection_error))
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
            logger.warning("Too many reconnection attempts (%d). Restarting bot...", self.reconnect_attempts)
            await self._restart_bot()
        else:
            logger.info("Attempting to reconnect... (attempt %d)", self.reconnect_attempts)

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
                    logger.warning("Failed to get channel %s", channel)
            except Exception as e:
                logger.error("Failed to send message to channel %s: %s", channel, str(e))

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

        logger.info("Bot restart initiated by channel owner: %s", ctx.author.name)
        await ctx.send("Bot restart initiated. The bot will be back in a few seconds...")

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
            logger.info("Restart attempt #%d", restart_count)

        # Start new process
        try:
            # Save current state before restarting
            self.save_state()

            if sys.platform.startswith('win'):
                # Windows implementation
                with subprocess.Popen(['start', 'python', __file__], shell=True):
                    pass
            else:
                # Unix implementation
                with subprocess.Popen(['python3', __file__],
                                start_new_session=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL):
                    pass

            # Exit current process
            logger.info("Bot restarting - shutting down current instance (initiated by user: %s)",
                        initiated_by_user)
            os._exit(0)
        except Exception as e:
            logger.critical("Failed to restart bot: %s", e)
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

        import platform

        import psutil

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
                f"👥 Connected Channels: {', '.join(list(self.connected_channels))}"
            ]

            await ctx.send("\n".join(health_report))
            logger.info("Health check performed")

        except Exception as e:
            await ctx.send(f"Error during health check: {str(e)}")
            logger.error("Health check error: %s", str(e))
            logger.error(traceback.format_exc())

    async def event_message(self, message) -> None:
        """Handle incoming chat messages."""
        # Check if message has an author
        if not message.author:
            logger.warning("Received message without author")
            return

        # Ignore messages from the bot itself
        if message.author.name.lower() == self.nick.lower():
            return

        # Track message count and log
        self.message_count += 1

        # Log the message for debugging
        logger.debug("[%s] %s: %s", message.channel.name, message.author.name, message.content)

        # Check if this is a new user we haven't seen before
        if message.author.name not in self.known_users:
            self.known_users.add(message.author.name)
            logger.info("New user detected: %s", message.author.name)

            # If this is their first message and not a command, potentially respond with AI
            if not message.content.startswith(TWITCH_PREFIX) and not message.content.startswith(MOD_PREFIX):
                # Only respond to first-time chatters with a 25% chance to avoid spamming
                if random.random() < 0.25:
                    try:
                        # Create a welcome prompt based on their message
                        welcome_prompt = (f"User {message.author.name} has joined the chat for the first time "
                                          f"and said: '{message.content}'. Give them a warm welcome.")

                        # Use the AI to generate a welcome message
                        await handle_ai_command(self, message, custom_prompt=welcome_prompt)
                        logger.info("Sent AI welcome to first-time chatter: %s", message.author.name)
                    except Exception as e:
                        logger.error("Error sending AI welcome: %s", e)
                        # Don't raise the exception - if AI fails, just continue

        # Let TwitchIO handle the message first for built-in commands
        await super().event_message(message)

        # Then handle custom command routing if not already handled
        if message.content.startswith(TWITCH_PREFIX):
            self.command_count += 1

            # Extract command name
            command_name = message.content[len(TWITCH_PREFIX):].split(" ")[0].lower()

            # Only process if it's not a built-in command
            if command_name not in [cmd.name for cmd in self.commands.values()]:
                if command_name.startswith("ai"):
                    # Handle AI command
                    try:
                        await handle_ai_command(self, message)
                        logger.info("AI command processed for %s", message.author.name)
                    except Exception as e:
                        logger.error("Error handling AI command: %s", e)
                elif command_name == "alwase":
                    # Handle alwase correction
                    try:
                        await self.suggest_variants(message)
                    except Exception as e:
                        logger.error("Error suggesting alwase variants: %s", e)
                elif command_name == "dms":
                    # Handle dms command
                    try:
                        await message.channel.send("dms? PauseChamp")
                        logger.info("DMS command processed for %s", message.author.name)
                    except Exception as e:
                        logger.error("Error handling DMS command: %s", e)
                else:
                    # Handle regular custom commands
                    try:
                        await handle_command(self, message)
                    except Exception as e:
                        logger.error("Error handling command: %s", e)

    async def suggest_variants(self, message) -> None:
        """Handle alwase correction command"""
        try:
            await message.channel.send("It's ALWASE gigaMadge")
        except Exception as e:
            logger.error("Error in suggest_variants: %s", e)

    async def _check_mod_permissions(self, ctx) -> bool:
        """Helper method to check if user is a moderator or the channel owner."""
        if not (ctx.author.is_mod or ctx.author.name.lower() == ctx.channel.name.lower()):
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return False
        return True

    @commands.command(name="teamsize")
    async def set_team_size(self, ctx, size: int) -> None:
        """Set the team size for the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return

        result = self.queue_manager.set_team_size(size)
        await ctx.send(result)

    @commands.command(name="join")
    async def join_queue(self, ctx) -> None:
        """Join the queue"""
        result = self.queue_manager.join_queue(ctx.author.name)
        await ctx.send(result)

    @commands.command(name="leave")
    async def leave_queue(self, ctx) -> None:
        """Leave the queue"""
        result = self.queue_manager.leave_queue(ctx.author.name)
        await ctx.send(result)

    @commands.command(name="fleave")
    async def force_kick_user(self, ctx, username: str) -> None:
        """Force kick a user from the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return
        result = self.queue_manager.force_kick(username)
        await ctx.send(result)

    @commands.command(name="fjoin")
    async def force_join_user(self, ctx, username: str) -> None:
        """Force join a user to the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return
        result = self.queue_manager.force_join(username)
        await ctx.send(result)

    @commands.command(name="moveup")
    async def move_user_up_command(self, ctx, username: str) -> None:
        """Move a user up in the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return
        result = self.queue_manager.move_user_up(username)
        await ctx.send(result)

    @commands.command(name="movedown")
    async def move_user_down_command(self, ctx, username: str) -> None:
        """Move a user down in the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return
        result = self.queue_manager.move_user_down(username)
        await ctx.send(result)

    @commands.command(name="Q")
    async def show_queue(self, ctx) -> None:
        """Show the current queue"""
        try:
            main_queue_msg, overflow_queue_msg = self.queue_manager.show_queue()
            await ctx.send(main_queue_msg)
            if overflow_queue_msg != "Overflow Queue is empty.":
                await ctx.send(overflow_queue_msg)
        except Exception as e:
            logger.error("Error showing queue: %s", e)

    @commands.command(name="here")
    async def make_available(self, ctx) -> None:
        """Mark yourself as available in the queue"""
        result = self.queue_manager.make_available(ctx.author.name)
        await ctx.send(result)

    @commands.command(name="nothere")
    async def make_not_available(self, ctx) -> None:
        """Mark yourself as not available in the queue"""
        result = self.queue_manager.make_not_available(ctx.author.name)
        await ctx.send(result)

    @commands.command(name="shuffle")
    async def shuffle_queue(self, ctx) -> None:
        """Shuffle the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return
        try:
            result = self.queue_manager.shuffle_teams()
            if "\n" in result:
                lines = result.split("\n")
                for line in lines:
                    await ctx.send(line)
            else:
                await ctx.send(result)
        except Exception as e:
            logger.error("Error shuffling queue: %s", e)

    @commands.command(name="clearqueue")
    async def clear_queue_command(self, ctx) -> None:
        """Clear the queue - moderator only."""
        if not await self._check_mod_permissions(ctx):
            return
        result = self.queue_manager.clear_queues()
        await ctx.send(result)


if __name__ == "__main__":
    try:
        bot = MurphyAI()
        bot.run()
    except Exception as e:
        logger.error("Critical error starting bot: %s", e)
        logger.error(traceback.format_exc())
        sys.exit(1)
