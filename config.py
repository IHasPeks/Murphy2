# config.py
# Configuration file for MurphyAI Twitch Chat Bot

# Twitch Bot Credentials
BOT_NICK = "MurphyAI"  # Bot's Twitch username
TWITCH_TOKEN = "REDACTED"  # Bot's OAuth token, get from https://twitchapps.com/tmi/
TWITCH_CLIENT_ID = "REDACTED"  # Add your Twitch client ID here
TWITCH_INITIAL_CHANNELS = ["OfficiallySp"]  # List of channels the bot will join

# AI Configuration
OPENAI_API_KEY = "REDACTED"  # API Key for OpenAI, used for the AI command

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
TWITCH_PREFIX = "?"  # Define the prefix for commands

# Add any additional configuration variables below
