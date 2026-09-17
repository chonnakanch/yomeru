"""OCR service using manga-ocr for Japanese text recognition with confidence scoring."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass

from manga_ocr import MangaOcr
from PIL import Image


class OCRError(Exception):
    """Raised when OCR processing fails."""


@dataclass(frozen=True)
class OCRResult:
    """Result from OCR processing with confidence score."""

    text: str
    confidence: float  # 0.0 to 1.0


class OCR:
    """Wrapper around manga-ocr for Japanese text recognition with confidence scoring."""

    def __init__(self) -> None:
        self._ocr = MangaOcr()

    def _calculate_confidence(self, image: Image.Image, text: str) -> float:
        """Calculate confidence score based on image characteristics and OCR result.

        Scoring factors:
        - Image aspect ratio (single bubbles are typically 0.3-0.7)
        - Whitespace border presence (isolated bubbles have clear borders)
        - Text density (text length vs image area)
        - Character composition (Japanese chars vs noise)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not text:
            return 0.0

        score = 1.0

        # 1. Aspect ratio penalty (extreme ratios suggest multi-region)
        width, height = image.size
        aspect = min(width, height) / max(width, height) if max(width, height) > 0 else 0
        if aspect < 0.2:  # Very thin/wide = likely multiple regions
            score *= 0.5
        elif aspect < 0.3:
            score *= 0.7

        # 2. Whitespace border detection
        gray = image.convert("L")
        pixels = list(gray.get_flattened_data())
        total_pixels = len(pixels)

        if total_pixels > 0:
            # Check border pixels (top/bottom rows, left/right columns)
            border_pixels = []
            for x in range(width):
                border_pixels.append(pixels[x])  # Top row
                border_pixels.append(pixels[(height - 1) * width + x])  # Bottom row
            for y in range(height):
                border_pixels.append(pixels[y * width])  # Left column
                border_pixels.append(pixels[y * width + (width - 1)])  # Right column

            white_threshold = 240
            border_whiteness = sum(1 for p in border_pixels if p > white_threshold) / len(border_pixels)

            if border_whiteness < 0.3:  # No white border = likely cropped from larger image
                score *= 0.6

        # 3. Text density (too much text relative to image size = likely multi-region)
        char_count = len(text)
        pixel_density = char_count / (width * height) if (width * height) > 0 else 0
        if pixel_density > 0.01:  # Very dense text
            score *= 0.7

        # 4. Character composition (noise indicators)
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u9fff' or '\u30a0' <= c <= '\u30ff')
        total_chars = len(text.replace(" ", ""))
        if total_chars > 0:
            jp_ratio = japanese_chars / total_chars
            if jp_ratio < 0.5:  # Less than 50% Japanese characters = likely noise
                score *= 0.6

        # 5. Minimum text length bonus (single words are usually correct)
        if 1 <= char_count <= 20:
            score *= 1.0  # No penalty
        elif char_count > 50:
            score *= 0.8  # Long text = more likely multi-region

        return max(0.0, min(1.0, score))

    def recognize(self, image_data: bytes) -> OCRResult:
        """Recognize Japanese text from image bytes with confidence score.

        Args:
            image_data: Raw image bytes (PNG, JPEG, etc.).

        Returns:
            OCRResult with text and confidence score.

        Raises:
            OCRError: If image processing or OCR fails.
        """
        if not image_data:
            raise OCRError("Empty image data")

        try:
            image = Image.open(io.BytesIO(image_data))
            text = self._ocr(image)
            text = text if text else ""
            confidence = self._calculate_confidence(image, text)
            return OCRResult(text=text, confidence=confidence)
        except Exception as e:
            raise OCRError(f"OCR processing failed: {e}") from e

    def recognize_base64(self, base64_string: str) -> OCRResult:
        """Recognize Japanese text from a base64-encoded image with confidence score.

        Args:
            base64_string: Base64-encoded image string.

        Returns:
            OCRResult with text and confidence score.

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


def recognize_image(image_data: bytes) -> OCRResult:
    """Convenience function to recognize text from image bytes."""
    return get_ocr().recognize(image_data)


def recognize_base64(base64_string: str) -> OCRResult:
    """Convenience function to recognize text from base64 string."""
    return get_ocr().recognize_base64(base64_string)
