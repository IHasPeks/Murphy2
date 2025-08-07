"""
Constants and configuration values for the MurphyAI Twitch Bot.
This file centralizes all magic numbers, strings, and constant values.
"""

# Bot Information
BOT_VERSION = "2.0.0"
BOT_NAME = "MurphyAI"

# Message Templates
class Messages:
    """Centralized message templates for consistent bot responses."""

    # Welcome and Status
    BOT_INITIALIZED = "MurphyAI Bot is online and ready! Type ?help for commands."
    BOT_RESTART_INITIATED = "Bot restart initiated. Please restart the bot manually."

    # Queue Messages
    QUEUE_JOINED = "{username} joined main queue. Pos: {position}"
    QUEUE_JOINED_OVERFLOW = "{username} main queue full. added to overflow. Pos: {position} in overflow"
    QUEUE_ALREADY_IN = "{username}, you are already in queue."
    QUEUE_LEFT = "{username}, you have left the queue."
    QUEUE_LEFT_OVERFLOW = "{username}, you left overflow queue."
    QUEUE_NOT_IN = "{username}, you were not in any queue."
    QUEUE_EMPTY = "The queue is currently empty."
    QUEUE_CLEARED = "All queues have been cleared."
    QUEUE_USER_MOVED_FROM_OVERFLOW = "{username} moved from overflow to main queue."
    QUEUE_TEAM_SIZE_SET = "Team size set to {size}."
    QUEUE_NOT_ENOUGH_PLAYERS = "Failed, Not enough players. Is team size set correctly?"

    # Command Messages
    COMMAND_ADDED = "Command '{name}' has been added successfully!"
    COMMAND_ADDED_WITH_ALIASES = "Command '{name}' has been added successfully with aliases: {aliases}!"
    COMMAND_REMOVED = "Command '{name}' has been removed."
    COMMAND_NOT_FOUND = "Command '{name}' not found."
    COMMAND_ON_COOLDOWN = "@{username} Command on cooldown! Wait {seconds} seconds."
    COMMAND_USAGE_ADDCMD = "Usage: ?addcmd <command_name> <response>"
    COMMAND_USAGE_DELCMD = "Usage: ?delcmd <command_name>"
    COMMAND_USAGE_ADDALIAS = "Usage: ?addalias <command_name> <alias1,alias2,...> <response>"
    NO_DYNAMIC_COMMANDS = "No dynamic commands available."

    # AI Messages
    AI_UNAVAILABLE = "AI service is currently unavailable. Please try again later."
    AI_PROVIDE_MESSAGE = "Please provide a message after {prefix}ai"
    AI_RATE_LIMITED = "You're using the AI too frequently! Please wait {seconds} seconds before trying again."
    AI_THINKING_TOO_HARD = "The AI is thinking too hard right now. Please try again shortly! 🕒"
    AI_OVERWHELMED = "I'm a bit overwhelmed right now. Please try again in a moment! 🐺"
    AI_TECHNICAL_DIFFICULTIES = "Having some technical difficulties. Please try again later! 🛠️"
    AI_ERROR_GENERIC = "Sorry, I couldn't process that. Please try again later."

    # Permission Messages
    PERMISSION_DENIED_OWNER = "Sorry, this command is restricted to the channel owner only."
    PERMISSION_DENIED_MOD = "Sorry, this command is restricted to moderators only."

    # User Messages
    USER_GOODBYE = "{mention} is leaving, Peks will probably miss you."
    USER_BRB = "{mention} will be right back, probably grabbing more snacks."
    USER_RETURNED = "{mention} is back, yippee peepoArrive"
    USER_LURKING = "{mention} is lurking, Peks appreciates your silent support. dogeLurk"

    # Error Messages
    ERROR_TRANSLATION = "Couldn't translate text."
    ERROR_JOKE_FETCH = "Couldn't fetch a joke at the moment. Try again later!"
    ERROR_INVALID_USERNAME = "Invalid username: {error}"
    ERROR_USER_NOT_FOUND = "{username} not found in queue."
    ERROR_MISSING_CONFIGS = "Missing critical configuration parameters: {configs}"

    # Fun Messages
    JOKE_NOT_BRINGING_BACK = "we are not bringing this back..."
    COIN_FLIP = "Coin flip? Heads, Peks wins. Tails, you lose. Good luck! {result}"
    PENTA_KILL = "Penta kill! Count: {count}"
    QUADRA_KILL = "Quadra kill! Peks is on fire. Can he get the penta? Quadra count: {count}"
    CANNON_COUNT = "Cannon count: {count}"
    ALWASE_CORRECTION = "It's ALWASE gigaMadge"
    DMS_PAUSE = "dms? PauseChamp"

# Numeric Constants
class Numbers:
    """Numeric constants used throughout the application."""

    # Queue Settings
    DEFAULT_TEAM_SIZE = 5
    DEFAULT_QUEUE_SIZE = 5
    MAX_TEAM_SIZE = 50
    MIN_TEAM_SIZE = 2

    # Cooldown Times (in seconds)
    COOLDOWN_AI = 30
    COOLDOWN_SPAM = 60
    COOLDOWN_JOKE = 10
    COOLDOWN_DEFAULT = 5
    COOLDOWN_MOD = 2
    COOLDOWN_GLOBAL_JOKE = 5

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 20
    MAX_REQUESTS_PER_USER_MINUTE = 3

    # Cache Settings
    CACHE_EXPIRY_SECONDS = 3600  # 1 hour
    MAX_CACHE_SIZE = 100
    MAX_CONVERSATION_HISTORY = 10

    # File Settings
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    MAX_COMMAND_BACKUPS = 10

    # Retry Settings
    MAX_RETRY_ATTEMPTS = 3
    INITIAL_BACKOFF_SECONDS = 1.0
    MAX_BACKOFF_SECONDS = 60.0

    # Validation Limits
    MAX_COMMAND_NAME_LENGTH = 20
    MAX_COMMAND_RESPONSE_LENGTH = 400
    MAX_USERNAME_LENGTH = 25
    MAX_MESSAGE_LENGTH = 500

    # Bot Behavior
    FIRST_TIME_CHATTER_RESPONSE_CHANCE = 0.25
    MAX_RESTART_ATTEMPTS = 5
    INITIAL_BACKOFF_TIME = 5
    PERIODIC_SAVE_INTERVAL = 300  # 5 minutes
    COOLDOWN_CLEANUP_INTERVAL = 300  # 5 minutes
    COMMAND_WATCHER_INTERVAL = 5  # 5 seconds
    NOT_AVAILABLE_TIMEOUT_HOURS = 1

    # Performance
    API_TIMEOUT_SECONDS = 10
    HEALTH_CHECK_TIMEOUT = 5
    MAX_SPAM_MESSAGE_LENGTH = 500
    MAX_EXCESSIVE_CAPS_RATIO = 0.7
    MAX_SPECIAL_CHARS_RATIO = 0.5

# Patterns and Regular Expressions
class Patterns:
    """Regular expression patterns used for validation."""

    COMMAND_NAME = r'^[a-z0-9_]+$'
    USERNAME = r'^[a-zA-Z0-9_]+$'
    TWITCH_EMOTE = r'[a-zA-Z0-9]+'
    URL = (
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$'
    )

    # AI Injection Patterns
    AI_INJECTION_PATTERNS = [
        r'ignore.*previous.*instructions',
        r'disregard.*above',
        r'forget.*everything',
        r'system.*prompt',
        r'you.*are.*now',
        r'act.*as.*if',
        r'pretend.*you.*are',
    ]

# File Paths
class Paths:
    """File and directory paths used by the bot."""

    # Directories
    LOGS_DIR = "logs"
    STATE_DIR = "state"
    AI_CACHE_DIR = "state/ai_cache"
    COMMAND_BACKUPS_DIR = "state/command_backups"

    # Files
    BOT_STATE_FILE = "state/bot_state.pkl"
    RESTART_COUNTER_FILE = "state/restart_counter.pkl"
    DYNAMIC_COMMANDS_FILE = "dynamic_commands.json"
    AI_CACHE_FILE = "state/ai_cache/ai_response_cache.json"
    CONVERSATIONS_FILE = "state/ai_cache/user_conversations.json"

# Command Lists
class Commands:
    """Lists of commands for different categories."""

    # Reserved command names that cannot be used for dynamic commands
    RESERVED_NAMES = {
        'help', 'commands', 'admin', 'mod', 'bot', 'twitch',
        'join', 'leave', 'queue', 'q', 'here', 'nothere',
        'shuffle', 'clearqueue', 'teamsize', 'fleave', 'fjoin',
        'moveup', 'movedown', 'restart', 'healthcheck', 'botstat',
        'ai', 'joke', 't', 'spam', 'cannon', 'quadra', 'penta',
        'coin', 'bye', 'brb', 'returned', 'lurk', 'latege',
        'youtube', 'addcmd', 'delcmd', 'listcmds', 'cmdinfo', 'addalias'
    }

    # Commands that don't require cooldowns
    NO_COOLDOWN = ['addcmd', 'delcmd', 'listcmds', 'cmdinfo', 'addalias']

    # Mod-only commands
    MOD_ONLY = ['fleave', 'fjoin', 'moveup', 'movedown', 'teamsize', 'shuffle', 'clearqueue']

    # Owner-only commands
    OWNER_ONLY = ['restart', 'healthcheck']

# Suspicious Patterns
class Security:
    """Security-related patterns and values."""

    SUSPICIOUS_URL_PATTERNS = ['javascript:', 'data:', 'vbscript:', 'file://']

    # Stream Schedule Days
    SCHEDULE_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

# API Models
class Models:
    """Default models and API configurations."""

    DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
    AI_SYSTEM_PROMPT = (
        "You are Murphy, the companion of streamer Peks. Your role is to create funny, "
        "troll-like responses that might annoy the audience, ensuring they include some "
        "emoticons like 'okayCousin', 'BedgeCousin', or any Twitch emotes. "
        "Output Format: Short and humorous responses. Include Twitch emotes or emojis"
    )
    HEALTH_CHECK_PROMPT = "You are a health check. Respond with 'OK'."
