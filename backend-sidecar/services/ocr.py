"""OCR service using manga-ocr for Japanese text recognition."""

from __future__ import annotations

import base64
import io

from manga_ocr import MangaOcr
from PIL import Image


class OCRError(Exception):
    """Raised when OCR processing fails."""


class OCR:
    """Wrapper around manga-ocr for Japanese text recognition."""

    def __init__(self) -> None:
        self._ocr = MangaOcr()

    def recognize(self, image_data: bytes) -> str:
        """Recognize Japanese text from image bytes.

        Args:
            image_data: Raw image bytes (PNG, JPEG, etc.).

        Returns:
            Extracted Japanese text.

        Raises:
            OCRError: If image processing or OCR fails.
        """
        if not image_data:
            raise OCRError("Empty image data")

        try:
            image = Image.open(io.BytesIO(image_data))
            text = self._ocr(image)
            return text if text else ""
        except Exception as e:
            raise OCRError(f"OCR processing failed: {e}") from e

    def recognize_base64(self, base64_string: str) -> str:
        """Recognize Japanese text from a base64-encoded image.

        Args:
            base64_string: Base64-encoded image string.

        Returns:
            Extracted Japanese text.

        Raises:
            OCRError: If decoding or OCR fails.
        """
        if not base64_string:
            raise OCRError("Empty base64 string")

        try:
            image_data = base64.b64decode(base64_string)
            return self.recognize(image_data)
        except Exception as e:
            raise OCRError(f"Base64 OCR processing failed: {e}") from e


_ocr_instance: OCR | None = None


def get_ocr() -> OCR:
    """Get or create the singleton OCR instance."""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCR()
    return _ocr_instance


def recognize_image(image_data: bytes) -> str:
    """Convenience function to recognize text from image bytes."""
    return get_ocr().recognize(image_data)


def recognize_base64(base64_string: str) -> str:
    """Convenience function to recognize text from base64 string."""
    return get_ocr().recognize_base64(base64_string)
