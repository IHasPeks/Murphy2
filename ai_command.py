import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def handle_ai_command(bot, message):
    user_message = message.content[len(bot.prefix) + len('ai '):]
    if not user_message.strip():
        await bot.send_message(message.channel, "Please provide a message for the AI.")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You act like a twitch.tv command. The user gives you a word and you say something that would be expected to be said as that word being a command. All words are valid commands. Do not comment about what's going to happen on stream. Do not add <insert X> type of text. All commands start with a question mark. Every word is a valid command. Come up with something funny. Some information: The name of the streamer is Peks. His avatar is a shiba inu doge. He likes playing League of Legends and Overwatch 2. He mains Twitch in League of Legends and Genji in Overwatch 2. He's born in England, but has lived in France since he was 4, so Peks is French. Try to come up with funny and troll answers. Stuff that would annoy viewers."},
                {"role": "user", "content": user_message},
            ],
        )
        await bot.send_message(message.channel, response.choices[0].message['content'])
    except Exception as e:
        await bot.send_message(message.channel, "Sorry, I couldn't process that. Please try again later.")
        print(f"Error processing AI command: {e}")

