"""Unit tests for the translator service."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from services.translator import TranslationError, Translator


class TestTranslator:
    """Tests for translation service with fallback providers."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.translator = Translator()

    def test_translate_basic_text(self) -> None:
        """Test basic translation works with mocked API."""
        self.translator._google = MagicMock()
        self.translator._google.translate.return_value = "Hello"

        result = self.translator.translate("こんにちは")
        assert result == "Hello"

    def test_translate_empty_string(self) -> None:
        """Test translation of empty string returns empty string."""
        result = self.translator.translate("")
        assert result == ""

    def test_translate_whitespace_string(self) -> None:
        """Test translation of whitespace-only string returns empty string."""
        result = self.translator.translate("   ")
        assert result == ""

    def test_translate_falls_back_to_mymemory(self) -> None:
        """Test that MyMemory is used when Google fails."""
        self.translator._google = MagicMock()
        self.translator._google.translate.side_effect = Exception("Rate limited")
        self.translator._mymemory = MagicMock()
        self.translator._mymemory.translate.return_value = "Hello from MyMemory"

        result = self.translator.translate("こんにちは")
        assert result == "Hello from MyMemory"

    def test_translate_all_providers_fail(self) -> None:
        """Test error when all providers fail."""
        self.translator._google = MagicMock()
        self.translator._google.translate.side_effect = Exception("Google error")
        self.translator._mymemory = MagicMock()
        self.translator._mymemory.translate.side_effect = Exception("MyMemory error")

        with pytest.raises(TranslationError, match="Translation failed"):
            self.translator.translate("テスト")

    def test_translate_returns_result(self) -> None:
        """Test that translation returns the expected result."""
        self.translator._google = MagicMock()
        self.translator._google.translate.return_value = "Hello"

        result = self.translator.translate("こんにちは")
        assert result == "Hello"

    def test_translate_handles_none_result(self) -> None:
        """Test that None result from API is handled gracefully."""
        self.translator._google = MagicMock()
        self.translator._google.translate.return_value = None
        self.translator._mymemory = MagicMock()
        self.translator._mymemory.translate.return_value = "Fallback"

        result = self.translator.translate("テスト")
        assert result == "Fallback"
