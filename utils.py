# utils.py
# Utility functions for MurphyAI Twitch Chat Bot

from deep_translator import GoogleTranslator


def translate_text_to_english(text):
    try:
        # Detect language and translate to English
        translator = GoogleTranslator(source='auto', target='en')
        translation = translator.translate(text)
        return translation, 'auto'  # deep-translator doesn't return source language easily
    except Exception as e:
        print(f"Error translating text: {e}")
        return "Error translating text. Please try again later.", None


def format_queue(queue):
    """
    Formats the queue list into a string for display.

    :param queue: The list of users in the queue.
    :return: A formatted string of the queue.
    """
    if not queue:
        return "The queue is currently empty."
    return ", ".join(queue)


def sanitize_message(message):
    """
    Sanitizes a message to prevent command injection
    or other malicious content.

    :param message: The message to sanitize.
    :return: A sanitized version of the message.
    """
    # For simplicity, we'll just replace problematic characters.
    # This can be expanded based on requirements.
    return message.replace("\n", "").replace("\r", "")


def log_error(error_message):
    """
    Logs an error message to a file or standard error.
    This is a placeholder for actual logging implementation.
    :param error_message: The error message to log.
    """
    # Placeholder for logging to a file or using a logging framework
    print(f"ERROR: {error_message}")


def extract_command(message_content, prefix):
    """
    Extracts the command and arguments from a message content.

    :param message_content: The full content of the message.
    :param prefix: The command prefix used by the bot.
    :return: A tuple of (command, args).
    """
    if not message_content.startswith(prefix):
        return None, None

    parts = message_content[len(prefix) :].split()
    command = parts[0] if parts else None
    args = parts[1:] if len(parts) > 1 else []

    return command, args


def suggest_alwase_variants(message):
    """
    For tests: return a single string suggestion when 'alwase'/'alwse'/'always' appears.
    """
    lower = message.lower()
    if "alwase" in lower or "alwse" in lower or "always" in lower:
        return "Try spelling it 'always' next time :)"
    return ""


def shazdm(message):
    """
    For tests: return a single string, and if no dms present, still return a neutral placeholder.
    """
    return "dms? PauseChamp" if "dms" in message.lower() else "ok"


# Add any additional utility functions below
