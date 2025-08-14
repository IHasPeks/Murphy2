import openai
import logging
import time
import os
import json
import asyncio
from datetime import datetime, timedelta
from openai import OpenAI
from config import OPENAI_API_KEY
from config import TWITCH_PREFIX

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# Store conversation history for each user
user_conversations = {}

# Import constants
from constants import Numbers, Paths, Messages, Models

# Rate limiting configuration
request_timestamps = []
user_request_timestamps = {}  # Keep track of per-user timestamps

# Cache for recent AI responses
response_cache = {}

# Create cache directory if it doesn't exist
os.makedirs(Paths.AI_CACHE_DIR, exist_ok=True)

# Cache configuration
CACHE_FILE = Paths.AI_CACHE_FILE
CONVERSATION_FILE = Paths.CONVERSATIONS_FILE
CACHE_EXPIRY = Numbers.CACHE_EXPIRY_SECONDS
MAX_CACHE_SIZE = Numbers.MAX_CACHE_SIZE
MAX_CONVERSATION_HISTORY = Numbers.MAX_CONVERSATION_HISTORY
MAX_REQUESTS_PER_MINUTE = Numbers.MAX_REQUESTS_PER_MINUTE
MAX_REQUESTS_PER_USER_MINUTE = Numbers.MAX_REQUESTS_PER_USER_MINUTE
MAX_MESSAGE_LENGTH = Numbers.MAX_MESSAGE_LENGTH

def load_cache():
    """Load cached responses from disk"""
    global response_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                # Filter out expired entries
                current_time = time.time()
                response_cache = {
                    k: v for k, v in data.items()
                    if v.get('timestamp', 0) + CACHE_EXPIRY > current_time
                }
            logger.info(f"Loaded {len(response_cache)} AI response cache entries from disk")
    except Exception as e:
        logger.error(f"Failed to load AI response cache: {e}")
        response_cache = {}

def save_cache():
    """Save cached responses to disk"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(response_cache, f)
        logger.info(f"Saved {len(response_cache)} AI response cache entries to disk")
    except Exception as e:
        logger.error(f"Failed to save AI response cache: {e}")

def load_conversations():
    """Load user conversations from disk"""
    global user_conversations
    try:
        if os.path.exists(CONVERSATION_FILE):
            with open(CONVERSATION_FILE, 'r') as f:
                user_conversations = json.load(f)
            logger.info(f"Loaded conversations for {len(user_conversations)} users from disk")
    except Exception as e:
        logger.error(f"Failed to load user conversations: {e}")
        user_conversations = {}

def save_conversations():
    """Save user conversations to disk"""
    try:
        with open(CONVERSATION_FILE, 'w') as f:
            json.dump(user_conversations, f)
        logger.info(f"Saved conversations for {len(user_conversations)} users to disk")
    except Exception as e:
        logger.error(f"Failed to save user conversations: {e}")

# Load cached data at module initialization
load_cache()
load_conversations()

# Set up periodic cache saving
async def periodic_cache_save():
    """Periodically save cache and conversations to disk"""
    while True:
        await asyncio.sleep(300)  # Save every 5 minutes
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
    if len(response_cache) > MAX_CACHE_SIZE:
        # Remove oldest entries
        oldest_keys = sorted(response_cache.items(),
                             key=lambda x: x[1]['timestamp'])[:len(response_cache) - MAX_CACHE_SIZE]
        for key, _ in oldest_keys:
            del response_cache[key]

def get_from_cache(user_id, prompt):
    """Get a response from the cache if it exists and is not expired"""
    cache_key = f"{user_id}:{prompt}"

    if cache_key in response_cache:
        entry = response_cache[cache_key]
        # Check if the entry is still valid
        if entry['timestamp'] + CACHE_EXPIRY > time.time():
            logger.info(f"Cache hit for user {user_id}")
            return entry['response']
        else:
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
    if len(request_timestamps) >= MAX_REQUESTS_PER_MINUTE:
        logger.warning(f"Global rate limit exceeded: {len(request_timestamps)} requests in the last minute")
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
        if len(user_request_timestamps[user_id]) >= MAX_REQUESTS_PER_USER_MINUTE:
            logger.warning(f"User rate limit exceeded for {user_id}: {len(user_request_timestamps[user_id])} requests in the last minute")
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
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a health check. Respond with 'OK'."},
                {"role": "user", "content": "Status?"}
            ],
            max_tokens=5,
            temperature=0,
            timeout=5  # Short timeout for health check
        )

        # Check the response
        if response and response.choices and response.choices[0].message:
            return "OK"
        else:
            return "DEGRADED (Unexpected response format)"

    except openai.RateLimitError:
        return "RATE LIMITED"
    except openai.APIError as e:
        return f"API ERROR ({str(e)[:30]}...)"
    except Exception as e:
        return f"ERROR ({str(e)[:30]}...)"

async def handle_ai_command(bot, message, custom_prompt=None):
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

        logger.info(f"Processing AI command from {user_id}: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

        # Check rate limiting for this user
        if not check_rate_limit(user_id):
            remaining_time = 60 - max([time.time() - t for t in user_request_timestamps.get(user_id, [time.time() - 61])])
            await message.channel.send(f"You're using the AI too frequently! Please wait {int(remaining_time)} seconds before trying again.")
            return

        # Check if we have a cached response
        cached_response = get_from_cache(user_id, prompt)
        if cached_response:
            await message.channel.send(cached_response)
            logger.info(f"Sent cached AI response to {user_id}")
            return

        # Get user's conversation history or create new one
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # Add user's message to history
        user_conversations[user_id].append({"role": "user", "content": prompt})

        # Keep only last 10 messages to avoid token limits
        if len(user_conversations[user_id]) > 10:
            user_conversations[user_id] = user_conversations[user_id][-10:]

        # Create messages array with system prompt and history
        messages = [
            {
                "role": "system",
                "content": "You are Murphy, the companion of streamer Peks. Your role is to create funny, troll-like responses that might annoy the audience, ensuring they include some emoticons like 'okayCousin', 'BedgeCousin', or any Twitch emotes. Output Format: Short and humorous responses. Include Twitch emotes or emojis",
            },
            *user_conversations[user_id],
        ]

        # Make API call with timeout protection and retries
        max_retries = 2
        # Get model from environment or use default
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        for retry in range(max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7,
                    timeout=10  # 10-second timeout
                )

                reply = response.choices[0].message.content

                # Add assistant's reply to history
                user_conversations[user_id].append({"role": "assistant", "content": reply})

                # Add to cache
                add_to_cache(user_id, prompt, reply)

                await message.channel.send(reply)
                logger.info(f"AI response sent to {user_id}")

                # Set cooldown for AI command (only for non-custom prompts)
                if not custom_prompt:
                    cooldown_manager.set_cooldown('ai', message.author.name)

                break  # Successfully processed, break out of retry loop

            except (TimeoutError, asyncio.TimeoutError):
                if retry < max_retries:
                    logger.warning(f"OpenAI API timeout for {user_id}, retry {retry+1}/{max_retries}")
                    await asyncio.sleep(1)  # Wait before retrying
                else:
                    await message.channel.send("The AI is thinking too hard right now. Please try again shortly! 🕒")
                    logger.warning(f"OpenAI API timeout for {user_id} after {max_retries} retries")
                    break

            except openai.RateLimitError:
                await message.channel.send(
                    "I'm a bit overwhelmed right now. Please try again in a moment! 🐺"
                )
                logger.warning(f"OpenAI rate limit reached for {user_id}")
                break

            except openai.APIError as e:
                if retry < max_retries:
                    logger.warning(f"OpenAI API error for {user_id}, retry {retry+1}/{max_retries}: {str(e)}")
                    await asyncio.sleep(1)  # Wait before retrying
                else:
                    await message.channel.send(
                        "Having some technical difficulties. Please try again later! 🛠️"
                    )
                    logger.error(f"OpenAI API error after {max_retries} retries: {str(e)}")
                    break

            except Exception as e:
                await message.channel.send(
                    "Sorry, I couldn't process that. Please try again later."
                )
                logger.error(f"Error processing AI command: {str(e)}")
                break

    except Exception as e:
        logger.error(f"Unexpected error in handle_ai_command: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        try:
            await message.channel.send("Something went wrong. Please try again later.")
        except:
            pass  # If we can't even send a message, just log and continue
