"""
Cooldown management for Twitch chat bot commands.
Prevents spam and rate limits command usage.
"""
import time
import logging
from typing import Dict, Optional, Tuple
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CooldownManager:
    """Manages cooldowns for commands to prevent spam."""

    def __init__(self):
        # Store last usage times: {command: {user: last_used_timestamp}}
        self.cooldowns: Dict[str, Dict[str, float]] = {}
        # Import constants
        from constants import Numbers

        # Default cooldown times in seconds for different command types
        self.default_cooldowns = {
            'ai': Numbers.COOLDOWN_AI,
            'spam': Numbers.COOLDOWN_SPAM,
            'joke': Numbers.COOLDOWN_JOKE,
            'default': Numbers.COOLDOWN_DEFAULT,
            'mod': Numbers.COOLDOWN_MOD,
        }
        # Global cooldowns (affects all users)
        self.global_cooldowns: Dict[str, float] = {}
        self.global_cooldown_times = {
            'joke': Numbers.COOLDOWN_GLOBAL_JOKE,
        }

    def is_on_cooldown(self, command: str, user: str, is_mod: bool = False) -> Tuple[bool, Optional[int]]:
        """
        Check if a command is on cooldown for a user.

        Returns:
            Tuple of (is_on_cooldown, remaining_seconds)
        """
        current_time = time.time()

        # Check global cooldown first
        if command in self.global_cooldown_times:
            if command in self.global_cooldowns:
                global_remaining = self.global_cooldown_times[command] - (current_time - self.global_cooldowns[command])
                if global_remaining > 0:
                    return True, int(global_remaining)

        # Mods have reduced cooldowns
        cooldown_multiplier = 0.5 if is_mod else 1.0

        # Get cooldown time for this command
        cooldown_time = self.default_cooldowns.get(command, self.default_cooldowns['default'])
        cooldown_time *= cooldown_multiplier

        # Check user-specific cooldown
        if command in self.cooldowns and user in self.cooldowns[command]:
            time_passed = current_time - self.cooldowns[command][user]
            if time_passed < cooldown_time:
                remaining = int(cooldown_time - time_passed)
                return True, remaining

        return False, None

    def set_cooldown(self, command: str, user: str):
        """Set a cooldown for a command and user."""
        current_time = time.time()

        # Set user cooldown
        if command not in self.cooldowns:
            self.cooldowns[command] = {}
        self.cooldowns[command][user] = current_time

        # Set global cooldown if applicable
        if command in self.global_cooldown_times:
            self.global_cooldowns[command] = current_time

    def clear_old_cooldowns(self):
        """Remove expired cooldowns to prevent memory bloat."""
        current_time = time.time()
        max_cooldown = max(self.default_cooldowns.values())

        for command in list(self.cooldowns.keys()):
            for user in list(self.cooldowns[command].keys()):
                if current_time - self.cooldowns[command][user] > max_cooldown * 2:
                    del self.cooldowns[command][user]

            # Remove command entry if no users remain
            if not self.cooldowns[command]:
                del self.cooldowns[command]

    async def start_cleanup_task(self, loop):
        """Start a background task to clean up old cooldowns."""
        while True:
            await asyncio.sleep(300)  # Clean up every 5 minutes
            self.clear_old_cooldowns()
            logger.debug(f"Cleaned up cooldowns. Active commands: {len(self.cooldowns)}")


# Global instance
cooldown_manager = CooldownManager()


def check_cooldown(command_name: Optional[str] = None):
    """
    Decorator to check cooldowns for commands.
    Can be used with or without specifying a command name.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            # Determine command name
            cmd_name = command_name or func.__name__.replace('_command', '').replace('_', '')

            # Check if user is mod
            is_mod = ctx.author.is_mod or ctx.author.name.lower() == ctx.channel.name.lower()

            # Check cooldown
            on_cooldown, remaining = cooldown_manager.is_on_cooldown(
                cmd_name,
                ctx.author.name,
                is_mod
            )

            if on_cooldown:
                await ctx.send(
                    f"@{ctx.author.name} Command on cooldown! "
                    f"Please wait {remaining} seconds before using this command again."
                )
                return

            # Set cooldown before executing command
            cooldown_manager.set_cooldown(cmd_name, ctx.author.name)

            # Execute the command
            return await func(ctx, *args, **kwargs)

        return wrapper
    return decorator
