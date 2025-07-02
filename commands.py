"""
Command handling module for the MurphyAI Twitch bot.
Manages both static and dynamic commands with proper state management.
"""
import datetime
import logging
import random
from typing import Optional, Dict, Tuple

import requests

from config import TWITCH_PREFIX, STREAM_SCHEDULE
from constants import Messages, Commands as CommandLists, Numbers
from utils import translate_text_to_english
from dynamic_commands import DynamicCommandManager
from cooldown_manager import cooldown_manager

# Set up logging
logger = logging.getLogger(__name__)

# Initialize dynamic command manager
dynamic_commands = DynamicCommandManager()


class CommandCounters:
    """Manages command counters with proper encapsulation."""

    def __init__(self):
        self.counters: Dict[str, int] = {
            'cannon': 0,
            'quadra': 0,
            'penta': 0
        }

    def increment(self, command: str) -> int:
        """Increment a counter and return the new value."""
        if command in self.counters:
            self.counters[command] += 1
            return self.counters[command]
        return 0

    def get(self, command: str) -> int:
        """Get the current value of a counter."""
        return self.counters.get(command, 0)

    def set_all(self, cannon: int = 0, quadra: int = 0, penta: int = 0) -> None:
        """Set all counters - used for state restoration."""
        self.counters['cannon'] = cannon
        self.counters['quadra'] = quadra
        self.counters['penta'] = penta
        logger.info("Command counts restored: cannon=%d, quadra=%d, penta=%d", cannon, quadra, penta)


# Global instance of command counters
command_counters = CommandCounters()


def set_command_counts(cannon: int = 0, quadra: int = 0, penta: int = 0) -> None:
    """Legacy function for backwards compatibility."""
    command_counters.set_all(cannon, quadra, penta)


def get_command_count(command_name: str) -> int:
    """Get the count for a specific command."""
    return command_counters.get(command_name)


async def handle_command(bot, message) -> None:
    """
    Main command handler that routes messages to appropriate command functions.

    Args:
        bot: The bot instance
        message: The message object from Twitch
    """
    command = message.content[len(TWITCH_PREFIX):].split(" ")[0].lower()
    args = message.content[len(TWITCH_PREFIX) + len(command):].strip()

    # Check if user is mod
    is_mod = message.author.is_mod or message.author.name.lower() == message.channel.name.lower()

    # Check cooldown for non-dynamic commands
    if command not in CommandLists.NO_COOLDOWN:
        on_cooldown, remaining = cooldown_manager.is_on_cooldown(
            command,
            message.author.name,
            is_mod
        )
        if on_cooldown:
            await message.channel.send(
                Messages.COMMAND_ON_COOLDOWN.format(
                    username=message.author.name,
                    seconds=remaining
                )
            )
            return

    # Check for dynamic command first
    command_result = dynamic_commands.get_command(command)
    if command_result:
        response, command_name = command_result
        await message.channel.send(response)
        # Set cooldown for dynamic commands
        cooldown_manager.set_cooldown(command_name, message.author.name)
        return

    # Handle dynamic command management
    if command in ['addcmd', 'addalias', 'delcmd', 'listcmds', 'cmdinfo']:
        await handle_dynamic_command_management(command, args, message, is_mod)
        return

    # Route to specific command handlers
    command_handler = get_command_handler(command)
    if command_handler:
        await command_handler(message, args)
        # Set cooldown after successful command execution
        cooldown_manager.set_cooldown(command, message.author.name)


async def handle_dynamic_command_management(command: str, args: str, message, is_mod: bool) -> None:
    """Handle commands related to dynamic command management."""
    # Check permissions for add/delete commands
    if command in ['addcmd', 'addalias', 'delcmd', 'cmdinfo'] and not is_mod:
        await message.channel.send(Messages.PERMISSION_DENIED_MOD)
        return

    if command == "addcmd":
        await handle_add_command(args, message)
    elif command == "addalias":
        await handle_add_alias(args, message)
    elif command == "delcmd":
        await handle_delete_command(args, message)
    elif command == "listcmds":
        await message.channel.send(dynamic_commands.list_commands())
    elif command == "cmdinfo":
        await handle_command_info(args, message)


async def handle_add_command(args: str, message) -> None:
    """Handle adding a new dynamic command."""
    if not args:
        await message.channel.send(Messages.COMMAND_USAGE_ADDCMD)
        return

    try:
        cmd_parts = args.split(" ", 1)
        if len(cmd_parts) < 2:
            await message.channel.send(Messages.COMMAND_USAGE_ADDCMD)
            return

        cmd_name, cmd_response = cmd_parts
        result = dynamic_commands.add_command(cmd_name, cmd_response)
        await message.channel.send(result)
    except ValueError:
        await message.channel.send(Messages.COMMAND_USAGE_ADDCMD)


async def handle_add_alias(args: str, message) -> None:
    """Handle adding a command with aliases."""
    if not args:
        await message.channel.send(Messages.COMMAND_USAGE_ADDALIAS)
        return

    try:
        parts = args.split(" ", 2)
        if len(parts) < 3:
            await message.channel.send(Messages.COMMAND_USAGE_ADDALIAS)
            return

        cmd_name, aliases_str, cmd_response = parts
        aliases = [a.strip() for a in aliases_str.split(",") if a.strip()]

        result = dynamic_commands.add_command(cmd_name, cmd_response, aliases)
        await message.channel.send(result)
    except ValueError:
        await message.channel.send(Messages.COMMAND_USAGE_ADDALIAS)


async def handle_delete_command(args: str, message) -> None:
    """Handle deleting a dynamic command."""
    if not args:
        await message.channel.send(Messages.COMMAND_USAGE_DELCMD)
        return

    result = dynamic_commands.remove_command(args)
    await message.channel.send(result)


async def handle_command_info(args: str, message) -> None:
    """Handle getting information about a command."""
    if not args:
        await message.channel.send("Usage: ?cmdinfo <command_name>")
        return

    result = dynamic_commands.get_command_details(args)
    await message.channel.send(result)


def get_command_handler(command: str):
    """Get the appropriate handler function for a command."""
    handlers = {
        "bye": handle_bye,
        "brb": handle_brb,
        "returned": handle_returned,
        "lurk": handle_lurk,
        "penta": handle_penta,
        "quadra": handle_quadra,
        "cannon": handle_cannon,
        "latege": handle_latege,
        "joke": handle_joke,
        "t": handle_translate,
        "spam": handle_spam,
        "youtube": handle_youtube,
        "coin": handle_coin,
    }
    return handlers.get(command)


# Individual command handlers

async def handle_bye(message, args: str) -> None:
    """Handle the bye command."""
    await message.channel.send(
        Messages.USER_GOODBYE.format(mention=message.author.mention)
    )


async def handle_brb(message, args: str) -> None:
    """Handle the brb command."""
    await message.channel.send(
        Messages.USER_BRB.format(mention=message.author.mention)
    )


async def handle_returned(message, args: str) -> None:
    """Handle the returned command."""
    await message.channel.send(
        Messages.USER_RETURNED.format(mention=message.author.mention)
    )


async def handle_lurk(message, args: str) -> None:
    """Handle the lurk command."""
    await message.channel.send(
        Messages.USER_LURKING.format(mention=message.author.mention)
    )


async def handle_penta(message, args: str) -> None:
    """Handle the penta command."""
    count = command_counters.increment('penta')
    await message.channel.send(Messages.PENTA_KILL.format(count=count))


async def handle_quadra(message, args: str) -> None:
    """Handle the quadra command."""
    count = command_counters.increment('quadra')
    await message.channel.send(Messages.QUADRA_KILL.format(count=count))


async def handle_cannon(message, args: str) -> None:
    """Handle the cannon command."""
    count = command_counters.increment('cannon')
    await message.channel.send(Messages.CANNON_COUNT.format(count=count))


async def handle_latege(message, args: str) -> None:
    """Handle the latege command - check if stream is late."""
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
            await message.channel.send(
                f"The stream is currently {minutes_late} minutes late! "
                f"Peks probably lost track of time again latege"
            )
        else:  # Stream is early or on time
            delta = scheduled_time - now
            minutes_early = delta.seconds // 60
            await message.channel.send(
                f"Wow! The stream is actually {minutes_early} minutes early today! "
                f"A new record? PogChamp"
            )
    else:
        # Check for next scheduled stream
        next_stream_info = find_next_stream(now)
        if next_stream_info:
            next_day, next_time = next_stream_info
            await message.channel.send(
                f"No stream scheduled for today. Next stream is on {next_day} at {next_time}!"
            )
        else:
            await message.channel.send("No scheduled streams found for the upcoming week.")


def find_next_stream(current_time: datetime.datetime) -> Optional[Tuple[str, str]]:
    """Find the next scheduled stream."""
    for days_ahead in range(1, 8):
        future_date = current_time + datetime.timedelta(days=days_ahead)
        future_day = future_date.strftime("%A").lower()
        future_stream = STREAM_SCHEDULE.get(future_day)
        if future_stream:
            return future_date.strftime("%A"), future_stream
    return None


async def handle_joke(message, args: str) -> None:
    """Handle the joke command."""
    if random.randint(0, 1) == 0:
        await message.channel.send(Messages.JOKE_NOT_BRINGING_BACK)
    else:
        try:
            joke_response = requests.get(
                "https://icanhazdadjoke.com",
                headers={"Accept": "application/json"},
                timeout=5
            )
            if joke_response.status_code == 200:
                joke_data = joke_response.json()
                await message.channel.send(joke_data["joke"])
            else:
                await message.channel.send(Messages.ERROR_JOKE_FETCH)
        except (requests.RequestException, KeyError):
            await message.channel.send(Messages.ERROR_JOKE_FETCH)


async def handle_translate(message, args: str) -> None:
    """Handle the translate command."""
    if not args:
        await message.channel.send(Messages.ERROR_TRANSLATION)
        return

    translated_text, source_lang = translate_text_to_english(args)
    if translated_text and source_lang:
        await message.channel.send(
            f"Translation Result: {translated_text} (Translated from {source_lang})"
        )
    else:
        await message.channel.send(Messages.ERROR_TRANSLATION)


async def handle_spam(message, args: str) -> None:
    """Handle the spam command."""
    if not args:
        return

    # Ensure the message is under 250 characters to avoid cutting it short
    spam_message = args[:250]
    if len(args) > 250:
        spam_message = args[:247] + "..."

    # Repeat the message as many times as possible without exceeding 500 characters
    repeated_message = spam_message
    while len(repeated_message + " " + spam_message) <= Numbers.MAX_SPAM_MESSAGE_LENGTH:
        repeated_message += " " + spam_message

    await message.channel.send(repeated_message)


async def handle_youtube(message, args: str) -> None:
    """Handle the youtube command."""
    await message.channel.send(
        "Watch Peks' latest video dealdough here: https://www.youtube.com/watch?v=vE0iNgwDl8E"
    )


async def handle_coin(message, args: str) -> None:
    """Handle the coin flip command."""
    result = "Heads" if random.randint(0, 1) == 0 else "Tails"
    await message.channel.send(Messages.COIN_FLIP.format(result=result))
