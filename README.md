# Yomeru — Real-Time Manga & VN Overlay Translator

A cross-platform desktop application for translating Japanese manga and visual novels in real time. It renders a transparent screen overlay, supports interactive Japanese token lookups (readings, definitions, kanji breakdowns), and saves vocabulary to a local database and Anki.

## Tech Stack

- **Frontend Overlay:** Tauri v2 (Rust + React/TypeScript)
- **Backend ML Engine:** Python 3.13 + FastAPI
- **OCR:** [manga-ocr](https://github.com/kha-white/manga-ocr)
- **Tokenization:** [SudachiPy](https://github.com/WorksApplications/sudachi.rs) (SplitMode A)
- **Dictionary:** jamdict (offline) + Jisho REST API (online)
- **Translation:** deep-translator (Google Translate)

## Project Structure

```
yomeru/
├── plan.md                    # Master project specification
├── backend-sidecar/           # Python FastAPI ML Engine
│   ├── run.sh                 # Server launcher
│   ├── server.py              # FastAPI app & endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── services/
│   │   ├── ocr.py             # manga-ocr wrapper
│   │   ├── tokenizer.py       # SudachiPy parser
│   │   └── translator.py      # Translation client
│   └── tests/                 # Unit & integration tests
├── frontend/                  # React / TypeScript UI (Phase 2+)
└── src-tauri/                 # Tauri Rust core (Phase 2+)
```

## Quick Start (Phase 1 — Backend)

### Prerequisites

- Python 3.13 (`brew install python@3.13`)

### Setup

```bash
# Create virtual environment
python3.13 -m venv backend-sidecar/.venv

# Install dependencies
backend-sidecar/.venv/bin/pip install -r backend-sidecar/requirements.txt

# Run server
cd backend-sidecar
./run.sh
```

### Test Endpoints

```bash
# Health check
curl http://127.0.0.1:8000/health

# OpenAPI docs
open http://127.0.0.1:8000/docs
```

### Run Tests

```bash
backend-sidecar/.venv/bin/pytest backend-sidecar/tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status": "online"}` |
| `POST` | `/process-image` | Accepts `{image: "base64..."}`, returns `{raw_text, translated_text, tokens}` |
| `GET` | `/docs` | Interactive OpenAPI documentation |

## License

MIT
