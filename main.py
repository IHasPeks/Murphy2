"""
Main entry point for MurphyAI Twitch Bot
Modern, clean architecture with proper error handling
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler

from config import LOG_LEVEL, LOG_FILE, ENVIRONMENT
from constants import Numbers
from core import MurphyAI


def setup_logging() -> None:
    """Setup logging configuration"""
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        os.path.join("logs", LOG_FILE),
        maxBytes=Numbers.LOG_MAX_BYTES,
        backupCount=Numbers.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("twitchio").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def main() -> None:
    """Main entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting MurphyAI Twitch Bot...")
        logger.info(f"Environment: {ENVIRONMENT}")
        
        # Create and run the bot
        bot = MurphyAI()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
        logger.critical(traceback.format_exc())
        
        # In production, try to restart
        if ENVIRONMENT == "production":
            logger.info("Attempting to restart bot...")
            try:
                import subprocess
                if sys.platform.startswith('win'):
                    subprocess.Popen(['start', 'python', __file__], shell=True)
                else:
                    subprocess.Popen(['python3', __file__])
                os._exit(1)
            except Exception as restart_error:
                logger.critical(f"Failed to restart bot: {restart_error}")
                sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    main() 