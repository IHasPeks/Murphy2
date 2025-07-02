"""
Type definitions and aliases for the MurphyAI Twitch bot.
Provides better type safety and code documentation.
"""
from typing import Dict, List, Optional, Union, Callable, Any, TypeVar, Protocol
import asyncio

# Type variables
T = TypeVar('T')

# Basic type aliases
UserId = str
ChannelName = str
CommandName = str
MessageContent = str
Timestamp = float

# Complex type aliases
CommandHandler = Callable[[Any, str], asyncio.Task]
ConversationHistory = List[Dict[str, str]]
CacheEntry = Dict[str, Union[str, float]]
CommandData = Dict[str, Union[str, List[str], float, int]]

# Protocol definitions for duck typing
class TwitchMessage(Protocol):
    """Protocol for Twitch message objects."""
    content: Optional[str]
    author: 'TwitchUser'
    channel: 'TwitchChannel'

    async def reply(self, content: str) -> None: ...

class TwitchUser(Protocol):
    """Protocol for Twitch user objects."""
    name: str
    mention: str
    is_mod: bool

    def __str__(self) -> str: ...

class TwitchChannel(Protocol):
    """Protocol for Twitch channel objects."""
    name: str

    async def send(self, content: str) -> None: ...

class BotProtocol(Protocol):
    """Protocol for the main bot instance."""
    nick: str
    loop: asyncio.AbstractEventLoop
    connected_channels: List[str]

    def get_channel(self, name: str) -> Optional[TwitchChannel]: ...
    def is_ready(self) -> bool: ...

# Response types
class CommandResponse:
    """Structured response from command execution."""
    def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data or {}

class ValidationResult:
    """Result from validation operations."""
    def __init__(self, is_valid: bool, error: Optional[str] = None):
        self.is_valid = is_valid
        self.error = error

# Configuration types
ConfigValue = Union[str, int, float, bool, List[str], Dict[str, Any]]
ConfigDict = Dict[str, ConfigValue]

# State types
BotState = Dict[str, Union[List[str], int, Dict[str, Any]]]

# Error types
class BotError(Exception):
    """Base exception for bot errors."""

class ConfigurationError(BotError):
    """Raised when there's a configuration issue."""

class CommandError(BotError):
    """Raised when a command fails to execute."""

class APIError(BotError):
    """Raised when an external API call fails."""
