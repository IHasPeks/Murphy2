"""
AI command handling module for the MurphyAI Twitch Bot.

This module handles AI chat interactions, conversation history,
rate limiting, and response caching.
"""

import asyncio
import json
import logging
import os
import time

import openai
from openai import OpenAI

from config import OPENAI_API_KEY, TWITCH_PREFIX
from constants import Numbers, Paths, Models

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized")
except Exception as e:
    logger.error("Failed to initialize OpenAI client: %s", e)
    client = None

# Store conversation history for each user
user_conversations = {}

# Rate limiting configuration
request_timestamps = []
user_request_timestamps = {}  # Keep track of per-user timestamps

# Cache for recent AI responses
response_cache = {}

# Create cache directory if it doesn't exist
os.makedirs(Paths.AI_CACHE_DIR, exist_ok=True)


def load_cache():
    """Load cached responses from disk"""
    global response_cache
    try:
        if os.path.exists(Paths.AI_CACHE_FILE):
            with open(Paths.AI_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Filter out expired entries
                current_time = time.time()
                response_cache = {
                    k: v for k, v in data.items()
                    if v.get('timestamp', 0) + Numbers.CACHE_EXPIRY_SECONDS > current_time
                }
            logger.info("Loaded %d AI response cache entries from disk", len(response_cache))
    except Exception as e:
        logger.error("Failed to load AI response cache: %s", e)
        response_cache = {}


def save_cache():
    """Save cached responses to disk"""
    try:
        with open(Paths.AI_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(response_cache, f)
        logger.info("Saved %d AI response cache entries to disk", len(response_cache))
    except Exception as e:
        logger.error("Failed to save AI response cache: %s", e)


def load_conversations():
    """Load user conversations from disk"""
    global user_conversations
    try:
        if os.path.exists(Paths.CONVERSATIONS_FILE):
            with open(Paths.CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
                user_conversations = json.load(f)
            logger.info("Loaded conversations for %d users from disk", len(user_conversations))
    except Exception as e:
        logger.error("Failed to load user conversations: %s", e)
        user_conversations = {}


def save_conversations():
    """Save user conversations to disk"""
    try:
        with open(Paths.CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_conversations, f)
        logger.info("Saved conversations for %d users to disk", len(user_conversations))
    except Exception as e:
        logger.error("Failed to save user conversations: %s", e)


# Load cached data at module initialization
load_cache()
load_conversations()


# Set up periodic cache saving
async def periodic_cache_save():
    """Periodically save cache and conversations to disk"""
    while True:
        await asyncio.sleep(Numbers.PERIODIC_SAVE_INTERVAL)
        save_cache()
        save_conversations()


def start_periodic_save(loop):
    """Start the periodic save task"""
    loop.create_task(periodic_cache_save())


def add_to_cache(user_id, prompt, response):
    """Add a response to the cache"""
    # Generate a cache key from the user ID and prompt
    cache_key = f"{user_id}:{prompt}"

    # Add to cache with current timestamp
    response_cache[cache_key] = {
        'response': response,
        'timestamp': time.time()
    }

    # Trim cache if it's too large
    if len(response_cache) > Numbers.MAX_CACHE_SIZE:
        # Remove oldest entries
        oldest_keys = sorted(response_cache.items(),
                             key=lambda x: x[1]['timestamp'])[:len(response_cache) - Numbers.MAX_CACHE_SIZE]
        for key, _ in oldest_keys:
            del response_cache[key]


def get_from_cache(user_id, prompt):
    """Get a response from the cache if it exists and is not expired"""
    cache_key = f"{user_id}:{prompt}"

    if cache_key in response_cache:
        entry = response_cache[cache_key]
        # Check if the entry is still valid
        if entry['timestamp'] + Numbers.CACHE_EXPIRY_SECONDS > time.time():
            logger.info("Cache hit for user %s", user_id)
            return entry['response']
        # Remove expired entry
        del response_cache[cache_key]

    return None


def check_rate_limit(user_id=None):
    """
    Check if we've exceeded our rate limit
    Args:
        user_id: Optional user ID to check user-specific rate limit

    Returns True if we can proceed, False if we're rate limited
    """
    current_time = time.time()

    # Check global rate limit
    # Remove timestamps older than 60 seconds
    global request_timestamps
    request_timestamps = [t for t in request_timestamps if current_time - t < 60]

    # Check if we've exceeded our global limit
    if len(request_timestamps) >= Numbers.MAX_REQUESTS_PER_MINUTE:
        logger.warning("Global rate limit exceeded: %d requests in the last minute",
                       len(request_timestamps))
        return False

    # Check user-specific rate limit if user_id is provided
    if user_id:
        if user_id not in user_request_timestamps:
            user_request_timestamps[user_id] = []

        # Remove timestamps older than 60 seconds
        user_request_timestamps[user_id] = [
            t for t in user_request_timestamps[user_id] if current_time - t < 60
        ]

        # Check if user has exceeded their limit
        user_limit = Numbers.MAX_REQUESTS_PER_USER_MINUTE
        if len(user_request_timestamps[user_id]) >= user_limit:
            logger.warning("User rate limit exceeded for %s: %d requests in the last minute",
                           user_id, len(user_request_timestamps[user_id]))
            return False

        # Add current timestamp to user's timestamps
        user_request_timestamps[user_id].append(current_time)

    # Add current timestamp to global timestamps and proceed
    request_timestamps.append(current_time)
    return True


async def check_ai_health():
    """
    Perform a simple health check on the AI service
    Returns a status string indicating the health of the AI service
    """
    try:
        if client is None:
            return "UNAVAILABLE (Client not initialized)"

        # Make a simple, minimal API call to test connectivity
        model_name = os.getenv("OPENAI_MODEL", Models.DEFAULT_OPENAI_MODEL)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": Models.HEALTH_CHECK_PROMPT},
                {"role": "user", "content": "Status?"}
            ],
            max_tokens=5,
            temperature=0,
            timeout=Numbers.HEALTH_CHECK_TIMEOUT
        )

        # Check the response
        if response and response.choices and response.choices[0].message:
            return "OK"
        return "DEGRADED (Unexpected response format)"

    except openai.RateLimitError:
        return "RATE LIMITED"
    except openai.APIError as e:
        return f"API ERROR ({str(e)[:30]}...)"
    except Exception as e:
        return f"ERROR ({str(e)[:30]}...)"


async def handle_ai_command(bot, message, custom_prompt=None):
    """
    Handle AI command requests from users.
    
    Args:
        bot: The bot instance
        message: The message object containing user input
        custom_prompt: Optional custom prompt to use instead of parsing from message
    """
    try:
        # Import cooldown manager
        from cooldown_manager import cooldown_manager

        # Check cooldown for AI command (only for non-custom prompts)
        if not custom_prompt:
            is_mod = message.author.is_mod or message.author.name.lower() == message.channel.name.lower()
            on_cooldown, remaining = cooldown_manager.is_on_cooldown('ai', message.author.name, is_mod)
            if on_cooldown:
                await message.channel.send(
                    f"@{message.author.name} AI command on cooldown! "
                    f"Please wait {remaining} seconds."
                )
                return

        # Check if OpenAI client was initialized properly
        if client is None:
            await message.channel.send("AI service is currently unavailable. Please try again later.")
            logger.error("AI command attempted but OpenAI client is not initialized")
            return

        # Get user's ID
        user_id = message.author.name

        # Get the prompt - either custom or from message
        if custom_prompt:
            prompt = custom_prompt
        else:
            # Ensure we have the correct command format
            if not message.content.startswith(f"{TWITCH_PREFIX}ai "):
                await message.channel.send(f"To use the AI command, type {TWITCH_PREFIX}ai followed by your message")
                return

            prompt = message.content[len(f"{TWITCH_PREFIX}ai ") :].strip()

        # Check if prompt is empty
        if not prompt:
            await message.channel.send(f"Please provide a message after {TWITCH_PREFIX}ai")
            return

        # Sanitize the prompt to prevent injection attacks
        from validation_utils import sanitize_ai_prompt
        prompt = sanitize_ai_prompt(prompt)

        logger.info("Processing AI command from %s: %s",
                    user_id, prompt[:50] + ('...' if len(prompt) > 50 else ''))

        # Check rate limiting for this user
        if not check_rate_limit(user_id):
            user_timestamps = user_request_timestamps.get(user_id, [time.time() - 61])
            remaining_time = 60 - max(time.time() - t for t in user_timestamps)
            await message.channel.send(f"You're using the AI too frequently! "
                                       f"Please wait {int(remaining_time)} seconds before trying again.")
            return

        # Check if we have a cached response
        cached_response = get_from_cache(user_id, prompt)
        if cached_response:
            await message.channel.send(cached_response)
            logger.info("Sent cached AI response to %s", user_id)
            return

        # Get user's conversation history or create new one
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # Add user's message to history
        user_conversations[user_id].append({"role": "user", "content": prompt})

        # Keep only last 10 messages to avoid token limits
        if len(user_conversations[user_id]) > Numbers.MAX_CONVERSATION_HISTORY:
            user_conversations[user_id] = user_conversations[user_id][-Numbers.MAX_CONVERSATION_HISTORY:]

        # Create messages array with system prompt and history
        messages = [
            {
                "role": "system",
                "content": Models.AI_SYSTEM_PROMPT,
            },
            *user_conversations[user_id],
        ]

        # Make API call with timeout protection and retries
        max_retries = Numbers.MAX_RETRY_ATTEMPTS - 1
        # Get model from environment or use default
        model_name = os.getenv("OPENAI_MODEL", Models.DEFAULT_OPENAI_MODEL)

        for retry in range(max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7,
                    timeout=Numbers.API_TIMEOUT_SECONDS
                )

                reply = response.choices[0].message.content

                # Add assistant's reply to history
                user_conversations[user_id].append({"role": "assistant", "content": reply})

                # Add to cache
                add_to_cache(user_id, prompt, reply)

                await message.channel.send(reply)
                logger.info("AI response sent to %s", user_id)

                # Set cooldown for AI command (only for non-custom prompts)
                if not custom_prompt:
                    cooldown_manager.set_cooldown('ai', message.author.name)

                break  # Successfully processed, break out of retry loop

            except (TimeoutError, asyncio.TimeoutError):
                if retry < max_retries:
                    logger.warning("OpenAI API timeout for %s, retry %d/%d",
                                   user_id, retry+1, max_retries)
                    await asyncio.sleep(Numbers.INITIAL_BACKOFF_SECONDS)
                else:
                    await message.channel.send("The AI is thinking too hard right now. "
                                               "Please try again shortly! 🕒")
                    logger.warning("OpenAI API timeout for %s after %d retries",
                                   user_id, max_retries)
                    break

            except openai.RateLimitError:
                await message.channel.send(
                    "I'm a bit overwhelmed right now. Please try again in a moment! 🐺"
                )
                logger.warning("OpenAI rate limit reached for %s", user_id)
                break

            except openai.APIError as e:
                if retry < max_retries:
                    logger.warning("OpenAI API error for %s, retry %d/%d: %s",
                                   user_id, retry+1, max_retries, str(e))
                    await asyncio.sleep(Numbers.INITIAL_BACKOFF_SECONDS)
                else:
                    await message.channel.send(
                        "Having some technical difficulties. Please try again later! 🛠️"
                    )
                    logger.error("OpenAI API error after %d retries: %s", max_retries, str(e))
                    break

            except Exception as e:
                await message.channel.send(
                    "Sorry, I couldn't process that. Please try again later."
                )
                logger.error("Error processing AI command: %s", str(e))
                break

    except Exception as e:
        logger.error("Unexpected error in handle_ai_command: %s", str(e))
        import traceback
        logger.error(traceback.format_exc())
        try:
            await message.channel.send("Something went wrong. Please try again later.")
        except Exception:
            pass  # If we can't even send a message, just log and continue
