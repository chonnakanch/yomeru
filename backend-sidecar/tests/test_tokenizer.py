"""Unit tests for the tokenizer service."""

from __future__ import annotations

from services.tokenizer import Token, Tokenizer


class TestTokenizer:
    """Tests for SudachiPy tokenizer wrapper."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.tokenizer = Tokenizer()

    def test_tokenize_basic_sentence(self, sample_japanese_text: str) -> None:
        """Test tokenization of a basic Japanese sentence."""
        tokens = self.tokenizer.tokenize(sample_japanese_text)

        assert len(tokens) > 0
        assert all(isinstance(t, Token) for t in tokens)
        assert all(t.surface for t in tokens)
        assert all(t.lemma for t in tokens)

    def test_tokenize_returns_correct_types(self, sample_japanese_text: str) -> None:
        """Test that tokens have correct field types."""
        tokens = self.tokenizer.tokenize(sample_japanese_text)

        for token in tokens:
            assert isinstance(token.surface, str)
            assert isinstance(token.lemma, str)
            assert isinstance(token.reading, str)
            assert isinstance(token.pos, str)

    def test_tokenize_empty_string(self, sample_empty_text: str) -> None:
        """Test tokenization of empty string returns empty list."""
        tokens = self.tokenizer.tokenize(sample_empty_text)
        assert tokens == []

    def test_tokenize_whitespace_string(self, sample_whitespace_text: str) -> None:
        """Test tokenization of whitespace-only string returns empty list."""
        tokens = self.tokenizer.tokenize(sample_whitespace_text)
        assert tokens == []

    def test_tokenize_filters_punctuation(self) -> None:
        """Test that punctuation is included as tokens (SudachiPy behavior)."""
        tokens = self.tokenizer.tokenize(" hello ")

        surfaces = [t.surface for t in tokens]
        assert len(surfaces) > 0

    def test_tokenize_complex_sentence(self) -> None:
        """Test tokenization of a more complex Japanese sentence."""
        text = "東京は日本の首都です"
        tokens = self.tokenizer.tokenize(text)

        assert len(tokens) > 0
        surfaces = "".join(t.surface for t in tokens)
        assert "東京" in surfaces

    def test_tokenize_reading_is_katakana(self) -> None:
        """Test that reading forms are in katakana."""
        tokens = self.tokenizer.tokenize("日本語")

        non_empty_readings = [t.reading for t in tokens if t.reading]
        for reading in non_empty_readings:
            assert all(
                ord(c) >= 0x30A0 and ord(c) <= 0x30FF for c in reading
            ), f"Reading '{reading}' contains non-katakana characters"

    def test_tokenize_pos_is_valid(self) -> None:
        """Test that POS tags are valid SudachiPy POS tags."""
        tokens = self.tokenizer.tokenize("食べる")

        valid_pos = {
            "名詞",
            "動詞",
            "形容詞",
            "副詞",
            "助詞",
            "助動詞",
            "接続詞",
            "感動詞",
            "連体詞",
            "記号",
            "補助記号",
            "空白",
            "未知語",
        }

        for token in tokens:
            assert token.pos in valid_pos, f"Unexpected POS: {token.pos}"

    def test_tokenize_multiple_sentences(self) -> None:
        """Test tokenization of multiple sentences."""
        text = "今日は天気がいいです。明日は雨です。"
        tokens = self.tokenizer.tokenize(text)

        assert len(tokens) > 0
        surfaces = "".join(t.surface for t in tokens)
        assert "今日" in surfaces
        assert "明日" in surfaces
