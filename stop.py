"""Cross-platform stop script for Yuketang Helper."""
import os, signal, json
from pathlib import Path

PID_FILE = Path(__file__).resolve().parent / "logs" / "pids.json"

if not PID_FILE.exists():
    print("No running processes found.")
    raise SystemExit

for name, pid in json.loads(PID_FILE.read_text()).items():
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped {name} (PID {pid})")
    except OSError:
        print(f"{name} was not running (PID {pid})")

PID_FILE.unlink()
