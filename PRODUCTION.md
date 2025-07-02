# Production Deployment Guide for MurphyAI Twitch Bot

This guide covers best practices for deploying the MurphyAI Twitch bot in a production environment.

## Recent Improvements

The bot has been enhanced with the following production-ready features:

### 1. **Security Enhancements**
- ✅ Created `env.example` file for secure configuration management
- ✅ Removed all hardcoded values (usernames, API models, etc.)
- ✅ Added comprehensive input validation and sanitization
- ✅ Implemented AI prompt injection protection

### 2. **Rate Limiting & Cooldowns**
- ✅ Added command cooldown system to prevent spam
- ✅ Implemented per-user and global cooldowns
- ✅ Special reduced cooldowns for moderators
- ✅ Memory-efficient cooldown cleanup

### 3. **Error Handling & Resilience**
- ✅ Created retry utilities with exponential backoff
- ✅ Added circuit breaker pattern for external services
- ✅ Improved API error handling

### 4. **Removed Issues**
- ✅ Disabled test message that was sent every hour
- ✅ Made queue default user configurable
- ✅ Made AI model configurable via environment

## Pre-Deployment Checklist

### 1. **Environment Configuration**
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your production values
# IMPORTANT: Never commit .env to version control
```

### 2. **Required Environment Variables**
- `TWITCH_TOKEN` - Your bot's OAuth token (required)
- `TWITCH_CLIENT_ID` - Twitch application client ID (required)
- `TWITCH_INITIAL_CHANNELS` - Comma-separated channel list (required)
- `OPENAI_API_KEY` - OpenAI API key for AI features (required for AI commands)
- `ENVIRONMENT` - Set to "production"

### 3. **Optional Configuration**
- `DEFAULT_QUEUE_USER` - Default user in queue (leave empty for no default)
- `OPENAI_MODEL` - AI model to use (defaults to gpt-3.5-turbo)
- `DEFAULT_TEAM_SIZE` - Default team size for queue
- `DEFAULT_QUEUE_SIZE` - Default main queue size

## Production Server Setup

### 1. **System Requirements**
- Python 3.9 or higher
- 2GB RAM minimum (4GB recommended)
- Stable internet connection
- Linux server (Ubuntu 20.04+ recommended)

### 2. **Installation Steps**
```bash
# Clone the repository
git clone https://github.com/yourusername/MurphyAI.git
cd MurphyAI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs state/ai_cache state/command_backups
```

### 3. **Systemd Service Setup**
Create `/etc/systemd/system/murphyai.service`:

```ini
[Unit]
Description=MurphyAI Twitch Bot
After=network.target

[Service]
Type=simple
User=murphyai
Group=murphyai
WorkingDirectory=/opt/murphyai
Environment="PATH=/opt/murphyai/venv/bin"
ExecStart=/opt/murphyai/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/murphyai/logs/stdout.log
StandardError=append:/opt/murphyai/logs/stderr.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/murphyai/logs /opt/murphyai/state

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable murphyai
sudo systemctl start murphyai
```

## Security Best Practices

### 1. **API Key Security**
- Store all sensitive data in environment variables
- Use a secrets management system in production (AWS Secrets Manager, HashiCorp Vault)
- Rotate API keys regularly
- Monitor API usage for anomalies

### 2. **File Permissions**
```bash
# Set appropriate permissions
chmod 600 .env
chmod 700 logs/ state/
chown -R murphyai:murphyai /opt/murphyai
```

### 3. **Network Security**
- Run the bot behind a firewall
- Only allow outbound connections to required services
- Consider using a VPN for additional security

## Monitoring & Maintenance

### 1. **Log Management**
- Logs rotate automatically (max 10MB, 5 backups)
- Monitor `logs/murphyai.log` for errors
- Set up log aggregation (ELK stack, Datadog, etc.)

### 2. **Health Monitoring**
Use the built-in health check command:
```
\healthcheck  # Channel owner only
```

Monitor these metrics:
- Memory usage
- CPU usage
- API response times
- Error rates
- Command usage statistics

### 3. **Backup Strategy**
Regular backups should include:
- `dynamic_commands.json` - User-created commands
- `state/` directory - Bot state and caches
- `.env` file (stored securely)

Automated backup script example:
```bash
#!/bin/bash
BACKUP_DIR="/backup/murphyai"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/murphyai_backup_$DATE.tar.gz" \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='logs/*.log' \
  /opt/murphyai
```

### 4. **Performance Tuning**
- Monitor memory usage of user_conversations cache
- Clear old cooldowns periodically (automatic)
- Optimize AI token usage to reduce costs
- Use connection pooling for database operations (if added)

## Troubleshooting

### Common Issues

1. **Bot disconnects frequently**
   - Check internet stability
   - Verify OAuth token hasn't expired
   - Check Twitch API status

2. **High memory usage**
   - Reduce cache sizes
   - Clear old conversation history
   - Check for memory leaks in custom commands

3. **AI commands slow/failing**
   - Check OpenAI API status
   - Verify API key and rate limits
   - Monitor circuit breaker status

### Debug Mode
For troubleshooting, temporarily set:
```bash
LOG_LEVEL=DEBUG
```

## Scaling Considerations

### Horizontal Scaling
For multiple channels:
- Run separate bot instances per channel group
- Use a message queue for command processing
- Implement distributed caching (Redis)

### Database Integration
For persistence at scale:
- Replace pickle files with PostgreSQL/MySQL
- Use SQLAlchemy for ORM
- Implement connection pooling

## Security Incident Response

1. **If API keys are compromised:**
   - Immediately revoke compromised keys
   - Generate new keys
   - Update .env file
   - Restart the bot
   - Review logs for unauthorized usage

2. **If bot is spamming:**
   - Use `\restart` command
   - Check for malicious dynamic commands
   - Review recent command additions
   - Temporarily increase cooldowns

## Additional Recommendations

1. **Use a process manager** like PM2 for better process management
2. **Implement metrics collection** using Prometheus/Grafana
3. **Set up alerts** for critical errors and downtime
4. **Regular security audits** of dependencies
5. **Document custom commands** and their purposes

## Contact & Support

For production issues:
1. Check logs first
2. Use `\healthcheck` command
3. Review this documentation
4. Check GitHub issues
5. Contact maintainers with detailed error reports

Remember: The bot includes self-healing capabilities and will attempt to recover from most failures automatically.
