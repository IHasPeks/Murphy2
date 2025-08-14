"""
Tests for command handling functionality
"""

import pytest
from unittest.mock import AsyncMock, patch
from commands import (
    handle_penta,
    handle_quadra,
    handle_cannon,
    command_counters
)
from constants import Messages


class TestCommandHandling:
    """Test command handling functions"""

    @pytest.mark.asyncio
    async def test_handle_penta(self, mock_message):
        """Test penta command increments counter"""
        # Reset counter
        command_counters.counters['penta'] = 0
        
        await handle_penta(mock_message, "")
        
        assert command_counters.get('penta') == 1
        mock_message.channel.send.assert_called_once()
        call_args = mock_message.channel.send.call_args[0][0]
        assert "1" in call_args  # Check counter is in message

    @pytest.mark.asyncio
    async def test_handle_quadra(self, mock_message):
        """Test quadra command increments counter"""
        # Reset counter
        command_counters.counters['quadra'] = 0
        
        await handle_quadra(mock_message, "")
        
        assert command_counters.get('quadra') == 1
        mock_message.channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_cannon(self, mock_message):
        """Test cannon command increments counter"""
        # Reset counter
        command_counters.counters['cannon'] = 0
        
        await handle_cannon(mock_message, "")
        
        assert command_counters.get('cannon') == 1
        mock_message.channel.send.assert_called_once()

    # Legacy router no longer exposed directly; routing handled in bot layer.


class TestCommandCounters:
    """Test command counter functionality"""

    def test_increment_existing_command(self):
        """Test incrementing existing command counter"""
        command_counters.counters['cannon'] = 10
        result = command_counters.increment('cannon')
        assert result == 11
        assert command_counters.get('cannon') == 11

    def test_increment_nonexistent_command(self):
        """Test incrementing non-existent command counter"""
        result = command_counters.increment('nonexistent')
        assert result == 0

    def test_get_existing_counter(self):
        """Test getting existing counter value"""
        command_counters.counters['quadra'] = 42
        assert command_counters.get('quadra') == 42

    def test_get_nonexistent_counter(self):
        """Test getting non-existent counter value"""
        assert command_counters.get('nonexistent') == 0

    def test_set_all_counters(self):
        """Test setting all counter values"""
        command_counters.set_all(cannon=5, quadra=10, penta=15)
        
        assert command_counters.get('cannon') == 5
        assert command_counters.get('quadra') == 10
        assert command_counters.get('penta') == 15
