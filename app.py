"""
Today.md visual UI: read-only display + interactive checkboxes for tasks.
Data stays in the markdown file; path from TODAY_MD_PATH. Re-reads on every run.
"""

import logging
from pathlib import Path

import bleach
import markdown
import streamlit as st
from dotenv import load_dotenv

from today_md import (
    get_today_path,
    is_plan_stale,
    load_and_parse,
    toggle_task,
)
from weather_forecast import fetch_5day_forecast, get_api_key as get_weather_api_key

logger = logging.getLogger(__name__)

# Load .env from app directory so TODAY_MD_PATH can be set there
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


# Allowed tags for today.md markdown→HTML (sanitized to prevent XSS from file content)
_PLAN_ALLOWED_TAGS = [
    "p", "br", "strong", "em", "b", "i", "u", "code", "pre",
    "h1", "h2", "h3", "h4", "ul", "ol", "li", "a", "hr",
    "table", "thead", "tbody", "tr", "td", "th", "blockquote",
]
_PLAN_ALLOWED_ATTRS = {"a": ["href", "title"]}


def _render_plan_buffer(buffer: list[str]) -> None:
    """Split buffer into sections by ## headers and render each in a div.plan-section."""
    if not buffer:
        return
    sections: list[list[str]] = []
    current: list[str] = []
    for line in buffer:
        if line.strip().startswith("##"):
            if current:
                sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)
    for section in sections:
        html = markdown.markdown("\n".join(section), extensions=["tables", "nl2br"])
        html = bleach.clean(html, tags=_PLAN_ALLOWED_TAGS, attributes=_PLAN_ALLOWED_ATTRS, strip=True)
        st.markdown(
            f'<div class="plan-section">{html}</div>',
            unsafe_allow_html=True,
        )


st.set_page_config(page_title="Todos for:", layout="centered")

# Add header image
st.image("https://cdn.pixabay.com/photo/2022/09/20/20/16/oak-7468708_1280.jpg")

# Custom CSS: app background, sidebar, H1 (change hex values to your colors)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
    .stApp { background-color: rgb(187, 62, 0); color: #2B2A2A; text-align: center; padding-bottom: 240px;}
    section[data-testid="stSidebar"] { background-color: rgb(101, 124, 106); color: rgb(255, 248, 222);}
    .stAlertContainer { background-color: #FF7444; }
    .stAlertContainer p { color: #2B2A2A; }
    .stElementContainer .row-widget, .plan-section { 
        background-color: rgb(255, 248, 222, .75); 
        border-radius: 10px; 
        padding: 1.5em; 
        margin-bottom: 2em;
    }
    .plan-section h2, h1 span, .plan-section h1 { text-align: center; font-family: 'Pacifico', cursive;}
    .decorative-bottom {
        position: fixed;
        bottom: 0;
        right: 2em;
        z-index: 1;
        pointer-events: none;
        line-height: 0;
        width: 33%;
        max-height: 50%;
    }
    .plan-section tr { 
        border-top: 1px solid rgb(255, 116, 68, 0.9); 
    }
    .plan-section table { border-radius: 10px; background-color: rgb(162, 185, 167); }
    .decorative-bottom img { width: 100%; height: auto; display: block; vertical-align: bottom;}
    .plan-section hr { display: none; }
    [class*="st-key-task_"] {
        p { color: #2B2A2A; }
        .row-widget { margin: 0 1em 1em 1em; background-color: rgb(255, 248, 222, .5); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 5-day weather forecast in sidebar (optional: set OPENWEATHER_API_KEY + location)
if get_weather_api_key():
    with st.sidebar:
        st.subheader("5-day forecast")
        forecast, err = fetch_5day_forecast()
        if err:
            st.caption(err)
        elif forecast:
            for day in forecast:
                icon_url = f"https://openweathermap.org/img/wn/{day.icon}@2x.png"
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(icon_url, width=40)
                with col2:
                    st.markdown(f"**{day.date}** — {day.condition}")
                    st.caption(f"{day.low_c:.0f}° – {day.high_c:.0f}°C")
        else:
            st.caption("No forecast data.")

path = get_today_path()
if path is None:
    st.error(
        "**TODAY_MD_PATH is not set.**\n\n"
        "Copy `.env.example` to `.env` and set the full path to your `today.md` file."
    )
    st.stop()

lines, tasks, error = load_and_parse(path)
if error is not None:
    logger.warning("load_and_parse failed: %s", error)
    st.error(error)
    st.stop()

# If plan looks like it's from another day, nudge to run /whatsuptoday in Cursor
if is_plan_stale(lines):
    st.info(
        "**Plan is from another day!** To refresh: open **Cursor**, open your "
        "workspace, and run the **/whatsuptoday** command with your energy level."
    )

# Build set of line indices that are tasks (for in-order rendering)
task_by_line = {t.line_index: t for t in tasks}

# Render content in document order: non-task lines as markdown, task lines as checkboxes
buffer: list[str] = []
for i in range(len(lines)):
    if i in task_by_line:
        # Flush any accumulated read-only markdown (each section in div.plan-section)
        if buffer:
            _render_plan_buffer(buffer)
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
                logger.warning("toggle_task failed: %s", err)
                st.error(err)
            else:
                st.rerun()
    else:
        buffer.append(lines[i])

if buffer:
    _render_plan_buffer(buffer)

# Fixed decorative image at bottom of viewport (stays in place when scrolling)
st.markdown(
    '<div class="decorative-bottom">'
    '<img src="https://cdn.pixabay.com/photo/2025/08/17/07/54/ai-generated-9779358_1280.png" alt="Trees" />'
    '</div>',
    unsafe_allow_html=True,
)
