# Image-to-Label Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an app that converts product images into Dutch labels formatted for a Brother QL810W printer (62mm).

**Architecture:** Streamlit frontend (3 pages), FastAPI/Python backend logic, Ollama (gemma4:31b-cloud) for AI, SQLite for history, and win32print for hardware interfacing.

**Tech Stack:** Python 3.10+, Streamlit, FastAPI, Ollama, SQLAlchemy, pywin32.

---

### File Structure
- `app.py`: Main Streamlit app and page routing.
- `engine/ai_processor.py`: OCR, translation, and smart attribute mapping.
- `engine/formatter.py`: Logic to transform structured data into Brother 62mm text layout.
- `engine/printer.py`: Win32Print wrapper for QL810W.
- `database/db_manager.py`: SQLite schema and operations.
- `requirements.txt`: Project dependencies.

---

### Task 1: Project Setup & Dependencies
**Files:** `requirements.txt`
- [ ] **Step 1: Create `requirements.txt`** including `streamlit`, `fastapi`, `uvicorn`, `pywin32`, `sqlalchemy`, `requests`.
- [ ] **Step 2: Install dependencies** via pip.
- [ ] **Step 3: Commit.**

### Task 2: AI Intelligence Engine
**Files:** `engine/ai_processor.py`, `tests/test_ai_processor.py`
- [ ] **Step 1: Implement `extract_product_data(image_path)`**. Interface with Ollama to extract text and translate to Dutch.
- [ ] **Step 2: Implement "Smart Mapping"**. Logic to detect category (Liters/KG) and prune missing fields to avoid empty spaces.
- [ ] **Step 3: Create failing test** for translation and field pruning.
- [ ] **Step 4: Implement minimal code to make test pass**.
- [ ] **Step 5: Run test and verify PASS**.
- [ ] **Step 6: Commit.**

### Task 3: Label Formatter (62mm Layout)
**Files:** `engine/formatter.py`, `tests/test_formatter.py`
- [ ] **Step 1: Implement `generate_label_text(data)`**. Match the visual structure of `SampleLabelFormat.txt`.
- [ ] **Step 2: Implement Dynamic Height Logic**. Ensure sections collapse if data is missing.
- [ ] **Step 3: Create test** comparing output against a known valid label string.
- [ ] **Step 4: Run test and verify PASS**.
- [ ] **Step 5: Commit.**

### Task 4: Local Storage (SQLite)
**Files:** `database/db_manager.py`
- [ ] **Step 1: Define `Label` model** with SQLAlchemy (id, original_image, dutch_content, formatted_text, created_at).
- [ ] **Step 2: Implement `save_label()` and `get_history()`**.
- [ ] **Step 3: Test database insertion and retrieval**.
- [ ] **Step 4: Commit.**

### Task 5: UI Page 1 - Image Upload
**Files:** `app.py`
- [ ] **Step 1: Implement `st.file_uploader`** and basic page routing.
- [ ] **Step 2: Integrate `ai_processor.py`** to trigger extraction on upload.
- [ ] **Step 3: Store result in `st.session_state`**.
- [ ] **Step 4: Commit.**

### Task 6: UI Page 2 - Review & Edit
**Files:** `app.py`
- [ ] **Step 1: Implement editable form** for all translated Dutch fields.
- [ ] **Step 2: Implement "Live Preview"** calling `formatter.py` on every edit.
- [ ] **Step 3: Implement "Save" button** via `db_manager.py`.
- [ ] **Step 4: Commit.**

### Task 7: UI Page 3 - Printing
**Files:** `app.py`, `engine/printer.py`
- [ ] **Step 1: Implement `get_installed_printers()`** using `win32print`.
- [ ] **Step 2: Implement `print_label(text, printer, copies)`** using `win32print.StartDocPrinter`.
- [ ] **Step 3: Implement UI** for copies count, printer selection, and the "Print" trigger.
- [ ] **Step 4: End-to-end test** (dry run to printer).
- [ ] **Step 5: Final Commit.**
