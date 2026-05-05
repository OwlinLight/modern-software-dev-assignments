# Week 2: Action Item Extractor

## Overview
This project is a small FastAPI application that turns free-form notes into stored action items. It includes:

- A heuristic extractor for bullet points, checkboxes, and simple imperative sentences
- An optional LLM-powered extractor backed by Ollama
- A SQLite persistence layer for notes and action items
- A minimal HTML frontend for extracting tasks, marking them done, and listing saved notes

The API and frontend are served by the same FastAPI app. Notes are stored in a local SQLite database at `week2/data/app.db`.

## Project Structure
- `week2/app/main.py`: FastAPI app entrypoint and frontend route
- `week2/app/routers/`: API endpoints for notes and action items
- `week2/app/services/extract.py`: heuristic and Ollama-based extraction logic
- `week2/app/db.py`: SQLite schema and data access helpers
- `week2/frontend/index.html`: minimal browser UI
- `week2/tests/`: pytest-based test suite

## Setup
This repository uses Poetry at the repo root.

### 1. Install dependencies
From the repository root:

```bash
poetry install
```

### 2. Optional: install and run Ollama
The `/action-items/extract/llm` endpoint requires Ollama and the `llama3.1:8b` model used in `week2/app/services/extract.py`.

Example setup:

```bash
ollama run llama3.1:8b
```

If Ollama is not running, the LLM endpoint will return `503 Model service unavailable`.

## Running the Project
Start the FastAPI server from the repository root:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Then open:

- App UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Frontend Functionality
The browser UI supports three main actions:

- `Extract (rules)`: extracts action items using the heuristic parser
- `Extract (LLM)`: extracts action items using Ollama
- `List Notes`: fetches and displays all saved notes

When extracted items are displayed, checking a box marks the stored action item as done through the API.

## API Endpoints

### `GET /`
Serves the HTML frontend.

### `POST /notes`
Creates a note.

Request body:

```json
{
  "content": "Discuss roadmap and write follow-up email"
}
```

Response:

```json
{
  "id": 1,
  "content": "Discuss roadmap and write follow-up email",
  "created_at": "2026-05-05 15:30:00"
}
```

### `GET /notes`
Returns all saved notes, ordered newest first.

Response:

```json
[
  {
    "id": 2,
    "content": "Second note",
    "created_at": "2026-05-05 15:35:00"
  }
]
```

### `GET /notes/{note_id}`
Returns a single note by ID.

- Returns `404` if the note does not exist

### `POST /action-items/extract`
Extracts action items using rule-based heuristics and persists the results.

Request body:

```json
{
  "text": "- [ ] Set up database\n- Write tests",
  "save_note": true
}
```

Response:

```json
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "Set up database" },
    { "id": 2, "text": "Write tests" }
  ]
}
```

### `POST /action-items/extract/llm`
Extracts action items using Ollama and persists the results.

- Uses the `llama3.1:8b` model
- Returns `503` if the model service is unavailable
- Returns `502` if the model response cannot be parsed as structured JSON

### `GET /action-items`
Lists action items.

Optional query parameter:

- `note_id`: when provided, returns only action items associated with that note

Example:

```text
GET /action-items?note_id=1
```

### `POST /action-items/{action_item_id}/done`
Marks an action item as done or not done.

Request body:

```json
{
  "done": true
}
```

Response:

```json
{
  "id": 1,
  "done": true
}
```

- Returns `404` if the action item does not exist

## Running Tests
Run the Week 2 test suite from the repository root:

```bash
poetry run pytest week2/tests
```

You can also run a single test module:

```bash
poetry run pytest week2/tests/test_notes.py
```

### Important test note
Some tests in `week2/tests/test_extract.py` call `extract_action_items_llm()` directly rather than mocking Ollama. Those tests may require:

- Ollama to be installed and running
- The `llama3.1:8b` model to be available locally

If you only want to run tests that do not depend on a live Ollama instance, start with:

```bash
poetry run pytest week2/tests/test_notes.py week2/tests/test_action_items_errors.py
```

## Notes on Persistence
- Notes and action items are stored in SQLite
- The database file is created automatically at `week2/data/app.db`
- Tables are initialized on app startup via `init_db()`
