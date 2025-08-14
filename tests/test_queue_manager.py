"""
Tests for queue management functionality
"""

import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch
from queue_manager import QueueManager


class TestQueueManager:
    """Test queue manager functionality"""

    @pytest.fixture
    def queue_manager(self, temp_state_dir):
        """Create a queue manager instance for testing"""
        queue_file = os.path.join(temp_state_dir, "test_queue.json")
        return QueueManager(queue_file)

    def test_queue_initialization(self, queue_manager):
        """Test queue manager initialization"""
        assert queue_manager.main_queue == []
        assert queue_manager.overflow_queue == []
        assert queue_manager.team_size == 5
        assert queue_manager.queue_user == ""

    def test_add_player_to_empty_queue(self, queue_manager):
        """Test adding player to empty queue"""
        result = queue_manager.add_player("testuser", "player1")
        
        assert result["success"] is True
        assert "player1" in queue_manager.main_queue
        assert len(queue_manager.main_queue) == 1

    def test_add_player_to_full_queue(self, queue_manager):
        """Test adding player to full main queue (should go to overflow)"""
        # Fill main queue
        queue_manager.team_size = 2
        queue_manager.add_player("testuser", "player1")
        queue_manager.add_player("testuser", "player2")
        
        # Add third player (should go to overflow)
        result = queue_manager.add_player("testuser", "player3")
        
        assert result["success"] is True
        assert "player3" in queue_manager.overflow_queue
        assert len(queue_manager.main_queue) == 2

    def test_remove_player_from_queue(self, queue_manager):
        """Test removing player from queue"""
        # Add players
        queue_manager.add_player("testuser", "player1")
        queue_manager.add_player("testuser", "player2")
        
        # Remove player
        result = queue_manager.remove_player("testuser", "player1")
        
        assert result["success"] is True
        assert "player1" not in queue_manager.main_queue
        assert len(queue_manager.main_queue) == 1

    def test_remove_nonexistent_player(self, queue_manager):
        """Test removing player that's not in queue"""
        result = queue_manager.remove_player("testuser", "nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["message"].lower()

    def test_clear_queue(self, queue_manager):
        """Test clearing the queue"""
        # Add players
        queue_manager.add_player("testuser", "player1")
        queue_manager.add_player("testuser", "player2")
        
        # Clear queue
        result = queue_manager.clear_queue("testuser")
        
        assert result["success"] is True
        assert len(queue_manager.main_queue) == 0
        assert len(queue_manager.overflow_queue) == 0

    def test_set_team_size(self, queue_manager):
        """Test setting team size"""
        result = queue_manager.set_team_size("testuser", 10)
        
        assert result["success"] is True
        assert queue_manager.team_size == 10

    def test_set_invalid_team_size(self, queue_manager):
        """Test setting invalid team size"""
        result = queue_manager.set_team_size("testuser", 0)
        
        assert result["success"] is False
        assert "invalid" in result["message"].lower()

    def test_get_queue_status(self, queue_manager):
        """Test getting queue status"""
        # Add some players
        queue_manager.add_player("testuser", "player1")
        queue_manager.add_player("testuser", "player2")
        
        status = queue_manager.get_queue_status()
        
        assert "Main Queue" in status
        assert "player1" in status
        assert "player2" in status
        assert f"Team Size: {queue_manager.team_size}" in status

    def test_shuffle_queue(self, queue_manager):
        """Test shuffling the queue"""
        # Add multiple players
        players = ["player1", "player2", "player3", "player4", "player5"]
        for player in players:
            queue_manager.add_player("testuser", player)
        
        original_order = queue_manager.main_queue.copy()
        
        # Shuffle multiple times to ensure it actually shuffles
        shuffled = False
        for _ in range(10):
            result = queue_manager.shuffle_queue("testuser")
            if queue_manager.main_queue != original_order:
                shuffled = True
                break
        
        assert result["success"] is True
        # With 5 players, very unlikely to get same order after 10 shuffles
        assert shuffled is True

    def test_overflow_promotion(self, queue_manager):
        """Test that overflow players are promoted when main queue has space"""
        queue_manager.team_size = 2
        
        # Fill main queue and add to overflow
        queue_manager.add_player("testuser", "player1")
        queue_manager.add_player("testuser", "player2")
        queue_manager.add_player("testuser", "player3")  # Goes to overflow
        
        # Remove from main queue
        queue_manager.remove_player("testuser", "player1")
        
        # Check if overflow player was promoted
        assert "player3" in queue_manager.main_queue
        assert "player3" not in queue_manager.overflow_queue

    def test_save_and_load_state(self, queue_manager, temp_state_dir):
        """Test saving and loading queue state"""
        # Add some data
        queue_manager.add_player("testuser", "player1")
        queue_manager.set_team_size("testuser", 8)
        queue_manager.queue_user = "testuser"
        
        # Save state
        queue_manager.save_state()
        
        # Create new queue manager and load state
        new_queue_file = os.path.join(temp_state_dir, "test_queue.json")
        new_queue_manager = QueueManager(new_queue_file)
        
        # Check state was loaded
        assert "player1" in new_queue_manager.main_queue
        assert new_queue_manager.team_size == 8
        assert new_queue_manager.queue_user == "testuser"

    def test_unauthorized_operations(self, queue_manager):
        """Test that unauthorized users can't modify queue"""
        # Set queue user
        queue_manager.queue_user = "authorized_user"
        
        # Try to modify as different user
        result = queue_manager.add_player("unauthorized_user", "player1")
        
        assert result["success"] is False
        assert "authorized" in result["message"].lower() or "permission" in result["message"].lower()
