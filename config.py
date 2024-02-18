# config.py
# Configuration file for MurphyAI Twitch Chat Bot

# Twitch Bot Credentials
BOT_NICK = "MurphyAI"  # Bot's Twitch username
BOT_TOKEN = "oauth:your_bot_token_here"  # Bot's OAuth token, get from https://twitchapps.com/tmi/
CHANNEL = "your_channel_name_here"  # Channel name where the bot will operate

# AI Configuration
OPENAI_API_KEY = (
    "your_openai_api_key_here"  # API Key for OpenAI, used for the AI command
)

# Scheduler Configuration
MESSAGE_INTERVAL_HOURS = 2  # Interval in hours for sending passive messages

# Queue System Messages
QUEUE_JOIN_MESSAGE = "You have successfully joined the queue!"
QUEUE_LEAVE_MESSAGE = "You have left the queue."
QUEUE_NOT_AVAILABLE_MESSAGE = "You are now marked as not available."
QUEUE_AVAILABLE_MESSAGE = "You are now available in the queue."
QUEUE_EMPTY_MESSAGE = "The queue is currently empty."
QUEUE_STATUS_MESSAGE = (
    "Current queue: {queue_list}"  # {queue_list} will be replaced dynamically
)

# General Bot Settings
COMMAND_PREFIX = "?"  # Prefix used for commands

# Add any additional configuration variables below
