# utils.py
# Utility functions for MurphyAI Twitch Chat Bot


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

    parts = message_content[len(prefix):].split()
    command = parts[0] if parts else None
    args = parts[1:] if len(parts) > 1 else []

    return command, args


# Add any additional utility functions below
