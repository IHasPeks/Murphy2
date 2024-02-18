# MurphyAI Twitch Chat Bot

MurphyAI is a Python-based Twitch chat bot designed to enhance the interaction between streamers and their audience. It features a variety of commands, a queue system for managing viewer participation, periodic messages for engagement, and an AI-powered response system using OpenAI's GPT technology.

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.
3. Create a `.env` file in the root directory and add your Twitch bot credentials and OpenAI API key as follows:
    ```
    TWITCH_TOKEN=your_twitch_bot_token
    TWITCH_CLIENT_ID=your_twitch_client_id
    OPENAI_API_KEY=your_openai_api_key
    ```
4. Update the `config.py` file with your specific settings (bot nickname, channel name, command prefix, etc.).

## Usage

To start the bot, run the following command in your terminal:

```
python bot.py
```

### Commands

see commands.py

## Scheduler

The bot includes a scheduler that sends periodic messages to the chat. You can customize the message and interval in `scheduler.py`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or encounter any problems.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
