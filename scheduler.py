import asyncio
import random
from datetime import datetime
from config import (
    TWITCH_INITIAL_CHANNELS,
    STREAM_SCHEDULE,
)  # Import the initial channels list


async def check_stream_status(bot):
    """
    Checks if the streamer is live and sends a message indicating how early or late the stream is,
    or if it's a secret stream. Only sends the message 3 times.
    """
    message_count = 0
    while message_count < 3:
        now = datetime.now()
        day_of_week = now.strftime("%A").lower()  # Get the current day of the week
        scheduled_time_str = STREAM_SCHEDULE.get(
            day_of_week
        )  # Get the scheduled time for today

        # Check if the streamer is live using Twitch API
        is_live = True  # Placeholder for actual live check

        if scheduled_time_str:
            scheduled_time = datetime.strptime(scheduled_time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if scheduled_time < now:  # Stream is late
                delta = now - scheduled_time
                late_messages = [
                    f"Can you believe it? The stream is {delta.seconds} seconds late! Maybe Peks got lost on the way to the chair.",
                    f"Oops! Looks like the stream is running {delta.seconds} seconds behind. Time to spam Peks!",
                    f"Streamer's timekeeping 101: Being {delta.seconds} seconds late is fashionable, right?",
                ]
                message = random.choice(late_messages)
            else:  # Stream is early
                delta = scheduled_time - now
                early_messages = [
                    f"Breaking news: The stream is {delta.seconds} seconds early! Quick, someone check if Peks is feeling ok!",
                    f"Alert! The stream is {delta.seconds} seconds ahead of schedule. Is this a new record?",
                    f"Whoa, {delta.seconds} seconds early? Peks must've been eager to stream today!",
                ]
                message = random.choice(early_messages)
        else:
            # No scheduled time for today, assume it's a secret stream
            message = "Surprise! It looks like we've got a secret stream on our hands. What mysteries will Peks unveil today?"

        if is_live:
            for channel in TWITCH_INITIAL_CHANNELS:
                await bot.get_channel(channel).send(message)
            message_count += 1

        await asyncio.sleep(60 * 5)  # Check every 5 minutes


async def start_scheduler(bot):
    """
    Starts the scheduler for sending periodic messages and checking stream status.
    """
    asyncio.create_task(
        send_periodic_messages(bot, 1, "TEST MESSAGE ON A TIMED SCHEDULE")
    )
    asyncio.create_task(check_stream_status(bot))


async def send_periodic_messages(
    bot, interval_hours, message="Remember to stay hydrated and take breaks!"
):
    """
    Sends periodic messages to the Twitch chat at specified intervals.

    :param bot: The instance of the bot to send messages through.
    :param interval_hours: interval in hours at which messages are sent.
    :param message: The message to be sent periodically.
    """
    while True:
        await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
        for channel in TWITCH_INITIAL_CHANNELS:  # Use the imported list
            await bot.get_channel(channel).send(message)
