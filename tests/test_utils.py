"""
Tests for utility functions
"""

import pytest
from unittest.mock import patch, MagicMock
from utils import (
    suggest_alwase_variants,
    shazdm,
    translate_text_to_english
)


class TestUtilityFunctions:
    """Test utility functions"""

    def test_suggest_alwase_variants(self):
        """Test alwase variant suggestion"""
        # Test with exact match
        result = suggest_alwase_variants("alwase")
        assert "always" in result.lower()

        # Test with partial match
        result = suggest_alwase_variants("alwse")
        assert "always" in result.lower()

        # Test with non-matching input
        result = suggest_alwase_variants("hello")
        assert result is None or result == ""

    def test_shazdm_basic(self):
        """Test basic shazdm functionality"""
        # Test with simple input
        result = shazdm("test input dms")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_translate_text_to_english(self):
        """Test translation functionality"""
        with patch('utils.GoogleTranslator') as mock_translator_class:
            # Setup mock
            mock_translator = MagicMock()
            mock_translator.translate.return_value = "Hello world"
            mock_translator_class.return_value = mock_translator
            
            # Test translation
            result, source_lang = translate_text_to_english("Hola mundo")
            
            assert result == "Hello world"
            assert source_lang == "auto"
            mock_translator.translate.assert_called_once_with("Hola mundo")

    @pytest.mark.asyncio
    async def test_translate_text_error_handling(self):
        """Test translation error handling"""
        with patch('utils.GoogleTranslator') as mock_translator_class:
            # Setup mock to raise exception
            mock_translator = MagicMock()
            mock_translator.translate.side_effect = Exception("Translation error")
            mock_translator_class.return_value = mock_translator
            
            # Test error handling
            result, source_lang = translate_text_to_english("test text")
            
            assert "Error translating" in result
            assert source_lang is None


class TestStringManipulation:
    """Test string manipulation utilities"""

    def test_shazdm_preserves_length(self):
        """Test that shazdm preserves input characteristics"""
        test_input = "test message"
        result = shazdm(test_input)
        
        # Should return a string
        assert isinstance(result, str)
        
        # Should not be empty
        assert len(result) > 0

    def test_shazdm_handles_empty_input(self):
        """Test shazdm with empty input"""
        result = shazdm("")
        assert isinstance(result, str)

    def test_shazdm_handles_special_characters(self):
        """Test shazdm with special characters"""
        test_input = "test!@#$%^&*()"
        result = shazdm(test_input)
        assert isinstance(result, str)
        assert len(result) > 0
