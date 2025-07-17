"""
Refactored MurphyAI bot class with better organization and separation of concerns
"""

import logging
import os
import signal
import sys
import subprocess
import traceback
from typing import Optional

from twitchio.ext import commands

from config import (
    TWITCH_TOKEN,
    TWITCH_CLIENT_ID,
    TWITCH_PREFIX,
    MOD_PREFIX,
    TWITCH_INITIAL_CHANNELS,
    validate_config,
)
from constants import Messages
from queue_manager import QueueManager
from .state import StateManager
from .events import EventHandler

logger = logging.getLogger(__name__)


class MurphyAI(commands.Bot):
    """
    Modern MurphyAI Twitch bot with clean architecture
    """

    def __init__(self) -> None:
        # Validate configuration
        validate_config()

        # Initialize TwitchIO bot
        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix=TWITCH_PREFIX,
            mod_prefix=MOD_PREFIX,
            initial_channels=TWITCH_INITIAL_CHANNELS,
        )

        # Initialize components
        self.state_manager = StateManager()
        self.queue_manager = QueueManager()
        self.event_handler = EventHandler(self)

        # Load saved state
        self.state_manager.load_state()

        # Reset restart counter on successful initialization
        self.state_manager.reset_restart_counter()

        logger.info("Bot initialized successfully")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.state_manager.save_state()
        sys.exit(0)

    async def restart_bot(self, initiated_by_user: bool = False) -> None:
        """Restart the bot with proper cleanup"""
        restart_count = 0

        if not initiated_by_user:
            restart_count = self.state_manager.increment_restart_count()
            logger.info(f"Restart attempt #{restart_count}")

        try:
            # Save current state
            self.state_manager.save_state()

            # Start new process
            if sys.platform.startswith('win'):
                subprocess.Popen(['start', 'python', __file__], shell=True)
            else:
                subprocess.Popen(['python3', __file__],
                                start_new_session=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

            logger.info(f"Bot restarting - shutting down current instance (initiated by user: {initiated_by_user})")
            os._exit(0)

        except Exception as e:
            logger.critical(f"Failed to restart bot: {e}")
            logger.critical(traceback.format_exc())

    # TwitchIO Event Handlers

    async def event_ready(self) -> None:
        """Bot is ready and connected"""
        await self.event_handler.handle_ready()

    async def event_message(self, message) -> None:
        """Handle incoming messages"""
        # Let TwitchIO handle built-in commands first
        await super().event_message(message)
        
        # Then handle custom logic
        await self.event_handler.handle_message(message)

    async def event_error(self, error: Exception, data=None) -> None:
        """Handle API errors"""
        await self.event_handler.handle_error(error, data)

    async def event_connection_error(self, connection_error) -> None:
        """Handle connection errors"""
        await self.event_handler.handle_connection_error(connection_error)

    async def event_disconnect(self) -> None:
        """Handle disconnection"""
        await self.event_handler.handle_disconnect()

    async def event_reconnect(self) -> None:
        """Handle reconnection"""
        await self.event_handler.handle_reconnect()

    # Built-in Commands

    @commands.command(name="restart")
    async def restart_command(self, ctx) -> None:
        """Restart the bot - channel owner only"""
        if ctx.author.name.lower() != ctx.channel.name.lower():
            await ctx.send(Messages.PERMISSION_DENIED_OWNER)
            return

        logger.info(f"Bot restart initiated by channel owner: {ctx.author.name}")
        await ctx.send(Messages.BOT_RESTART_INITIATED)

        await self.restart_bot(initiated_by_user=True)

    @commands.command(name="botstat")
    async def bot_stats(self, ctx) -> None:
        """Display bot statistics"""
        stats = self.state_manager.get_stats()
        
        stats_lines = [
            f"🕒 Uptime: {stats['uptime']}",
            f"💬 Messages processed: {stats['message_count']}",
            f"🔄 Commands executed: {stats['command_count']}",
            f"⚠️ Errors encountered: {stats['error_count']}",
            f"👥 Known users: {stats['known_users']}",
            f"👤 Queue size: {len(self.queue_manager.queue) + len(self.queue_manager.overflow_queue)}",
            f"🔃 Restart count: {stats['restart_count']}"
        ]

        await ctx.send("Bot Statistics:\n" + "\n".join(stats_lines))

    @commands.command(name="healthcheck")
    async def health_check(self, ctx) -> None:
        """Display health information - channel owner only"""
        if ctx.author.name.lower() != ctx.channel.name.lower():
            await ctx.send(Messages.PERMISSION_DENIED_OWNER)
            return

        try:
            import psutil
            import platform
            from datetime import datetime
            from ai_command import check_ai_health

            # Get system info
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent

            # Check AI service health
            ai_status = await check_ai_health()

            # Get stats
            stats = self.state_manager.get_stats()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            twitch_status = "CONNECTED" if self.is_ready() else "DISCONNECTED"
            python_version = platform.python_version()
            system_info = f"{platform.system()} {platform.release()}"
            memory_mb = memory_info.rss / 1024 / 1024

            health_report = [
                f"🕒 Timestamp: {current_time}",
                f"🤖 Bot Status: RUNNING (uptime: {stats['uptime']})",
                f"🔌 Twitch Connection: {twitch_status}",
                f"🔃 Restart Count: {stats['restart_count']}",
                f"🧠 AI Service: {ai_status}",
                f"💾 Memory Usage: {memory_mb:.2f} MB ({memory_percent}% system memory used)",
                f"⚙️ CPU Usage: {cpu_percent}%",
                f"💿 Disk Usage: {disk_percent}%",
                f"🔢 Messages Processed: {stats['message_count']}",
                f"📊 Commands Processed: {stats['command_count']}",
                f"⚠️ Errors Encountered: {stats['error_count']}",
                f"💻 System: {system_info} (Python {python_version})",
                f"👥 Connected Channels: {', '.join([ch for ch in self.connected_channels])}"
            ]

            await ctx.send("\n".join(health_report))
            logger.info("Health check performed")

        except Exception as e:
            await ctx.send(f"Error during health check: {str(e)}")
            logger.error(f"Health check error: {str(e)}")
            logger.error(traceback.format_exc())

    # Helper Methods

    def _check_mod_permissions(self, ctx) -> bool:
        """Check if user has mod permissions"""
        return (ctx.author.is_mod or 
                ctx.author.name.lower() == ctx.channel.name.lower())

    def _check_owner_permissions(self, ctx) -> bool:
        """Check if user is channel owner"""
        return ctx.author.name.lower() == ctx.channel.name.lower()

    # Queue Management Commands

    @commands.command(name="teamsize")
    async def set_team_size(self, ctx, size: int) -> None:
        """Set team size - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return

        if size < 1:
            await ctx.send("Team size must be at least 1.")
            return

        await ctx.send(self.queue_manager.set_team_size(size))

    @commands.command(name="join")
    async def join_queue(self, ctx) -> None:
        """Join the queue"""
        await ctx.send(self.queue_manager.join_queue(ctx.author.name))

    @commands.command(name="leave")
    async def leave_queue(self, ctx) -> None:
        """Leave the queue"""
        await ctx.send(self.queue_manager.leave_queue(ctx.author.name))

    @commands.command(name="fleave")
    async def force_kick_user(self, ctx, username: str) -> None:
        """Force kick user from queue - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return
        await ctx.send(self.queue_manager.force_kick(username))

    @commands.command(name="fjoin")
    async def force_join_user(self, ctx, username: str) -> None:
        """Force join user to queue - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return
        await ctx.send(self.queue_manager.force_join(username))

    @commands.command(name="moveup")
    async def move_user_up_command(self, ctx, username: str) -> None:
        """Move user up in queue - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return
        await ctx.send(self.queue_manager.move_user_up(username))

    @commands.command(name="movedown")
    async def move_user_down_command(self, ctx, username: str) -> None:
        """Move user down in queue - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return
        await ctx.send(self.queue_manager.move_user_down(username))

    @commands.command(name="Q")
    async def show_queue(self, ctx) -> None:
        """Show current queue"""
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
        """Mark yourself as available"""
        await ctx.send(self.queue_manager.make_available(ctx.author.name))

    @commands.command(name="nothere")
    async def make_not_available(self, ctx) -> None:
        """Mark yourself as not available"""
        await ctx.send(self.queue_manager.make_not_available(ctx.author.name))

    @commands.command(name="shuffle")
    async def shuffle_queue(self, ctx) -> None:
        """Shuffle teams - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
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
        """Clear the queue - moderator only"""
        if not self._check_mod_permissions(ctx):
            await ctx.send(Messages.PERMISSION_DENIED_MOD)
            return
        message = self.queue_manager.clear_queues()
        await ctx.send(message) 