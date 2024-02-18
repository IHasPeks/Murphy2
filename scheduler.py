import asyncio
from config import TWITCH_INITIAL_CHANNELS  # Import the initial channels list


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


async def start_scheduler(bot):
    """
    Starts the scheduler for sending periodic messages.

    :param bot: The instance of the bot to use for sending messages.
    """
    # You can adjust the interval and message as needed
    asyncio.create_task(send_periodic_messages(bot, 1, "TEST MESSAGE"))
