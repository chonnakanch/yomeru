"""Translation service using deep-translator."""

from __future__ import annotations

from deep_translator import GoogleTranslator


class TranslationError(Exception):
    """Raised when translation fails."""


class Translator:
    """Wrapper around deep-translator for Japanese-to-English translation."""

    def __init__(self, source: str = "ja", target: str = "en") -> None:
        self._source = source
        self._target = target

    def translate(self, text: str) -> str:
        """Translate text from source language to target language.

        Args:
            text: Text to translate.

        Returns:
            Translated text.

        Raises:
            TranslationError: If translation fails.
        """
        if not text or not text.strip():
            return ""

        try:
            translator = GoogleTranslator(source=self._source, target=self._target)
            result = translator.translate(text)
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
