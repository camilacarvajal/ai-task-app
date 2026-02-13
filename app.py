"""
Today.md visual UI: read-only display + interactive checkboxes for tasks.
Data stays in the markdown file; path from TODAY_MD_PATH. Re-reads on every run.
"""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from today_md import (
    get_today_path,
    load_and_parse,
    toggle_task,
)

# Load .env from app directory so TODAY_MD_PATH can be set there
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

st.set_page_config(page_title="Today's Focus", layout="centered")

path = get_today_path()
if path is None:
    st.error(
        "**TODAY_MD_PATH is not set.**\n\n"
        "Copy `.env.example` to `.env` and set the full path to your `today.md` file."
    )
    st.stop()

lines, tasks, error = load_and_parse(path)
if error is not None:
    st.error(error)
    st.stop()

# Build set of line indices that are tasks (for in-order rendering)
task_by_line = {t.line_index: t for t in tasks}

# Render content in document order: non-task lines as markdown, task lines as checkboxes
buffer: list[str] = []
for i in range(len(lines)):
    if i in task_by_line:
        # Flush any accumulated read-only markdown
        if buffer:
            st.markdown("\n".join(buffer))
            buffer = []
        task = task_by_line[i]
        new_done = st.checkbox(
            task.label,
            value=task.done,
            key=f"task_{task.line_index}",
        )
        if new_done != task.done:
            err = toggle_task(path, lines, task, new_done)
            if err:
                st.error(err)
            else:
                st.rerun()
    else:
        buffer.append(lines[i])

if buffer:
    st.markdown("\n".join(buffer))
