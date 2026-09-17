# Project Plan: Yomeru (Real-Time Manga & VN Overlay Translator)

Yomeru is a cross-platform desktop application (Windows & macOS) designed for translating Japanese manga and visual novels in real time. It renders a transparent screen overlay, supports interactive Japanese token lookups (readings, definitions, kanji breakdowns), and saves vocabulary to a local database and Anki.

---

## 1. System Architecture & Tech Stack

* **Frontend Overlay:** Tauri v2 (Rust + React/TypeScript)
  * Window management: Frameless, transparent, always-on-top, dynamic click-through toggling.
  * Canvas rendering: Bounding boxes, translated text overlays, interactive Japanese word chips, and hover dictionary popups.
* **Backend ML Engine (Sidecar):** Python 3.11 + FastAPI
  * OCR: `manga-ocr` (tuned for Japanese vertical/horizontal text)
  * Tokenization: `SudachiPy` (SplitMode A) for morphological analysis
  * Dictionary Lookups: `jamdict` (Offline) + Jisho REST API (Online fallback)
  * Translation: `deep-translator` (Google Translate / DeepL API)
* **Storage:** SQLite (local vocabulary store) + `genanki` / `AnkiConnect`

---

## 2. AI Agent Execution Rules & Guidelines

When implementing code for **Yomeru**, strictly adhere to these principles:

1. **Modular Decoupling:** Keep the Python sidecar completely decoupled from the Tauri frontend. All communication must occur strictly over HTTP/REST payloads.
2. **Fail Fast & Fallback:** If `manga-ocr` or `SudachiPy` fails on a frame, return structured JSON error payloads instead of letting the FastAPI process crash.
3. **Non-Blocking UI:** Never perform synchronous image processing or network requests on the main UI thread. All API calls to the sidecar must be asynchronous (`async/await`).
4. **Mocking for Development:** Provide mock JSON payloads for the sidecar endpoints so frontend UI components can be developed and tested without waiting for PyTorch/OCR model loading times.
5. **Incremental Execution:** Build and verify each MVP step completely before proceeding to the next layer.

---

## 3. Project Directory Structure

```text
yomeru/
├── plan.md                    # This master project specification
├── src-tauri/                 # Tauri Rust core & application config
│   ├── binaries/              # Target-triple compiled sidecar executables
│   ├── src/                   # Native Rust commands (window control, click-through)
│   └── tauri.conf.json        # Tauri configuration (transparent overlay, sidecars)
├── frontend/                  # React / TypeScript UI
│   ├── src/
│   │   ├── components/        # Overlay canvas, WordChip, DictionaryPopup, Toolbar
│   │   ├── services/          # API client for Python sidecar
│   │   └── App.tsx            # Main canvas container
│   └── package.json
├── backend-sidecar/           # Python FastAPI ML Engine
│   ├── server.py              # Main FastAPI application & lifecycle
│   ├── services/
│   │   ├── ocr.py             # manga-ocr execution wrapper
│   │   ├── tokenizer.py       # SudachiPy parser
│   │   ├── translator.py      # Translation client
│   │   └── dictionary.py      # Jamdict/Jisho lookup handlers
│   └── requirements.txt
└── README.md