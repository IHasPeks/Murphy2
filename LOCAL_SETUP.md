# MurphyAI Twitch Bot - Local Setup Guide

A production-ready Twitch chatbot designed for single streamers running locally on their PC.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- **Python 3.11 or higher** ([Download here](https://www.python.org/downloads/))
- A Twitch account for your bot
- Your streaming channel name

### Step 1: Get Your Tokens

1. **Twitch OAuth Token** (Bot login)
   - Go to: https://twitchapps.com/tmi/
   - Log in with your BOT account (not your main account)
   - Copy the token (starts with `oauth:`)

2. **Twitch Client ID** (Bot identity)
   - Go to: https://dev.twitch.tv/console/apps
   - Click "Register Your Application"
   - Name: MurphyAI (or anything you want)
   - OAuth Redirect URL: http://localhost
   - Category: Chat Bot
   - Copy the Client ID

3. **OpenAI API Key** (Optional - for AI features)
   - Go to: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy the key (starts with `sk-`)

### Step 2: Configure the Bot

1. Copy `env.example` to `.env`:
   ```bash
   copy env.example .env
   ```

2. Edit `.env` with Notepad or any text editor:
   ```ini
   # Required settings
   TWITCH_TOKEN=oauth:your_token_here
   TWITCH_CLIENT_ID=your_client_id_here
   TWITCH_INITIAL_CHANNELS=yourchannelname
   
   # Optional - for AI features
   OPENAI_API_KEY=sk-your_api_key_here
   ```

### Step 3: Install and Run

1. Open Command Prompt/Terminal in the bot folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the bot:
   ```bash
   python main.py
   ```

That's it! The bot should connect to your channel.

## 📝 Basic Commands

### For Everyone
- `?ai <message>` - Chat with AI (if configured)
- `?joke` - Get a random joke
- `?coin` - Flip a coin
- `?join` - Join the queue
- `?leave` - Leave the queue
- `?Q` - Show queue status

### For Mods/Streamer
- `\teamsize <number>` - Set team size
- `\shuffle` - Shuffle teams
- `\clearqueue` - Clear all queues

### For Streamer Only
- `\restart` - Restart the bot
- `\healthcheck` - Check bot health

## 🎮 Features

### Queue System
Perfect for viewer games:
- Automatic team formation
- Overflow queue management
- Not-available status tracking

### AI Integration
- Natural chat responses
- Conversation memory
- Rate limiting to prevent spam

### Dynamic Commands
Create custom commands on the fly:
- `\addcmd !hello Hello everyone!`
- `\delcmd !hello`
- `?listcmds` - List all custom commands

### Safety Features
- Command cooldowns
- Rate limiting
- Input validation
- Automatic memory cleanup
- Graceful error handling

## 🔧 Troubleshooting

### Bot won't connect
1. Check your tokens in `.env`
2. Make sure channel name is lowercase
3. Check internet connection

### Commands not working
1. Check command prefix (`?` for normal, `\` for mod)
2. Make sure bot is mod in your channel: `/mod MurphyAI`

### AI not responding
1. Check OpenAI API key
2. Check rate limits (3 per user per minute)
3. Look at logs/murphyai.log for errors

### High memory usage
- Bot automatically cleans up old data every 5 minutes
- Restart bot if needed

## 📁 File Structure

```
MurphyAI2/
├── .env                    # Your configuration (create from env.example)
├── main.py                 # Start the bot with this
├── core/                   # Core bot logic
├── logs/                   # Log files (created automatically)
├── state/                  # Bot state and cache
└── dynamic_commands.json   # Your custom commands
```

## 🛡️ Security Notes

- **Never share your `.env` file**
- Tokens are like passwords - keep them secret
- Bot runs locally on your PC - no external servers
- All state is saved in JSON (not pickle) for security

## 💡 Tips for Streamers

1. **Make the bot a mod** in your channel for full features:
   ```
   /mod MurphyAI
   ```

2. **Custom welcome message**: Edit `BOT_INITIALIZED` in `constants.py`

3. **Adjust rate limits** in `.env` if needed

4. **Monitor health** with `\healthcheck` command

5. **Regular restarts** keep the bot running smoothly

## 🔄 Updating the Bot

1. Back up your files:
   - `.env`
   - `dynamic_commands.json`
   - `state/` folder

2. Download new version

3. Copy your backed-up files back

4. Run `pip install -r requirements.txt` again

## 📊 Performance

Optimized for single-streamer use:
- Low memory footprint (~50-100MB)
- Automatic cleanup every 5 minutes
- Efficient caching system
- Rate limiting prevents API overuse

## 🆘 Getting Help

1. Check `logs/murphyai.log` for errors
2. Use `\healthcheck` to see bot status
3. Restart the bot if something seems wrong
4. Check this guide again

## 🎯 Best Practices

1. **Run on a dedicated machine** if possible
2. **Keep Python updated** (3.11+)
3. **Monitor the logs** occasionally
4. **Restart weekly** for best performance
5. **Backup your commands** regularly

---

**Remember**: This bot is designed to run locally on your PC. It's secure, efficient, and perfect for single streamers!
