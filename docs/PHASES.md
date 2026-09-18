# Yomeru: Comprehensive Implementation Phases

This document contains the step-by-step master plan for building **Yomeru**. An executing AI agent must complete each phase sequentially, including unit and integration tests, before proceeding to the next.

---

## Phase 1: Python ML Sidecar API

### 1. Objective
Establish an independent local FastAPI server that processes cropped manga images and returns extracted Japanese text, sentence translations, and tokenized word components.

### 2. Deliverables & Directory Requirements
* **Directory Structure:**
  * `backend-sidecar/server.py`
  * `backend-sidecar/requirements.txt`
  * `backend-sidecar/services/ocr.py`
  * `backend-sidecar/services/tokenizer.py`
  * `backend-sidecar/services/translator.py`

### 3. Core Tasks
* [ ] Set up Python virtual environment and dependencies (`fastapi`, `uvicorn`, `manga-ocr`, `sudachipy`, `sudachidict_core`, `pillow`, `pydantic`, `deep-translator`).
* [ ] Implement OCR service wrapper around `manga-ocr`.
* [ ] Implement tokenization service using `SudachiPy` (SplitMode A) to extract surface form, lemma (dictionary form), reading (katakana), and part of speech.
* [ ] Implement translation service using `deep-translator` (Google Translate fallback, optional DeepL API support).
* [ ] Implement `/health` REST endpoint returning status.
* [ ] Implement `POST /process-image` endpoint receiving base64 image strings and returning structured JSON (`raw_text`, `translated_text`, `tokens`).

### 4. Required Tests
* **Unit Tests:**
  * Test OCR image loading and conversion logic.
  * Test SudachiPy tokenization against sample Japanese sentences (verify symbol filtering and katakana reading extraction).
  * Test translation service handling of empty strings and API exceptions.
* **Integration Tests:**
  * Test FastAPI endpoints using `fastapi.testclient.TestClient`.
  * Validate JSON response schema for `POST /process-image` using a mock image input.

### 5. Phase Verification
* Start server (`uvicorn`) and confirm `http://127.0.0.1:8000/health` returns `{"status": "online"}`.
* Send sample payload via OpenAPI docs (`http://127.0.0.1:8000/docs`) and verify response payload structure.

---

## Phase 2: Tauri Transparent Canvas & Screen Capture

### 1. Objective
Build a transparent, frameless, desktop-first overlay app in Tauri v2 that sits on top of all desktop applications, toggles click-through capabilities, and captures screen regions via hotkeys.

### 2. Deliverables & Directory Requirements
* **Directory Structure:**
  * `src-tauri/tauri.conf.json`
  * `src-tauri/Cargo.toml`
  * `src-tauri/src/lib.rs`
  * `frontend/src/App.tsx`
  * `frontend/src/components/SelectionCanvas.tsx`

### 3. Core Tasks
* [x] Initialize Tauri v2 project with React/TypeScript frontend (Vite + React + TypeScript).
* [x] Configure window flags in `tauri.conf.json` (`transparent: true`, `decorations: false`, `alwaysOnTop: true`, `skipTaskbar: true`, `macOSPrivateApi: true`).
* [x] Implement Rust commands `set_click_through(ignore: bool)` and `toggle_click_through` via native cursor event handlers.
* [x] Register global hotkey shortcut (`Option+T` / `Alt+T`) using `tauri-plugin-global-shortcut`.
* [x] Create system tray icon with toggle menu and quit option.
* [x] Create selection bounding-box component in React allowing users to drag and select a screen region.
* [x] Crop selected region and convert screen area into a base64 image string.
* [x] Auto-detect primary monitor size and position window to cover full screen at startup.
* [x] Apply click-through mode on startup.
* [x] Emit `click-through-changed` event to sync frontend state with Rust backend.

### 4. Required Tests
* **Unit Tests:**
  * Test React canvas selection logic (bounding box coordinate calculations, width/height validations).
  * Test hotkey label detection (macOS vs other platforms).
* **Integration Tests:**
  * Test status indicator rendering in click-through mode.
  * Test that Tauri event listener is registered for state sync.
  * Test base64 conversion utilities.

### 5. Phase Verification
* Run `cargo tauri dev`.
* Confirm window sits transparently on top of open applications.
* Confirm status icon appears at bottom-right corner of full screen.
* Press `Option+T` to toggle between click-through and selection modes.
* Verify system tray icon appears with toggle menu.
* Drag selection box and verify base64 image capture (console output).

---

## Phase 3: Translation Overlay Rendering

### 1. Objective
Connect the Tauri frontend to the local Python sidecar API to display translated speech bubbles directly over the captured screen region.

### 2. Deliverables & Directory Requirements
* **Directory Structure:**
  * `frontend/src/services/api.ts`
  * `frontend/src/components/TranslatedBox.tsx`
  * `frontend/src/components/ModeToolbar.tsx`

### 3. Core Tasks
* [ ] Create HTTP service layer in frontend to communicate with `http://127.0.0.1:8000/process-image`.
* [ ] Build `TranslatedBox` overlay component that positions a translucent card over the exact screen coordinates of the captured speech bubble.
* [ ] Implement state management for processing states (Idle, Capturing, Loading/OCR, Rendered).
* [ ] Build mode switcher control:
  * **Translated Mode:** Displays target translation.
  * **Original Mode:** Displays raw Japanese text.
  * **Hidden Mode:** Makes overlay invisible and enables click-through.

### 4. Required Tests
* **Unit Tests:**
  * Test API client error handling (timeout, backend offline, bad response).
  * Test `TranslatedBox` coordinate positioning logic.
* **Integration Tests:**
  * Mock sidecar API responses and test full UI flow from capture trigger to overlay box rendering.

### 5. Phase Verification
* Drag-select Japanese text on screen with backend running.
* Verify loading state displays, followed by translated text box rendered precisely over the selected area.
* Test switching between Translated, Original, and Hidden modes.

---

## Phase 4: Interactive Word Tokens & Dictionary Popups

### 1. Objective
Transform original text overlays into interactive learning elements by rendering individual clickable Japanese word tokens with hover/click dictionary popups.

### 2. Deliverables & Directory Requirements
* **Directory Structure:**
  * `backend-sidecar/services/dictionary.py`
  * `frontend/src/components/WordChip.tsx`
  * `frontend/src/components/DictionaryPopup.tsx`

### 3. Core Tasks
* [ ] Integrate `jamdict` (offline) and Jisho REST API (online) into `backend-sidecar/services/dictionary.py`.
* [ ] Add `/dictionary-lookup` endpoint to sidecar accepting word lemmas and returning definitions, furigana readings, and JLPT levels.
* [ ] Create `WordChip` React component that renders individual SudachiPy tokens as interactive elements with furigana rendered above Kanji.
* [ ] Create `DictionaryPopup` component that opens on hover or click to display complete word details.

### 4. Required Tests
* **Unit Tests:**
  * Test `dictionary.py` offline lookup and online fallback behavior.
  * Test `WordChip` rendering logic with various Japanese parts of speech.
* **Integration Tests:**
  * Test endpoint `GET /dictionary-lookup?word=...`.
  * Test UI integration: clicking a `WordChip` fetches dictionary data and positions popup correctly.

### 5. Phase Verification
* Switch overlay to Original Japanese Mode.
* Hover or click on individual Japanese word tokens.
* Confirm popup appears instantly showing base dictionary forms, furigana, English definitions, and JLPT tags.

---

## Phase 5: Vocabulary Storage & Anki Sync

### 1. Objective
Allow users to save looked-up words, sentence context, readings, and image snapshots to a local database and export or sync them with Anki.

### 2. Deliverables & Directory Requirements
* **Directory Structure:**
  * `backend-sidecar/services/storage.py`
  * `backend-sidecar/services/anki.py`
  * `frontend/src/components/VocabBook.tsx`

### 3. Core Tasks
* [ ] Implement SQLite database initialization in sidecar (`yomeru_vocab.db`) with a `vocab_cards` schema.
* [ ] Create `/save-word` endpoint to store card data (word, reading, definition, sentence context, snapshot image).
* [ ] Add "Add to Vocab Book" button inside `DictionaryPopup`.
* [ ] Implement Anki export service using `AnkiConnect` HTTP API or `.apkg` file generator (`genanki`).
* [ ] Create simple Vocabulary Manager view in frontend to review saved words.

### 4. Required Tests
* **Unit Tests:**
  * Test SQLite Data Access Object (DAO) CRUD operations.
  * Test Anki payload formatter functions.
* **Integration Tests:**
  * Test `/save-word` endpoint writing to SQLite database.
  * Test mock connection to `AnkiConnect` endpoint.

### 5. Phase Verification
* Click "Add to Vocab Book" on a word popup.
* Open SQLite database or Vocabulary Manager UI to verify card, furigana, context sentence, and image snapshot were saved.
* Test card sync/export to Anki.

---

## Phase 6: Sidecar Packaging & Production Distribution

### 1. Objective
Package the Python sidecar into a standalone binary executable and bundle the entire application into native installers for Windows (`.msi`) and macOS (`.dmg`).

### 2. Deliverables & Directory Requirements
* **Directory Structure:**
  * `backend-sidecar/MangaBackend.spec`
  * `src-tauri/binaries/manga_backend-[target-triple]`

### 3. Core Tasks
* [ ] Configure `PyInstaller` spec file to freeze Python FastAPI backend and dependencies (`manga-ocr`, `SudachiPy` dictionaries) into an executable folder/binary.
* [ ] Compile executable and copy to `src-tauri/binaries/` named according to Rust target triples (e.g., `manga_backend-x86_64-pc-windows-msvc.exe` or `manga_backend-aarch64-apple-darwin`).
* [ ] Configure `tauri.conf.json` `externalBin` field to declare the sidecar binary.
* [ ] Update `src-tauri/src/lib.rs` to spawn sidecar process on startup and manage lifecycle on exit.
* [ ] Run `npm run tauri build` to generate standalone installers.

### 4. Required Tests
* **Unit Tests:**
  * Test Rust sidecar spawn lifecycle handlers.
* **Integration Tests:**
  * Test application startup sequence: verify frontend waits for sidecar `/health` ping before rendering UI.

### 5. Phase Verification
* Run produced `.msi` or `.dmg` installer on a target computer that does **not** have Python installed.
* Launch application, verify background sidecar starts automatically, and perform full capture-to-translation workflow.