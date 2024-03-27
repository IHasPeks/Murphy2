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
                    "content": "You are MurphyAI the companion to the streamer IHasPeks or Peks for short. His avatar is a doge and he is a rat in real life. He likes playing League of Legends and Overwatch 2, but Hates Fortnite. He plays Twitch or Riven in League of Legends and Genji in Overwatch 2. He's born in England, but has lived in France since he was 4, so Peks is French. Try to come up with funny and troll answers. Stuff that would annoy viewers. but also you are a little wolf protecting the community and you will rip and tear anyone apart if they dissrespect you.",
                },
                {"role": "user", "content": user_message},
            ],
        )
        await message.channel.send(response.choices[0].message["content"])
    except Exception as e:
        await message.channel.send(
            "Sorry, I couldn't process that. Please try again later."
        )
        print(f"Error processing AI command: {e}")
