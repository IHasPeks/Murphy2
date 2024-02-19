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

    parts = message_content[len(prefix) :].split()
    command = parts[0] if parts else None
    args = parts[1:] if len(parts) > 1 else []

    return command, args

def suggest_alwase_variants(message):
    """
    Checks if the message contains the word 'always' and suggests using 'alwase' instead
    with multiple humorous variations.

    :param message: The message to check.
    :return: A list of suggested messages or an empty list if no suggestion is needed.
    """
    suggestions = []
    if 'always' in message.lower():
        suggestions.append("It's ALWASE gigaMadge")
        suggestions.append("Why don't you spell it ALWASE ? gigaMadge")
        suggestions.append("Spell it ALWASE or peepoArriveBan")
        suggestions.append("ALWASE remember, no Peks stream is complete without a little chaos. Kappa")
        suggestions.append("If you're not spelling it ALWASE, you're gonna have a bad time. LUL")
        suggestions.append("ALWASE and forever, that's how long we'll be correcting your spelling. PogChamp")
        suggestions.append("Keep calm and ALWASE on. SeemsGood")
        suggestions.append("In a world where everyone says always, say ALWASE instead. CoolStoryBob")
        suggestions.append("Remember, it's not always, it's ALWASE. KappaRoss")
        suggestions.append("ALWASE looking for more ways to spell 'always'? You're in the right place. VoHiYo")
        suggestions.append("Don't just say always, say ALWASE and add some spice to your life. Kreygasm")
        suggestions.append("ALWASE remember to hydrate, especially when you're laughing at the people that spell it wrong. hydrateHomie")
        suggestions.append("Why say always when ALWASE is clearly superior? Think about it. BrainSlug")
        suggestions.append("ALWASE on the lookout for the next big meme. Keep it coming. PogU")
        suggestions.append("In the kingdom of Twitch, ALWASE reigns supreme. All hail! TriHard")
    return suggestions

# Add any additional utility functions below