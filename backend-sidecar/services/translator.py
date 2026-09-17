"""Translation service using deep-translator with fallback providers."""

from __future__ import annotations

import time

from deep_translator import GoogleTranslator, MyMemoryTranslator


class TranslationError(Exception):
    """Raised when translation fails."""


class Translator:
    """Translation with Google (primary) and MyMemory (fallback) providers."""

    def __init__(self, source: str = "ja", target: str = "en") -> None:
        self._source = source
        self._target = target
        self._google = GoogleTranslator(source=source, target=target)
        self._mymemory = MyMemoryTranslator(source="ja-JP", target="en-US")
        self._last_request_time: float = 0.0
        self._min_interval: float = 1.0

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def translate(self, text: str) -> str:
        """Translate text with automatic fallback on rate limit.

        Tries Google Translate first, falls back to MyMemory on 429.

        Args:
            text: Text to translate.

        Returns:
            Translated text.

        Raises:
            TranslationError: If all providers fail.
        """
        if not text or not text.strip():
            return ""

        # Try Google first
        try:
            self._rate_limit()
            result = self._google.translate(text)
            if result:
                return result
        except Exception:
            pass

        # Fallback to MyMemory
        try:
            self._rate_limit()
            result = self._mymemory.translate(text)
            return result if result else ""
        except Exception as e:
            raise TranslationError(f"Translation failed: {e}") from e


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
