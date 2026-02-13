# Feature Implementation Plan

**Overall Progress:** `100%`

## TLDR

Build a small local Streamlit app that renders `today.md` as a visual UI: the "Today's plan" checklist is interactive (toggle complete/incomplete); all other content (title, rhythm, calendar, pipeline, deadlines) is read-only. Data stays in the markdown file on disk; path is set via env var. Re-read file on every interaction; toggling overwrites the file.

## Critical Decisions

- **New workspace:** App lives in `C:\Users\camil\OneDrive\Desktop\AI Task App` (separate repo for sharing).
- **Path:** `TODAY_MD_PATH` env var so each machine can point to its own `today.md`.
- **Editable scope:** Only checkbox lines (`- [ ]` / `- [x]`) in the Today's plan section are toggleable; everything else is read-only display.
- **Sync:** Re-read file on every Streamlit interaction; no polling or file watcher.
- **Concurrent edits:** Overwrite on toggle is acceptable; no conflict handling.
- **Toggle direction:** Both ways — incomplete ↔ complete.

## Tasks

- [x] 🟩 **Step 1: Project setup**
  - [x] 🟩 Create `requirements.txt` (Streamlit, python-dotenv only).
  - [x] 🟩 Create `.env.example` with `TODAY_MD_PATH=` and short comment.
  - [x] 🟩 Create `.gitignore` (`.env`, `__pycache__`, `.venv`, etc.).

- [x] 🟩 **Step 2: Parse and segment today.md**
  - [x] 🟩 Load file from `TODAY_MD_PATH`; handle missing/unset path with clear message.
  - [x] 🟩 Split content into: (1) task lines matching `- [ ]` or `- [x]` (with optional leading space), (2) everything else. Preserve order and exact text for write-back.
  - [x] 🟩 Expose list of tasks (each with: raw line, done boolean, stable index for write-back).

- [x] 🟩 **Step 3: Write-back logic**
  - [x] 🟩 Function: given file path + task index + new state (done/not done), re-read file, replace only that line’s `[ ]` or `[x]`, write file back. Preserve line endings and all other lines unchanged.
  - [x] 🟩 Handle read/write errors (e.g. file locked, path invalid) with user-visible message.

- [x] 🟩 **Step 4: Streamlit UI — read-only sections**
  - [x] 🟩 Render title, horizontal rule, "Today's plan" heading, then Rhythm / Recovery / Remember, Calendar table, Pipeline table, Deadlines table as read-only (e.g. `st.markdown` for markdown, or structured display). Use the parsed “everything else” content so one source of truth.

- [x] 🟩 **Step 5: Streamlit UI — interactive checklist**
  - [x] 🟩 For each task from Step 2, show a checkbox (Streamlit `st.checkbox`) with label derived from task text (e.g. strip `- [ ]` / `- [x]` and show the rest). Initial checked state = task done.
  - [x] 🟩 On change: call write-back for that task index, then `st.rerun()` so the file is re-read and UI reflects file state (and any external edits).

- [x] 🟩 **Step 6: README and run instructions**
  - [x] 🟩 README: what the app does, how to run (`pip install -r requirements.txt`, set `TODAY_MD_PATH`, `streamlit run app.py`), optional note about creating a GitHub repo to share.
