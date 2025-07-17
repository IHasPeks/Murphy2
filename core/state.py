"""
State management for MurphyAI bot
Handles state persistence and recovery
"""

import os
import pickle
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime

from constants import Paths

logger = logging.getLogger(__name__)


class StateManager:
    """Manages bot state persistence and recovery"""

    def __init__(self):
        self.state_file = Paths.BOT_STATE_FILE
        self.restart_counter_file = Paths.RESTART_COUNTER_FILE
        
        # Initialize state
        self.known_users: Set[str] = set()
        self.start_time = datetime.now().timestamp()
        self.message_count = 0
        self.command_count = 0
        self.error_count = 0
        self.last_reconnect_time = 0
        self.reconnect_attempts = 0
        
        # Command counters
        self.command_counters: Dict[str, int] = {
            'cannon': 0,
            'quadra': 0,
            'penta': 0
        }

    def save_state(self) -> None:
        """Save current bot state to disk"""
        try:
            state = {
                "known_users": list(self.known_users),
                "start_time": self.start_time,
                "message_count": self.message_count,
                "command_count": self.command_count,
                "error_count": self.error_count,
                "last_reconnect_time": self.last_reconnect_time,
                "reconnect_attempts": self.reconnect_attempts,
                "command_counters": self.command_counters,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.state_file, 'wb') as f:
                pickle.dump(state, f)
            
            logger.info("Bot state saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save bot state: {e}")

    def load_state(self) -> None:
        """Load bot state from disk if available"""
        if not os.path.exists(self.state_file):
            logger.info("No saved state found, starting fresh")
            return
            
        try:
            with open(self.state_file, 'rb') as f:
                state = pickle.load(f)
            
            # Restore state
            self.known_users = set(state.get("known_users", []))
            self.start_time = state.get("start_time", datetime.now().timestamp())
            self.message_count = state.get("message_count", 0)
            self.command_count = state.get("command_count", 0)
            self.error_count = state.get("error_count", 0)
            self.last_reconnect_time = state.get("last_reconnect_time", 0)
            self.reconnect_attempts = state.get("reconnect_attempts", 0)
            self.command_counters = state.get("command_counters", {
                'cannon': 0,
                'quadra': 0,
                'penta': 0
            })
            
            logger.info("Bot state loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load bot state: {e}")
            logger.info("Starting with default state")

    def increment_message_count(self) -> None:
        """Increment message counter"""
        self.message_count += 1

    def increment_command_count(self) -> None:
        """Increment command counter"""
        self.command_count += 1

    def increment_error_count(self) -> None:
        """Increment error counter"""
        self.error_count += 1

    def add_known_user(self, username: str) -> bool:
        """Add a user to known users set. Returns True if user was new"""
        if username not in self.known_users:
            self.known_users.add(username)
            return True
        return False

    def get_command_count(self, command: str) -> int:
        """Get count for a specific command"""
        return self.command_counters.get(command, 0)

    def increment_command_counter(self, command: str) -> int:
        """Increment and return count for a specific command"""
        if command not in self.command_counters:
            self.command_counters[command] = 0
        self.command_counters[command] += 1
        return self.command_counters[command]

    def get_uptime(self) -> str:
        """Get formatted uptime string"""
        uptime_seconds = int(datetime.now().timestamp() - self.start_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            uptime_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            uptime_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not uptime_parts:
            uptime_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(uptime_parts)

    def get_restart_count(self) -> int:
        """Get current restart attempt count"""
        try:
            if os.path.exists(self.restart_counter_file):
                with open(self.restart_counter_file, 'rb') as f:
                    return pickle.load(f)
            return 0
        except Exception:
            return 0

    def increment_restart_count(self) -> int:
        """Increment restart attempt counter"""
        try:
            count = self.get_restart_count() + 1
            with open(self.restart_counter_file, 'wb') as f:
                pickle.dump(count, f)
            return count
        except Exception as e:
            logger.error(f"Failed to increment restart counter: {e}")
            return 1

    def reset_restart_counter(self) -> None:
        """Reset restart counter after successful initialization"""
        try:
            with open(self.restart_counter_file, 'wb') as f:
                pickle.dump(0, f)
        except Exception as e:
            logger.warning(f"Failed to reset restart counter: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        return {
            "uptime": self.get_uptime(),
            "message_count": self.message_count,
            "command_count": self.command_count,
            "error_count": self.error_count,
            "known_users": len(self.known_users),
            "restart_count": self.get_restart_count(),
            "command_counters": self.command_counters.copy()
        } 