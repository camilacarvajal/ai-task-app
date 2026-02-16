"""
Parse and write today.md: task lines (- [ ] / - [x]) vs rest.
Single source of truth for file path, load, segment, and write-back.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Match a single task line: optional leading space, "- [ ]" or "- [x]", rest is label.
TASK_PATTERN = re.compile(r"^(\s*-\s+)\[([ x])\](.*)$", re.IGNORECASE)


@dataclass
class Task:
    """One toggleable task: file line index, done state, and raw line for write-back."""

    line_index: int  # 0-based index in full lines list
    done: bool
    raw_line: str
    label: str  # line after checkbox, for display


def get_today_path() -> Optional[Path]:
    """Resolve TODAY_MD_PATH from env; return None if unset or empty."""
    raw = os.environ.get("TODAY_MD_PATH", "").strip()
    if not raw:
        return None
    return Path(raw).resolve()


def load_and_parse(path: Path) -> tuple[Optional[list[str]], Optional[list[Task]], Optional[str]]:
    """
    Load today.md and split into full lines and task list.

    Returns:
        (lines, tasks, error_message). On success error_message is None.
        If path missing/unreadable: lines and tasks are None, error_message set.
    """
    if not path.exists():
        return None, None, f"File not found: {path}"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return None, None, f"Cannot read file: {e}"
    except Exception as e:
        return None, None, f"Error reading file: {e}"

    lines = text.splitlines(keepends=False)
    # Normalize: we'll write back with \n; if original had \r\n we preserve by not keeping 'ends'
    # We'll join with \n on write. So no need to store line endings per line.

    tasks: list[Task] = []
    for i, line in enumerate(lines):
        m = TASK_PATTERN.match(line)
        if m:
            done = m.group(2).strip().lower() == "x"
            label = m.group(3)  # rest of line
            tasks.append(
                Task(line_index=i, done=done, raw_line=line, label=label)
            )

    return lines, tasks, None


# Date in first line. Supports:
#   # Sunday, February 15, 2026 (whatsuptoday format)
#   # February 15, 2026 / # Feb 15, 2026
#   legacy: something -- Sunday, February 15, 2026
_DATE_PATTERNS = [
    ("%A, %B %d, %Y", re.compile(r"^#\s*(\w+,?\s+\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
    ("%A, %b %d, %Y", re.compile(r"^#\s*(\w+,?\s+\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
    ("%B %d, %Y", re.compile(r"^#\s*(\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
    ("%b %d, %Y", re.compile(r"^#\s*(\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
    ("%A, %B %d, %Y", re.compile(r".*--\s*(\w+,?\s+\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
    ("%A, %b %d, %Y", re.compile(r".*--\s*(\w+,?\s+\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
    ("%b %d, %Y", re.compile(r".*--\s*(\w+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)),
]


def is_plan_stale(lines: list[str]) -> bool:
    """
    True if the plan looks like it's from another day (first line date != today).
    Returns True (stale) if no date found or parse fails, so we nudge to refresh.
    """
    if not lines:
        return True
    first = lines[0].strip()
    for fmt, pattern in _DATE_PATTERNS:
        m = pattern.match(first)
        if m:
            try:
                parsed = datetime.strptime(m.group(1).strip(), fmt).date()
                return parsed != datetime.now().date()
            except ValueError:
                continue
    return True


def toggle_task(path: Path, lines: list[str], task: Task, new_done: bool) -> Optional[str]:
    """
    Write back file with one task's checkbox flipped. Preserves all other lines.

    Returns None on success, or an error message string.
    """
    if task.line_index < 0 or task.line_index >= len(lines):
        return "Invalid task index"
    new_char = "x" if new_done else " "
    m = TASK_PATTERN.match(lines[task.line_index])
    if not m:
        return "Line is not a task line"
    new_line = f"{m.group(1)}[{new_char}]{m.group(3)}"
    new_lines = lines[: task.line_index] + [new_line] + lines[task.line_index + 1 :]
    try:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except OSError as e:
        return f"Cannot write file: {e}"
    except Exception as e:
        return f"Error writing file: {e}"
    return None
