"""
Task scheduler module for the MurphyAI Twitch bot.
Handles periodic tasks and stream status checking.
"""
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from config import TWITCH_INITIAL_CHANNELS, STREAM_SCHEDULE
from constants import Numbers, Security
from types import BotProtocol, ChannelName

logger = logging.getLogger(__name__)


class StreamStatusChecker:
    """Handles stream status checking and notifications."""

    def __init__(self, bot: BotProtocol):
        self.bot = bot
        self.message_count = 0
        self.max_messages = 3
        self.check_interval = 300  # 5 minutes in seconds

    async def start(self) -> None:
        """Start the stream status checking task."""
        await self.check_stream_status()

    async def check_stream_status(self) -> None:
        """
        Checks if the streamer is live and sends a message indicating how early or late the stream is,
        or if it's a secret stream. Only sends the message 3 times.
        """
        while self.message_count < self.max_messages:
            message = await self._generate_status_message()

            if message and await self._is_streamer_live():
                await self._broadcast_message(message)
                self.message_count += 1

            await asyncio.sleep(self.check_interval)

    async def _generate_status_message(self) -> Optional[str]:
        """Generate appropriate status message based on stream schedule."""
        now = datetime.now()
        day_of_week = now.strftime("%A").lower()
        scheduled_time_str = STREAM_SCHEDULE.get(day_of_week)

        if scheduled_time_str:
            scheduled_time = datetime.strptime(scheduled_time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )

            if scheduled_time < now:  # Stream is late
                return self._generate_late_message(now - scheduled_time)
            else:  # Stream is early
                return self._generate_early_message(scheduled_time - now)
        else:
            # No scheduled time for today, assume it's a secret stream
            return self._generate_secret_stream_message()

    def _generate_late_message(self, delta: timedelta) -> str:
        """Generate a random message for when the stream is late."""
        late_messages = [
            f"Can you believe it? The stream is {delta.seconds} seconds late! Maybe Peks got lost on the way to the chair.",
            f"Oops! Looks like the stream is running {delta.seconds} seconds behind. Time to spam Peks!",
            f"Streamer's timekeeping 101: Being {delta.seconds} seconds late is fashionable, right?",
        ]
        return random.choice(late_messages)

    def _generate_early_message(self, delta: timedelta) -> str:
        """Generate a random message for when the stream is early."""
        early_messages = [
            f"Breaking news: The stream is {delta.seconds} seconds early! Quick, someone check if Peks is feeling ok!",
            f"Alert! The stream is {delta.seconds} seconds ahead of schedule. Is this a new record?",
            f"Whoa, {delta.seconds} seconds early? Peks must've been eager to stream today!",
        ]
        return random.choice(early_messages)

    def _generate_secret_stream_message(self) -> str:
        """Generate a message for unscheduled streams."""
        return "Surprise! It looks like we've got a secret stream on our hands. What mysteries will Peks unveil today?"

    async def _is_streamer_live(self) -> bool:
        """Check if the streamer is currently live."""
        # TODO: Implement actual Twitch API check
        # For now, return True as placeholder
        return True

    async def _broadcast_message(self, message: str) -> None:
        """Broadcast a message to all connected channels."""
        for channel_name in TWITCH_INITIAL_CHANNELS:
            try:
                channel = self.bot.get_channel(channel_name)
                if channel:
                    await channel.send(message)
                else:
                    logger.warning(f"Failed to get channel: {channel_name}")
            except Exception as e:
                logger.error(f"Error sending message to {channel_name}: {e}")


class PeriodicMessageSender:
    """Handles sending periodic messages to channels."""

    def __init__(self, bot: BotProtocol):
        self.bot = bot
        self.tasks: List[asyncio.Task] = []

    async def add_periodic_message(
        self,
        interval_hours: float,
        message: str = "Remember to stay hydrated and take breaks!",
        channels: Optional[List[ChannelName]] = None
    ) -> None:
        """
        Add a periodic message task.

        Args:
            interval_hours: Interval in hours between messages
            message: The message to send
            channels: List of channels to send to (defaults to all initial channels)
        """
        task = asyncio.create_task(
            self._send_periodic_messages(interval_hours, message, channels)
        )
        self.tasks.append(task)

    async def _send_periodic_messages(
        self,
        interval_hours: float,
        message: str,
        channels: Optional[List[ChannelName]] = None
    ) -> None:
        """Send periodic messages to specified channels."""
        channels = channels or TWITCH_INITIAL_CHANNELS
        interval_seconds = interval_hours * 3600

        while True:
            await asyncio.sleep(interval_seconds)

            for channel_name in channels:
                try:
                    channel = self.bot.get_channel(channel_name)
                    if channel:
                        await channel.send(message)
                    else:
                        logger.warning(f"Failed to get channel: {channel_name}")
                except Exception as e:
                    logger.error(f"Error sending periodic message to {channel_name}: {e}")

    def cancel_all(self) -> None:
        """Cancel all periodic message tasks."""
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()


class Scheduler:
    """Main scheduler that manages all scheduled tasks."""

    def __init__(self, bot: BotProtocol):
        self.bot = bot
        self.stream_checker = StreamStatusChecker(bot)
        self.message_sender = PeriodicMessageSender(bot)
        self.tasks: List[asyncio.Task] = []

    async def start(self) -> None:
        """Start all scheduled tasks."""
        # Start stream status checker
        stream_task = asyncio.create_task(self.stream_checker.start())
        self.tasks.append(stream_task)

        # Add any periodic messages here (currently disabled)
        # await self.message_sender.add_periodic_message(
        #     interval_hours=1,
        #     message="Remember to follow and subscribe!"
        # )

        logger.info("Scheduler started successfully")

    def stop(self) -> None:
        """Stop all scheduled tasks."""
        # Cancel stream checker tasks
        for task in self.tasks:
            task.cancel()

        # Cancel periodic message tasks
        self.message_sender.cancel_all()

        logger.info("Scheduler stopped")


# Legacy function for backwards compatibility
async def start_scheduler(bot: BotProtocol) -> None:
    """
    Start the scheduler for the bot.

    Args:
        bot: The bot instance
    """
    scheduler = Scheduler(bot)
    await scheduler.start()
