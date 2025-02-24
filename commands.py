import random
import requests
import logging
import datetime
from config import TWITCH_PREFIX, STREAM_SCHEDULE
from utils import translate_text_to_english
from dynamic_commands import DynamicCommandManager

# Set up logging
logger = logging.getLogger(__name__)

# Initialize dynamic command manager
dynamic_commands = DynamicCommandManager()

# variables used for commands below
cannon_count = 0
quadra_count = 0
penta_count = 0


def set_command_counts(cannon=0, quadra=0, penta=0):
    """Set the command counters - used for state restoration"""
    global cannon_count, quadra_count, penta_count
    cannon_count = cannon
    quadra_count = quadra
    penta_count = penta
    logger.info(f"Command counts restored: cannon={cannon}, quadra={quadra}, penta={penta}")


async def handle_command(bot, message):
    global cannon_count
    global quadra_count
    global penta_count

    command = message.content[len(TWITCH_PREFIX) :].split(" ")[0].lower()
    args = message.content[len(TWITCH_PREFIX) + len(command) :].strip()

    # Check for dynamic command first
    dynamic_response = dynamic_commands.get_command(command)
    if dynamic_response:
        await message.channel.send(dynamic_response)
        return

    # Handle command addition/removal (mod only)
    if command == "addcmd" and (
        message.author.is_mod
        or message.author.name.lower() == message.channel.name.lower()
    ):
        if not args:
            await message.channel.send("Usage: ?addcmd <command_name> <response>")
            return
        try:
            cmd_name, cmd_response = args.split(" ", 1)
            result = dynamic_commands.add_command(cmd_name, cmd_response)
            await message.channel.send(result)
        except ValueError:
            await message.channel.send("Usage: ?addcmd <command_name> <response>")
        return

    if command == "delcmd" and (
        message.author.is_mod
        or message.author.name.lower() == message.channel.name.lower()
    ):
        if not args:
            await message.channel.send("Usage: ?delcmd <command_name>")
            return
        result = dynamic_commands.remove_command(args)
        await message.channel.send(result)
        return

    if command == "listcmds":
        await message.channel.send(dynamic_commands.list_commands())
        return

    # Original static commands

    elif command == "bye":
        await message.channel.send(
            f"{message.author.mention} is leaving, Peks will probably miss you.",
        )

    elif command == "brb":
        await message.channel.send(
            f"{message.author.mention} will be right back, probably grabbing more snacks.",
        )

    elif command == "returned":
        await message.channel.send(
            f"{message.author.mention} is back, yippee peepoArrive"
        )

    elif command == "lurk":
        await message.channel.send(
            f"{message.author.mention} is lurking, Peks appreciates your silent support. dogeLurk",
        )

    elif command == "penta":
        penta_count += 1
        await message.channel.send(f"Penta kill! Count: {penta_count}")

    elif command == "latege":
        now = datetime.datetime.now()
        day_of_week = now.strftime("%A").lower()

        # Get today's scheduled time if available
        scheduled_time_str = STREAM_SCHEDULE.get(day_of_week)

        if scheduled_time_str:
            scheduled_time = datetime.datetime.strptime(scheduled_time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )

            if scheduled_time < now:  # Stream is late
                delta = now - scheduled_time
                minutes_late = delta.seconds // 60
                await message.channel.send(f"The stream is currently {minutes_late} minutes late! Peks probably lost track of time again latege")
            else:  # Stream is early or on time
                delta = scheduled_time - now
                minutes_early = delta.seconds // 60
                await message.channel.send(f"Wow! The stream is actually {minutes_early} minutes early today! A new record? PogChamp")
        else:
            # Check if there's a scheduled stream tomorrow
            tomorrow = now + datetime.timedelta(days=1)
            tomorrow_day = tomorrow.strftime("%A").lower()
            tomorrow_stream = STREAM_SCHEDULE.get(tomorrow_day)

            if tomorrow_stream:
                await message.channel.send(f"No stream scheduled for today. Next stream is tomorrow at {tomorrow_stream}!")
            else:
                # Find the next scheduled stream
                days_ahead = 2
                while days_ahead <= 7:
                    future_date = now + datetime.timedelta(days=days_ahead)
                    future_day = future_date.strftime("%A").lower()
                    future_stream = STREAM_SCHEDULE.get(future_day)
                    if future_stream:
                        next_day = future_date.strftime("%A")
                        await message.channel.send(f"No stream today. Next stream is on {next_day} at {future_stream}!")
                        break
                    days_ahead += 1
                else:
                    await message.channel.send("No scheduled streams found for the upcoming week.")

    elif command == "joke":
        if random.randint(0, 1) == 0:
            await message.channel.send("we are not bringing this back...")
        else:
            joke_response = requests.get(
                "https://icanhazdadjoke.com", headers={"Accept": "application/json"}
            )
            if joke_response.status_code == 200:
                joke_data = joke_response.json()
                await message.channel.send(joke_data["joke"])
            else:
                await message.channel.send(
                    "Couldn't fetch a joke at the moment. Try again later!"
                )

    elif command == "t":
        text_to_translate = message.content[
            len(TWITCH_PREFIX) + len(command) + 1 :
        ].strip()
        if not text_to_translate:
            await message.channel.send("Couldnt translate text.")
            return
        translated_text, source_lang = translate_text_to_english(text_to_translate)
        await message.channel.send(
            f"Translation Result: {translated_text} (Translated from {source_lang})"
        )
    elif command == "spam":
        # Extract the message to spam, removing the command part
        spam_message = message.content[len(TWITCH_PREFIX) + len(command) + 1 :].strip()
        # Ensure the message is under 250 characters to avoid cutting it short
        if len(spam_message) > 250:
            spam_message = spam_message[:247] + "..."
        # Repeat the message as many times as possible without exceeding 500 characters
        repeated_message = (spam_message + " ").rstrip()
        while len(repeated_message + spam_message + " ") <= 500:
            repeated_message += " " + spam_message
        await message.channel.send(repeated_message)
    # elif command == "opgg":
    #     await message.channel.send("ADD OPGG LOOKUPS")
    elif command == "youtube":
        await message.channel.send(
            "Watch Peks' latest video dealdough here: https://www.youtube.com/watch?v=vE0iNgwDl8E ",
        )
    elif command == "cannon":
        cannon_count += 1  # Properly increment the cannon count
        await message.channel.send(f"Cannon count: {cannon_count}")
    elif command == "coin":
        result = "Heads" if random.randint(0, 1) == 0 else "Tails"
        await message.channel.send(
            f"Coin flip? Heads, Peks wins. Tails, you lose. Good luck! {result}",
        )


    elif command == "quadra":
        quadra_count += 1
        await message.channel.send(
            f"Quadra kill! Peks is on fire. Can he get the penta? Quadra count: {quadra_count}"
        )
    else:
        return
