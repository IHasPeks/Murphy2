# MurphyAI Twitch Bot - 2025 Edition

A modern, feature-rich Twitch chatbot built with Python 3.11+ and the latest dependencies. This is a complete rewrite of the original MurphyAI bot with improved architecture, better error handling, and modern Python practices.

## ✨ Features

### 🤖 AI Integration
- **OpenAI GPT Integration**: Powered by the latest OpenAI API (v1.97.0)
- **Context-Aware Responses**: Maintains conversation history for better responses
- **Smart Rate Limiting**: Prevents API abuse with intelligent rate limiting
- **Caching System**: Reduces API calls with intelligent response caching

### 🎮 Queue Management
- **Team-Based Queues**: Manage player queues with configurable team sizes
- **Overflow Support**: Automatic overflow queue when main queue is full
- **Advanced Controls**: Move users up/down, force join/kick, shuffle teams
- **Away System**: Users can mark themselves as away with auto-removal

### 🔧 Command System
- **Dynamic Commands**: Add/remove commands on-the-fly
- **Command Aliases**: Multiple aliases for the same command
- **Cooldown Management**: Intelligent cooldown system with mod exemptions
- **Permission System**: Owner, mod, and user permission levels

### 📊 Monitoring & Analytics
- **Real-time Statistics**: Track messages, commands, errors, and uptime
- **Health Monitoring**: Comprehensive health checks with system metrics
- **Persistent State**: Automatic state saving and recovery
- **Logging**: Structured logging with rotation and multiple levels

### 🛡️ Reliability
- **Auto-Restart**: Automatic restart on crashes with exponential backoff
- **Connection Recovery**: Intelligent reconnection with retry logic
- **Error Handling**: Comprehensive error handling and recovery
- **State Persistence**: Save and restore bot state across restarts

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Twitch account for the bot
- OpenAI API key (optional, for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MurphyAI2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Configuration

#### Required Settings
- `TWITCH_TOKEN`: OAuth token from [Twitch Token Generator](https://twitchapps.com/tmi/)
- `TWITCH_CLIENT_ID`: Client ID from [Twitch Developer Console](https://dev.twitch.tv/console/apps)
- `TWITCH_INITIAL_CHANNELS`: Comma-separated list of channels to join

#### Optional Settings
- `OPENAI_API_KEY`: For AI features
- `TWITCH_PREFIX`: Command prefix (default: `?`)
- `MOD_PREFIX`: Moderator command prefix (default: `\\`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

See `env.example` for all available configuration options.

## 🏗️ Architecture

### Modern Design Principles
- **Separation of Concerns**: Clean separation between bot logic, state management, and events
- **Dependency Injection**: Components are loosely coupled and easily testable
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Error Handling**: Structured error handling with proper logging

### Core Components

#### `core/bot.py`
The main bot class that orchestrates all components and handles TwitchIO integration.

#### `core/state.py`
**StateManager**: Handles all bot state persistence and recovery
- User tracking and statistics
- Command counters and usage metrics
- Restart tracking and recovery

#### `core/events.py`
**EventHandler**: Processes all bot events in a clean, organized manner
- Message processing and routing
- Connection management
- Error handling and recovery

#### `commands.py`
Command processing and routing system with support for:
- Static commands with counters
- Dynamic commands with aliases
- Permission-based access control

#### `ai_command.py`
AI integration with OpenAI API including:
- Conversation context management
- Rate limiting and caching
- Error handling and fallbacks

#### `queue_manager.py`
Queue management system for team-based gameplay:
- Multi-queue support (main + overflow)
- Team shuffling and management
- User availability tracking

### Dependencies

#### Core Dependencies
- **TwitchIO 3.0.1**: Modern Twitch API integration
- **OpenAI 1.97.0**: Latest OpenAI API client
- **Python-dotenv 1.0.1**: Environment variable management
- **PSUtil 6.1.0**: System monitoring

#### Supporting Libraries
- **APScheduler 3.10.4**: Task scheduling
- **Requests 2.32.3**: HTTP requests
- **Watchdog 6.0.0**: File system monitoring
- **Googletrans 4.0.0rc1**: Translation support

## 🎛️ Commands

### User Commands
- `?join` - Join the queue
- `?leave` - Leave the queue
- `?Q` - Show current queue
- `?here` - Mark yourself as available
- `?nothere` - Mark yourself as not available
- `?ai <message>` - Chat with AI
- `?joke` - Get a random joke
- `?t <text>` - Translate text to English
- `?coin` - Flip a coin
- `?cannon` - Increment cannon counter
- `?quadra` - Increment quadra counter
- `?penta` - Increment penta counter
- `?botstat` - Show bot statistics

### Moderator Commands
- `\\teamsize <size>` - Set team size
- `\\fleave <username>` - Force remove user from queue
- `\\fjoin <username>` - Force add user to queue
- `\\moveup <username>` - Move user up in queue
- `\\movedown <username>` - Move user down in queue
- `\\shuffle` - Shuffle teams
- `\\clearqueue` - Clear all queues
- `\\addcmd <name> <response>` - Add dynamic command
- `\\delcmd <name>` - Delete dynamic command
- `\\listcmds` - List all dynamic commands

### Owner Commands
- `\\restart` - Restart the bot
- `\\healthcheck` - Show detailed health information

## 🔧 Development

### Project Structure
```
MurphyAI2/
├── core/                   # Core bot components
│   ├── __init__.py
│   ├── bot.py             # Main bot class
│   ├── events.py          # Event handling
│   └── state.py           # State management
├── config.py              # Configuration management
├── constants.py           # Application constants
├── commands.py            # Command processing
├── ai_command.py          # AI integration
├── queue_manager.py       # Queue management
├── cooldown_manager.py    # Cooldown system
├── dynamic_commands.py    # Dynamic command system
├── validation_utils.py    # Input validation
├── utils.py               # Utility functions
├── main.py                # Application entry point
├── requirements.txt       # Dependencies
└── .env.example          # Configuration template
```

### Adding New Commands

1. **Static Command**: Add to `commands.py`
   ```python
   async def handle_mycommand(message, args: str) -> None:
       await message.channel.send("My response")
   ```

2. **Dynamic Command**: Use in chat
   ```
   \\addcmd mycommand My response here
   ```

### Adding New Features

1. **Extend StateManager**: Add new state properties
2. **Add Event Handlers**: Extend EventHandler class
3. **Update Configuration**: Add new config options
4. **Add Tests**: Create comprehensive tests

## 🛠️ Maintenance

### Logs
- Location: `logs/murphyai.log`
- Rotation: 10MB max, 5 backup files
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### State Files
- `state/bot_state.pkl`: Bot state and statistics
- `state/restart_counter.pkl`: Restart tracking
- `state/ai_cache/`: AI response caching
- `state/command_backups/`: Dynamic command backups

### Monitoring
- Use `\\healthcheck` for system health
- Monitor logs for errors and warnings
- Check `\\botstat` for runtime statistics

## 🔄 Migration from Old Version

1. **Backup Data**: Save your old `dynamic_commands.json` and state files
2. **Update Dependencies**: Install new requirements
3. **Update Configuration**: Migrate to new `.env` format
4. **Test**: Run in development mode first
5. **Deploy**: Switch to production mode

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type hints
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Original MurphyAI bot inspiration
- TwitchIO library for Twitch integration
- OpenAI for AI capabilities
- Python community for excellent libraries

## 🆘 Support

If you encounter issues:
1. Check the logs in `logs/murphyai.log`
2. Verify your configuration in `.env`
3. Use `\\healthcheck` to diagnose problems
4. Check the GitHub issues page
5. Create a new issue with detailed information

## 📋 Changelog

### Version 2.0.0 (2025)
- Complete rewrite with modern Python practices
- Updated to TwitchIO 3.0.1 and OpenAI 1.97.0
- Improved architecture with proper separation of concerns
- Enhanced error handling and recovery
- Better logging and monitoring
- Comprehensive type hints
- Environment-based configuration
- Automated testing structure
- Security improvements
