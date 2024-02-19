# Murphy2 Twitch Chat Bot

Murphy2 is a Python-based Twitch chat bot designed for the streamer IHasPeks. It features a variety of commands, a queue system for managing viewer participation, periodic messages for engagement, and an AI-powered response system using OpenAI's GPT.

## Local Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.
3. Create a `.env` file in the root directory and add your Twitch bot credentials and OpenAI API key as follows:
    ```
    TWITCH_TOKEN=your_twitch_bot_token
    TWITCH_CLIENT_ID=your_twitch_client_id
    OPENAI_API_KEY=your_openai_api_key
    ```
4. Update the `config.py` file with your specific settings (bot nickname, channel name, command prefix, etc.). (`config.py` is not included in this repo

## Usage

To start the bot, run the following command in your terminal:

```
python bot.py
```

### Commands

see commands.py

## Scheduler

The bot includes a scheduler that sends periodic messages to the chat. You can customize the message and interval in `scheduler.py`.
