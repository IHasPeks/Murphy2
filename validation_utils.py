"""
Input validation and sanitization utilities for the Twitch bot.
"""
import re
import logging
from typing import Optional, List, Tuple
import html

logger = logging.getLogger(__name__)

from constants import Numbers, Patterns, Commands, Security
from type_definitions import ValidationResult

# Compile patterns
COMMAND_NAME_PATTERN = re.compile(Patterns.COMMAND_NAME)
USERNAME_PATTERN = re.compile(Patterns.USERNAME)
TWITCH_EMOTE_PATTERN = re.compile(Patterns.TWITCH_EMOTE)


def sanitize_input(text: str, max_length: int = Numbers.MAX_MESSAGE_LENGTH) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: The input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Truncate to max length
    text = text[:max_length]

    # Remove potential script tags
    text = re.sub(r"<\s*script[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/\s*script\s*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"alert\s*\(.*?\)", "", text, flags=re.IGNORECASE)

    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')

    # Remove multiple consecutive spaces
    text = re.sub(r'\s+', ' ', text)

    # Trim whitespace
    text = text.strip()

    return text


def validate_command_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a command name.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Command name cannot be empty"

    if len(name) > Numbers.MAX_COMMAND_NAME_LENGTH:
        return False, f"Command name too long (max {Numbers.MAX_COMMAND_NAME_LENGTH} characters)"

    if not COMMAND_NAME_PATTERN.match(name):
        return False, "Command name must contain only lowercase letters, numbers, and underscores"

    # Check for reserved command names
    if name in Commands.RESERVED_NAMES:
        return False, f"'{name}' is a reserved command name"

    return True, None


def validate_command_response(response: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a command response.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not response:
        return False, "Command response cannot be empty"

    if len(response) > Numbers.MAX_COMMAND_RESPONSE_LENGTH:
        return False, f"Command response too long (max {Numbers.MAX_COMMAND_RESPONSE_LENGTH} characters)"

    # Check for potential spam patterns
    if response.count(' ') > 100:
        return False, "Command response contains too many spaces"

    if len(set(response)) < 3:
        return False, "Command response is too repetitive"

    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a Twitch username.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"

    if len(username) > Numbers.MAX_USERNAME_LENGTH:
        return False, f"Username too long (max {Numbers.MAX_USERNAME_LENGTH} characters)"

    if not USERNAME_PATTERN.match(username):
        if ' ' in username:
            return False, "Username cannot contain spaces"
        return False, "Invalid username format"

    return True, None


def validate_team_size(size: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a team size value.

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        size_int = int(size)
    except ValueError:
        return False, "Team size must be a number"

    if size_int < Numbers.MIN_TEAM_SIZE:
        return False, f"Team size must be at least {Numbers.MIN_TEAM_SIZE}"

    if size_int > Numbers.MAX_TEAM_SIZE:
        return False, f"Team size cannot exceed {Numbers.MAX_TEAM_SIZE}"

    return True, None


def sanitize_ai_prompt(prompt: str) -> str:
    """
    Sanitize AI prompts to prevent prompt injection.

    Args:
        prompt: The AI prompt to sanitize

    Returns:
        Sanitized prompt
    """
    # Basic sanitization
    prompt = sanitize_input(prompt, Numbers.MAX_MESSAGE_LENGTH)

    # Remove potential command injections
    injection_patterns = [
        r'ignore.*previous.*instructions',
        r'disregard.*above',
        r'forget.*everything',
        r'system.*prompt',
        r'you.*are.*now',
        r'act.*as.*if',
        r'pretend.*you.*are',
    ]

    for pattern in injection_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            logger.warning(f"Potential prompt injection detected: {pattern}")
            prompt = re.sub(pattern, "[FILTERED]", prompt, flags=re.IGNORECASE)

    return prompt


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL to ensure it's safe.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not url_pattern.match(url):
        return False, "Invalid URL format"

    # Check for suspicious patterns
    suspicious_patterns = [
        'javascript:', 'data:', 'vbscript:', 'file://'
    ]

    for pattern in suspicious_patterns:
        if pattern in url.lower():
            return False, f"URL contains suspicious pattern: {pattern}"

    return True, None


def escape_twitch_formatting(text: str) -> str:
    """
    Escape special characters that might affect Twitch chat formatting.

    Args:
        text: The text to escape

    Returns:
        Escaped text
    """
    # Twitch doesn't support many formatting options, but we should handle @ mentions
    # Don't escape @ at the beginning (for mentions) but escape inline @
    if text.startswith('@'):
        return text[0] + text[1:].replace('@', '@ ')
    return text.replace('@', '@ ')


def validate_message_content(message: str, context: str = "general") -> Tuple[bool, Optional[str]]:
    """
    Validate message content based on context.

    Args:
        message: The message to validate
        context: The context of the message (e.g., "chat", "command", "ai")

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return False, "Message cannot be empty"

    if len(message) > Numbers.MAX_MESSAGE_LENGTH:
        return False, f"Message too long (max {Numbers.MAX_MESSAGE_LENGTH} characters)"

    # Check for spam patterns
    if message.count(message[0]) == len(message) and len(message) > 5:
        return False, "Message appears to be spam"

    # Check for excessive caps (more than 70% caps)
    if len(message) > 10:
        caps_count = sum(1 for c in message if c.isupper())
        if caps_count / len(message) > 0.7:
            return False, "Message contains too many capital letters"

    # Check for excessive special characters
    special_count = sum(1 for c in message if not c.isalnum() and not c.isspace())
    if special_count > len(message) * 0.5:
        return False, "Message contains too many special characters"

    return True, None
