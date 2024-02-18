# config.py
# Configuration file for MurphyAI Twitch Chat Bot

# Twitch Bot Credentials
BOT_NICK = "MurphyAI"  # Bot's Twitch username
TWITCH_TOKEN = "oauth:vrqm74lwywtc7i0yuefw0039jtvktm"  # Bot's OAuth token, get from https://twitchapps.com/tmi/
TWITCH_CLIENT_ID = "bhr9s5c1j8rfn0lyvb4qszrscecism"  # Add your Twitch client ID here
TWITCH_PREFIX = "?"  # Define the prefix for commands
TWITCH_INITIAL_CHANNELS = ["IHasPeks"]  # List of channels the bot will join

# AI Configuration
OPENAI_API_KEY = (
    "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"  # API Key for OpenAI, used for the AI command
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
