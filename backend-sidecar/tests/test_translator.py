"""Unit tests for the translator service."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from services.translator import TranslationError, Translator


class TestTranslator:
    """Tests for deep-translator wrapper."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.translator = Translator()

    def test_translate_basic_text(self) -> None:
        """Test basic translation works with mocked API."""
        mock_translator = MagicMock()
        mock_translator.translate.return_value = "Hello"
        self.translator._translator = mock_translator

        result = self.translator.translate("こんにちは")
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == "Hello"

    def test_translate_empty_string(self) -> None:
        """Test translation of empty string returns empty string."""
        result = self.translator.translate("")
        assert result == ""

    def test_translate_whitespace_string(self) -> None:
        """Test translation of whitespace-only string returns empty string."""
        result = self.translator.translate("   ")
        assert result == ""

    @patch("services.translator.GoogleTranslator")
    def test_translate_api_error(self, mock_translator_class: MagicMock) -> None:
        """Test that API errors are wrapped in TranslationError."""
        mock_translator = MagicMock()
        mock_translator.translate.side_effect = Exception("API Error")
        mock_translator_class.return_value = mock_translator

        translator = Translator()
        with pytest.raises(TranslationError, match="Translation failed"):
            translator.translate("テスト")

    @patch("services.translator.GoogleTranslator")
    def test_translate_returns_result(self, mock_translator_class: MagicMock) -> None:
        """Test that translation returns the expected result."""
        mock_translator = MagicMock()
        mock_translator.translate.return_value = "Hello"
        mock_translator_class.return_value = mock_translator

        translator = Translator()
        result = translator.translate("こんにちは")
        assert result == "Hello"

    @patch("services.translator.GoogleTranslator")
    def test_translate_handles_none_result(
        self, mock_translator_class: MagicMock
    ) -> None:
        """Test that None result from API is handled gracefully."""
        mock_translator = MagicMock()
        mock_translator.translate.return_value = None
        mock_translator_class.return_value = mock_translator

        translator = Translator()
        result = translator.translate("テスト")
        assert result == ""
