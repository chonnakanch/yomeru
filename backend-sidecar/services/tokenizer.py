"""SudachiPy tokenizer service for Japanese morphological analysis."""

from __future__ import annotations

from dataclasses import dataclass

import sudachipy
from sudachipy import SplitMode


@dataclass(frozen=True)
class Token:
    """Represents a single morphological token from Japanese text."""

    surface: str
    lemma: str
    reading: str
    pos: str


class Tokenizer:
    """Wrapper around SudachiPy for Japanese tokenization."""

    def __init__(self) -> None:
        self._tokenizer = sudachipy.Dictionary().create()

    def tokenize(self, text: str) -> list[Token]:
        """Tokenize Japanese text into morphological components.

        Args:
            text: Raw Japanese text to tokenize.

        Returns:
            List of Token objects with surface, lemma, reading, and POS.
        """
        if not text or not text.strip():
            return []

        tokens: list[Token] = []
        for morpheme in self._tokenizer.tokenize(text, SplitMode.A):
            pos_parts = morpheme.part_of_speech()
            pos = pos_parts[0] if pos_parts else "UNKNOWN"

            reading = morpheme.reading_form()
            if reading:
                reading = reading.replace("　", "")

            tokens.append(
                Token(
                    surface=morpheme.surface(),
                    lemma=morpheme.normalized_form(),
                    reading=reading,
                    pos=pos,
                )
            )

        return tokens


_tokenizer_instance: Tokenizer | None = None


def get_tokenizer() -> Tokenizer:
    """Get or create the singleton tokenizer instance."""
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = Tokenizer()
    return _tokenizer_instance


def tokenize(text: str) -> list[Token]:
    """Convenience function to tokenize text using the singleton tokenizer."""
    return get_tokenizer().tokenize(text)
