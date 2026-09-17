"""Translation service using deep-translator."""

from __future__ import annotations

import time

from deep_translator import GoogleTranslator
from deep_translator.exceptions import TooManyRequests


class TranslationError(Exception):
    """Raised when translation fails."""


class Translator:
    """Wrapper around deep-translator for Japanese-to-English translation."""

    def __init__(self, source: str = "ja", target: str = "en") -> None:
        self._source = source
        self._target = target
        self._translator = GoogleTranslator(source=source, target=target)

    def translate(self, text: str, max_retries: int = 3) -> str:
        """Translate text from source language to target language.

        Args:
            text: Text to translate.
            max_retries: Maximum number of retries on rate limit errors.

        Returns:
            Translated text.

        Raises:
            TranslationError: If translation fails after all retries.
        """
        if not text or not text.strip():
            return ""

        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                result = self._translator.translate(text)
                return result if result else ""
            except TooManyRequests:
                last_error = TooManyRequests("Rate limited by Google Translate")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
            except Exception as e:
                raise TranslationError(f"Translation failed: {e}") from e

        raise TranslationError(f"Translation failed after {max_retries} retries: {last_error}")


_translator_instance: Translator | None = None


def get_translator() -> Translator:
    """Get or create the singleton translator instance."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = Translator()
    return _translator_instance


def translate(text: str) -> str:
    """Convenience function to translate text using the singleton translator."""
    return get_translator().translate(text)
