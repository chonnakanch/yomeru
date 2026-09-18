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

---

## Click-through Toggle Button

**Feature:** Allow the overlay status icon to be clicked to toggle click-through mode.

**Problem:** Currently, the overlay uses `set_ignore_cursor_events(true)` which makes the entire window ignore all mouse events. This means the status icon cannot be clicked when click-through is ON. Users must rely on the keyboard shortcut (Option+T) or system tray icon to toggle.

**Proposed Solution:** Split the window into two layers or use a separate small always-clickable window for the toggle button:
- Main overlay window: handles click-through and selection
- Status button window: always interactive, never gets `set_ignore_cursor_events`

Alternative approaches:
- Use macOS Accessibility APIs to create a floating button above the overlay
- Use a system tray icon with a toggle menu item (already implemented as workaround)

**Implementation Notes:**
- Tauri v2's `set_ignore_cursor_events` is all-or-nothing per window
- A second always-interactive window could show the toggle button
- Need to sync state between both windows via events
- Consider using `WindowBuilder` to create a second small window at runtime

**Status:** Not implemented yet. System tray icon and keyboard shortcut are the current workaround.

**Date:** 2026-09-18
