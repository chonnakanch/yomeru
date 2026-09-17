# Improvement Notes

## OCR Confidence Scoring

**Feature:** Add confidence scoring to OCR results for multi-region detection.

**Problem:** When capturing images with multiple speech bubbles, OCR doesn't extract text correctly. Single bubbles work well.

**Proposed Solution:** Heuristic-based confidence scoring (0.0-1.0) based on:
- Image aspect ratio (wide/thin images penalized)
- Whitespace borders (no border = likely cropped from larger image)
- Text density (too much text relative to image size)
- Japanese character ratio (noise detection)

**Implementation Notes:**
- manga-ocr doesn't return confidence scores natively
- Use PIL to analyze image characteristics
- Return `OCRResult(text, confidence)` instead of just `str`
- Frontend can display warning when confidence < 0.7

**Status:** Not implemented yet. Consider adding in future phases.

**Date:** 2026-09-17
