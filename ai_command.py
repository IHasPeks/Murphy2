import openai
from config import OPENAI_API_KEY
from config import TWITCH_PREFIX

openai.api_key = OPENAI_API_KEY


async def handle_ai_command(bot, message):
    user_message = message.content[len(TWITCH_PREFIX) :]
    if not user_message.strip():
        await message.channel.send("Please provide a message for the AI.")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "The name of the streamer is Peks. His avatar is a shiba inu doge. He likes playing League of Legends and Overwatch 2. He mains Twitch in League of Legends and Genji in Overwatch 2. He's born in England, but has lived in France since he was 4, so Peks is French. Try to come up with funny and troll answers. Stuff that would annoy viewers.",
                },
                {"role": "user", "content": user_message},
            ],
        )
        await message.channel.send(response.choices[0].message["content"])
    except Exception as e:
        await message.channel.send("Sorry, I couldn't process that. Please try again later.")
        print(f"Error processing AI command: {e}")
