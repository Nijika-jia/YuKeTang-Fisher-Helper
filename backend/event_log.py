"""
Append-only event log stored as JSON Lines (store/events.jsonl).
Keeps the most recent MAX_EVENTS entries; older ones are trimmed automatically.
"""

import json
import threading
from datetime import datetime
from pathlib import Path

from config import STORE_DIR

MAX_EVENTS = 500
_lock = threading.Lock()
_LOG_PATH = STORE_DIR / "events.jsonl"


def append(event: dict) -> None:
    record = {**event, "logged_at": datetime.now().isoformat(timespec="seconds")}
    with _lock:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        _trim()


def load_recent(n: int = 50) -> list:
    if not _LOG_PATH.exists():
        return []
    with _lock:
        lines = [l.strip() for l in _LOG_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
        return [json.loads(l) for l in lines[-n:]]


def _trim() -> None:
    lines = [l for l in _LOG_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) > MAX_EVENTS:
        _LOG_PATH.write_text("\n".join(lines[-MAX_EVENTS:]) + "\n", encoding="utf-8")
