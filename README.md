[![Pylint](https://github.com/IHasPeks/Murphy2/actions/workflows/pylint.yml/badge.svg)](https://github.com/IHasPeks/Murphy2/actions/workflows/pylint.yml)
# MurphyAI Twitch Bot

A feature-rich Twitch chat bot built with Python designed to enhance stream interaction through custom commands, AI responses, and queue management.

## Features

- **Custom Commands**: Add, remove, and list dynamic chat commands
- **AI Integration**: Utilize OpenAI's GPT models for interactive responses
- **Queue Management**: Manage viewer queues for games
- **Translation**: Translate messages from different languages
- **Event Scheduling**: Track stream schedules and notify viewers
- **Fun Interactions**: Various interactive commands for viewer engagement
- **Self-Healing**: Automatic recovery from crashes with exponential backoff
- **State Persistence**: Maintains state across restarts and crashes
- **Remote Management**: Channel owner can control and monitor the bot via chat commands

## Setup

### Prerequisites

- Python 3.9 or higher
- A Twitch account for the bot
- Twitch developer application credentials
- OpenAI API key (for AI commands)

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/MurphyAI.git
   cd MurphyAI
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Configure your environment
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials:
   - Add your Twitch OAuth token (get from https://twitchapps.com/tmi/)
   - Add your Twitch client ID
   - Add your OpenAI API key
   - Configure channel names and other settings

## Running the Bot

Start the bot with:
```
python bot.py
```

### Production Deployment

For production deployment, consider:

1. **Using a Process Manager**: Set up with PM2 or systemd to ensure the bot restarts after crashes

    Example systemd service:
    ```
    [Unit]
    Description=MurphyAI Twitch Bot
    After=network.target

    [Service]
    User=yourusername
    WorkingDirectory=/path/to/MurphyAI
    ExecStart=/path/to/MurphyAI/venv/bin/python bot.py
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    ```

2. **Setting Up Monitoring**: Monitor logs for errors using tools like Datadog or CloudWatch

3. **Regular Backups**: Ensure `dynamic_commands.json` is backed up regularly

4. **State Directory**: The `state` directory contains saved bot state - include this in backups

## Command Reference

### User Commands
- `?join` - Join the viewer queue
- `?leave` - Leave the queue
- `?here` - Mark yourself as available in the queue
- `?nothere` - Mark yourself as unavailable
- `?Q` - View current queue
- `?ai <message>` - Get AI response from Murphy
- `?t <text>` - Translate text to English
- `?joke` - Get a random joke
- `?latege` - Check stream schedule status
- `?spam <message>` - Repeat a message multiple times
- `?botstat` - Show bot statistics including uptime and message counts

### Moderator Commands
- `\fleave <username>` - Force-remove a user from queue
- `\fjoin <username>` - Force-add a user to queue
- `\moveup <username>` - Move user up in queue
- `\movedown <username>` - Move user down in queue
- `\teamsize <number>` - Set team size
- `\shuffle` - Shuffle teams
- `\clearqueue` - Clear all queues

### Channel Owner Only Commands
- `\restart` - Remotely restart the bot (channel owner only)
- `\healthcheck` - Run a health check on all bot components (channel owner only)

### Dynamic Commands
- `?addcmd <name> <response>` - Add a custom command
- `?delcmd <name>` - Remove a custom command
- `?listcmds` - List all custom commands

## Resilience Features

The bot includes several resilience features to ensure reliable operation:

1. **Auto-Recovery**: The bot includes a crash recovery system with exponential backoff
2. **State Persistence**: Essential state is saved and recovered across restarts
3. **Remote Restart**: Channel owner can trigger a restart directly from chat
4. **Health Monitoring**: System resource usage and component health can be checked
5. **Improved Error Handling**: All critical operations have robust error handling

## Maintenance and Troubleshooting

### Log Files
Logs are stored in the `logs/` directory. Check `murphyai.log` for issues.

### Common Issues
- **Bot disconnects frequently**: Check your internet connection and Twitch token validity
- **AI commands not working**: Verify your OpenAI API key and rate limits
- **Commands not responding**: Check the logs for errors
- **Bot crashed**: Use the `\restart` command to restart the bot, or check the crash recovery logs

### Remote Management
As the channel owner, you can:
- Use `\restart` to restart the bot if it's behaving incorrectly
- Use `\healthcheck` to see the status of various components
- Use `?botstat` to view current bot statistics

## License

See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
