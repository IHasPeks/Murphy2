# 🤖 MurphyAI Twitch Bot

A secure, production-ready Twitch chatbot designed for single streamers running locally on their PC.

## ✨ Features

- **🎮 Queue Management** - Organize viewer games with automatic team formation
- **🤖 AI Chat Integration** - Natural conversations powered by OpenAI
- **⚡ Dynamic Commands** - Create custom commands on the fly
- **🛡️ Security First** - Rate limiting, input validation, and secure state storage
- **📊 Health Monitoring** - Built-in health checks and performance tracking
- **🔄 Auto-cleanup** - Automatic memory management for 24/7 operation

## 🚀 Quick Start

### Windows Users
Just double-click `start_bot.bat`

### Mac/Linux Users
Run `./start_bot.sh` in terminal

### Manual Setup
See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed instructions.

## 📋 Requirements

- Python 3.11 or higher
- Windows, macOS, or Linux
- Twitch account for your bot
- OpenAI API key (optional, for AI features)

## 🎯 Designed For

This bot is specifically optimized for:
- **Single streamers** running the bot locally
- **Low resource usage** (~50-100MB RAM)
- **Easy setup** with no coding required
- **Security** with all data stored locally

## 📁 Project Structure

```
MurphyAI2/
├── start_bot.bat         # Windows quick start
├── start_bot.sh          # Mac/Linux quick start
├── main.py               # Main entry point
├── core/                 # Core bot logic
│   ├── bot.py           # Bot class
│   ├── events.py        # Event handlers
│   └── state.py         # State management
├── .env                  # Your configuration (create from env.example)
├── requirements.txt      # Python dependencies
└── LOCAL_SETUP.md       # Detailed setup guide
```

## 🔒 Security Features

- ✅ JSON-based state storage (no pickle)
- ✅ Environment variable configuration
- ✅ Input sanitization and validation
- ✅ AI prompt injection protection
- ✅ Rate limiting and cooldowns
- ✅ Secure subprocess handling

## 📝 Basic Commands

| Command | Description | Who Can Use |
|---------|-------------|-------------|
| `?ai <message>` | Chat with AI | Everyone |
| `?join` | Join queue | Everyone |
| `?Q` | Show queue | Everyone |
| `\teamsize <n>` | Set team size | Mods/Owner |
| `\restart` | Restart bot | Owner only |
| `\healthcheck` | Check bot status | Owner only |

## 🛠️ Configuration

All configuration is done through the `.env` file:

```env
# Required
TWITCH_TOKEN=oauth:your_token_here
TWITCH_CLIENT_ID=your_client_id_here
TWITCH_INITIAL_CHANNELS=yourchannel

# Optional
OPENAI_API_KEY=sk-your_key_here
```

## 📊 Performance

- **Memory**: ~50-100MB
- **CPU**: Minimal usage
- **Cleanup**: Automatic every 5 minutes
- **Uptime**: Designed for 24/7 operation

## 🆘 Troubleshooting

1. **Check logs**: `logs/murphyai.log`
2. **Health check**: Type `\healthcheck` in chat
3. **Restart**: Close and run start script again
4. **See**: [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed help

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built with [TwitchIO](https://github.com/TwitchIO/TwitchIO)
- AI powered by [OpenAI](https://openai.com/)
- Designed for the streaming community

---

**Made with ❤️ for streamers who want a reliable, local chatbot**