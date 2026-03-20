"""
Append-only event log stored as JSON Lines.
Location: <config_dir>/events.jsonl
Keeps the most recent MAX_EVENTS entries; older ones are trimmed automatically.
"""

import json
import threading
from datetime import datetime
from pathlib import Path

from config import get_config_dir

MAX_EVENTS = 500  # maximum entries kept on disk
_lock = threading.Lock()


def _log_path() -> Path:
    return get_config_dir() / "events.jsonl"


def append(event: dict) -> None:
    """Append one event to the log (thread-safe). Trims if over MAX_EVENTS."""
    record = {**event, "logged_at": datetime.now().isoformat(timespec="seconds")}
    path = _log_path()
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        _trim(path)


def load_recent(n: int = 50) -> list:
    """Return the last n events from disk, oldest first."""
    path = _log_path()
    if not path.exists():
        return []
    with _lock:
        lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        recent = lines[-n:]
        return [json.loads(l) for l in recent]


def _trim(path: Path) -> None:
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) > MAX_EVENTS:
        path.write_text("\n".join(lines[-MAX_EVENTS:]) + "\n", encoding="utf-8")
