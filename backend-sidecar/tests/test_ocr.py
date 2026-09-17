"""Unit tests for the OCR service."""

from __future__ import annotations

import base64
import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from services.ocr import OCR, OCRError


class TestOCR:
    """Tests for manga-ocr wrapper."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.ocr = OCR()

    def test_recognize_with_valid_image(self) -> None:
        """Test OCR recognition with a valid image."""
        img = Image.new("RGB", (100, 50), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        result = self.ocr.recognize(img_bytes.read())
        assert isinstance(result, str)

    def test_recognize_empty_bytes_raises_error(self) -> None:
        """Test that empty bytes raises OCRError."""
        with pytest.raises(OCRError, match="Empty image data"):
            self.ocr.recognize(b"")

    def test_recognize_base64_empty_string_raises_error(self) -> None:
        """Test that empty base64 string raises OCRError."""
        with pytest.raises(OCRError, match="Empty base64 string"):
            self.ocr.recognize_base64("")

    def test_recognize_base64_with_valid_image(self) -> None:
        """Test OCR recognition with a valid base64 image."""
        img = Image.new("RGB", (100, 50), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        base64_string = base64.b64encode(img_bytes.read()).decode("utf-8")
        result = self.ocr.recognize_base64(base64_string)
        assert isinstance(result, str)

    def test_recognize_base64_invalid_data_raises_error(self) -> None:
        """Test that invalid base64 data raises OCRError."""
        with pytest.raises(OCRError, match="Base64 OCR processing failed"):
            self.ocr.recognize_base64("not-valid-base64")

    @patch("services.ocr.MangaOcr")
    def test_recognize_handles_ocr_failure(
        self, mock_manga_ocr_class: MagicMock
    ) -> None:
        """Test that OCR failures are wrapped in OCRError."""
        mock_ocr = MagicMock()
        mock_ocr.side_effect = Exception("OCR Model Error")
        mock_manga_ocr_class.return_value = mock_ocr

        ocr = OCR()
        img = Image.new("RGB", (100, 50), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with pytest.raises(OCRError, match="OCR processing failed"):
            ocr.recognize(img_bytes.read())

    @patch("services.ocr.MangaOcr")
    def test_recognize_returns_empty_string(
        self, mock_manga_ocr_class: MagicMock
    ) -> None:
        """Test that empty OCR result is handled gracefully."""
        mock_ocr = MagicMock()
        mock_ocr.return_value = ""
        mock_manga_ocr_class.return_value = mock_ocr

        ocr = OCR()
        img = Image.new("RGB", (100, 50), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        result = ocr.recognize(img_bytes.read())
        assert result == ""
