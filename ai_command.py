import openai
import logging
import time
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

# Rate limiting configuration
MAX_REQUESTS_PER_MINUTE = 20
request_timestamps = []

def check_rate_limit():
    """
    Check if we've exceeded our rate limit
    Returns True if we can proceed, False if we're rate limited
    """
    current_time = time.time()

    # Remove timestamps older than 60 seconds
    global request_timestamps
    request_timestamps = [t for t in request_timestamps if current_time - t < 60]

    # Check if we've exceeded our limit
    if len(request_timestamps) >= MAX_REQUESTS_PER_MINUTE:
        return False

    # Add current timestamp and proceed
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
        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:officiallysp:murphy2feb2nd2025:AwWr0fDu",
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
        # Check if OpenAI client was initialized properly
        if client is None:
            await message.channel.send("AI service is currently unavailable. Please try again later.")
            logger.error("AI command attempted but OpenAI client is not initialized")
            return

        # Check rate limit
        if not check_rate_limit():
            await message.channel.send("Too many AI requests right now. Please try again in a minute!")
            logger.warning(f"Rate limit exceeded for AI command from {message.author.name}")
            return

        # Get user's conversation history or create new one
        user_id = message.author.name
        if user_id not in user_conversations:
            user_conversations[user_id] = []

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

        logger.info(f"Processing AI command from {user_id}: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

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

        # Make API call with timeout protection
        try:
            response = client.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:officiallysp:murphy2feb2nd2025:AwWr0fDu",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                timeout=10  # 10-second timeout
            )

            reply = response.choices[0].message.content

            # Add assistant's reply to history
            user_conversations[user_id].append({"role": "assistant", "content": reply})

            await message.channel.send(reply)
            logger.info(f"AI response sent to {user_id}")

        except TimeoutError:
            await message.channel.send("The AI is thinking too hard right now. Please try again shortly! 🕒")
            logger.warning(f"OpenAI API timeout for {user_id}")

    except openai.RateLimitError:
        await message.channel.send(
            "I'm a bit overwhelmed right now. Please try again in a moment! 🐺"
        )
        logger.warning(f"OpenAI rate limit reached for {user_id}")

    except openai.APIError as e:
        await message.channel.send(
            "Having some technical difficulties. Please try again later! 🛠️"
        )
        logger.error(f"OpenAI API error: {str(e)}")

    except Exception as e:
        await message.channel.send(
            "Sorry, I couldn't process that. Please try again later."
        )
        logger.error(f"Error processing AI command: {str(e)}")
