"""
Pytest configuration and fixtures for MurphyAI bot tests
"""

import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

# Set test environment variables
os.environ.update({
    'TWITCH_TOKEN': 'test_token',
    'TWITCH_CLIENT_ID': 'test_client_id',
    'OPENAI_API_KEY': 'test_openai_key',
    'BOT_NICK': 'TestBot',
    'TWITCH_INITIAL_CHANNELS': 'testchannel',
    'LOG_LEVEL': 'DEBUG'
})


@pytest.fixture
def mock_message():
    """Create a mock Twitch message object"""
    message = MagicMock()
    message.author.name = "testuser"
    message.content = "test message"
    message.channel = type("Chan", (), {"name": "testchannel", "send": AsyncMock()})()
    return message


@pytest.fixture
def mock_bot():
    """Create a mock bot instance"""
    bot = MagicMock()
    bot.nick = "TestBot"
    bot.connected_channels = ["testchannel"]
    bot.queue_manager = MagicMock()
    return bot


@pytest.fixture
def temp_state_dir():
    """Create a temporary state directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override state paths for testing
        import constants
        original_state_dir = constants.Paths.STATE_DIR
        constants.Paths.STATE_DIR = temp_dir
        constants.Paths.BOT_STATE_FILE = os.path.join(temp_dir, "bot_state.pkl")
        constants.Paths.RESTART_COUNTER_FILE = os.path.join(temp_dir, "restart_counter.pkl")
        
        yield temp_dir
        
        # Restore original paths
        constants.Paths.STATE_DIR = original_state_dir


@pytest.fixture
def sample_queue_data():
    """Sample queue data for testing"""
    return {
        "main_queue": ["player1", "player2", "player3"],
        "overflow_queue": ["player4", "player5"],
        "team_size": 5,
        "queue_user": "testuser"
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "This is a test AI response"
    return response
