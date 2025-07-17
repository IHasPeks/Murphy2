"""
Event handling for MurphyAI bot
Handles all bot events in a clean, organized manner
"""

import logging
import random
import traceback
from typing import TYPE_CHECKING

from constants import Messages
from config import TWITCH_PREFIX, MOD_PREFIX
from utils import suggest_alwase_variants, shazdm

if TYPE_CHECKING:
    from .bot import MurphyAI

logger = logging.getLogger(__name__)


class EventHandler:
    """Handles all bot events"""

    def __init__(self, bot: "MurphyAI"):
        self.bot = bot

    async def handle_ready(self) -> None:
        """Handle bot ready event"""
        logger.info(f"Logged in as | {self.bot.nick}")
        
        try:
            # Start scheduler
            from scheduler import start_scheduler
            await start_scheduler(self.bot)
            
            # Start queue cleanup
            self.bot.queue_manager.start_cleanup_task(self.bot.loop)
            
            # Start AI cache save task
            from ai_command import start_periodic_save
            start_periodic_save(self.bot.loop)
            
            # Start dynamic command watcher
            from dynamic_commands import DynamicCommandManager
            dynamic_command_manager = DynamicCommandManager()
            dynamic_command_manager.start_command_watcher(self.bot.loop)
            
            # Start cooldown cleanup
            from cooldown_manager import cooldown_manager
            await cooldown_manager.start_cleanup_task(self.bot.loop)
            
            # Send welcome message
            await self._send_welcome_message()
            
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def handle_message(self, message) -> None:
        """Handle incoming chat messages"""
        # Check if message has an author
        if not message.author:
            logger.warning("Received message without author")
            return

        # Ignore messages from the bot itself
        if message.author.name.lower() == self.bot.nick.lower():
            return

        # Update statistics
        self.bot.state_manager.increment_message_count()

        # Log the message
        logger.debug(f"[{message.channel.name}] {message.author.name}: {message.content}")

        # Check for new users
        is_new_user = self.bot.state_manager.add_known_user(message.author.name)
        
        if is_new_user:
            logger.info(f"New user detected: {message.author.name}")
            await self._handle_new_user(message)

        # Handle commands
        if message.content.startswith(TWITCH_PREFIX):
            await self._handle_prefix_command(message)
        elif message.content.startswith(MOD_PREFIX):
            await self._handle_mod_command(message)
        else:
            # Handle non-command messages
            await self._handle_regular_message(message)

    async def handle_error(self, error: Exception, data=None) -> None:
        """Handle errors raised by the Twitch API"""
        self.bot.state_manager.increment_error_count()
        
        error_msg = f"Error in Twitch API: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Handle critical connection errors
        if isinstance(error, (ConnectionError, TimeoutError)) or "connection" in str(error).lower():
            logger.warning("Connection-related error detected. Will attempt reconnection.")

    async def handle_connection_error(self, connection_error) -> None:
        """Handle connection errors with retry logic"""
        self.bot.state_manager.increment_error_count()
        
        logger.error(f"Connection error: {str(connection_error)}")
        logger.error(traceback.format_exc())
        
        # Update reconnection tracking
        import time
        current_time = time.time()
        
        if current_time - self.bot.state_manager.last_reconnect_time < 60:
            self.bot.state_manager.reconnect_attempts += 1
        else:
            self.bot.state_manager.reconnect_attempts = 1
            
        self.bot.state_manager.last_reconnect_time = current_time
        
        # If too many rapid reconnections, restart bot
        if self.bot.state_manager.reconnect_attempts >= 3:
            logger.warning(f"Too many reconnection attempts ({self.bot.state_manager.reconnect_attempts}). Restarting bot...")
            await self.bot.restart_bot()
        else:
            logger.info(f"Attempting to reconnect... (attempt {self.bot.state_manager.reconnect_attempts})")

    async def handle_disconnect(self) -> None:
        """Handle disconnection events"""
        logger.warning("Bot disconnected from Twitch")

    async def handle_reconnect(self) -> None:
        """Handle reconnection events"""
        logger.info("Bot reconnected to Twitch")
        self.bot.state_manager.reconnect_attempts = 0

    async def _send_welcome_message(self) -> None:
        """Send welcome message to all channels"""
        welcome_message = Messages.BOT_INITIALIZED
        
        for channel in self.bot.initial_channels:
            try:
                channel_obj = self.bot.get_channel(channel)
                if channel_obj:
                    await channel_obj.send(welcome_message)
                else:
                    logger.warning(f"Failed to get channel {channel}")
            except Exception as e:
                logger.error(f"Failed to send message to channel {channel}: {str(e)}")

    async def _handle_new_user(self, message) -> None:
        """Handle new user welcome with AI response"""
        # Only respond to first-time chatters with a 25% chance
        if (not message.content.startswith(TWITCH_PREFIX) and 
            not message.content.startswith(MOD_PREFIX) and 
            random.random() < 0.25):
            
            try:
                welcome_prompt = (
                    f"User {message.author.name} has joined the chat for the first time "
                    f"and said: '{message.content}'. Give them a warm welcome."
                )
                
                from ai_command import handle_ai_command
                await handle_ai_command(self.bot, message, custom_prompt=welcome_prompt)
                logger.info(f"Sent AI welcome to first-time chatter: {message.author.name}")
                
            except Exception as e:
                logger.error(f"Error sending AI welcome: {e}")

    async def _handle_prefix_command(self, message) -> None:
        """Handle commands with the bot prefix"""
        self.bot.state_manager.increment_command_count()
        
        # Extract command name
        command_name = message.content[len(TWITCH_PREFIX):].split(" ")[0].lower()
        
        # Check if it's a built-in TwitchIO command
        if command_name in [cmd.name for cmd in self.bot.commands.values()]:
            return  # Let TwitchIO handle it
        
        try:
            if command_name.startswith("ai"):
                # Handle AI command
                from ai_command import handle_ai_command
                await handle_ai_command(self.bot, message)
            else:
                # Handle other commands
                from commands import handle_command
                await handle_command(self.bot, message)
                
        except Exception as e:
            self.bot.state_manager.increment_error_count()
            logger.error(f"Error processing command '{message.content}': {e}")
            logger.error(traceback.format_exc())
            await message.channel.send("Error processing command. Please try again later.")

    async def _handle_mod_command(self, message) -> None:
        """Handle moderator commands"""
        # Check permissions
        if not (message.author.is_mod or message.author.name.lower() == message.channel.name.lower()):
            await message.channel.send(Messages.PERMISSION_DENIED_MOD)
            return
        
        self.bot.state_manager.increment_command_count()
        # Built-in mod commands are handled by TwitchIO decorators

    async def _handle_regular_message(self, message) -> None:
        """Handle non-command messages"""
        await self.suggest_variants(message)

    async def suggest_variants(self, message) -> None:
        """Suggest variants for common misspellings"""
        for suggest_func in [suggest_alwase_variants, shazdm]:
            try:
                suggestions = suggest_func(message.content)
                if suggestions:
                    await message.channel.send(random.choice(suggestions))
                    break  # Only send one suggestion
            except Exception as e:
                logger.error(f"Error in suggest_variants with {suggest_func.__name__}: {str(e)}") 