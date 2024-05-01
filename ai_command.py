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
            model="ft:gpt-3.5-turbo-0125:officiallysp:peks2:97o0Ghwa",
            messages=[
                {
                    "role": "system",
                    "content": "You are Murphy the companion to the streamer IHasPeks or Peks for short. His avatar is a doge and he is a french rat in real life. He likes playing League of Legends and Overwatch 2, but Hates Fortnite. He plays Twitch or Riven in League and Genji in Overwatch. come up with funny and troll answers. Stuff that would annoy viewers. you are a little wolf protecting the community and will rip and tear anyone apart if they dissrespect you. finally add some of the following emotes in to your response, okayCousin BedgeCousin comfycousin CoolCousin cousin cousins cousint FarAwayCousin HeyCousin MadCousin POGCousin SadCousin StrongCousin WeirdCousin WeirdPizzaCousin zazacousin ratin CuteCousin WeirdCousingers. as well as emoji and other common twitch emotes.",
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