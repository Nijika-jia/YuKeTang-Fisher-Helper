"""Cross-platform start script for Yuketang Helper."""
import subprocess, sys, os, signal, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
PID_FILE = LOG_DIR / "pids.json"
LOG_DIR.mkdir(exist_ok=True)

# Stop existing processes first
if PID_FILE.exists():
    for name, pid in json.loads(PID_FILE.read_text()).items():
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Stopped previous {name} (PID {pid})")
        except OSError:
            pass
    PID_FILE.unlink()

npm = "npm.cmd" if sys.platform == "win32" else "npm"

backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=ROOT / "backend",
    stdout=open(LOG_DIR / "backend.log", "w"),
    stderr=subprocess.STDOUT,
)

frontend = subprocess.Popen(
    [npm, "run", "dev", "--", "--host", "0.0.0.0"],
    cwd=ROOT / "frontend",
    stdout=open(LOG_DIR / "frontend.log", "w"),
    stderr=subprocess.STDOUT,
)

PID_FILE.write_text(json.dumps({"backend": backend.pid, "frontend": frontend.pid}))

print(f"Yuketang Helper is running — http://localhost:5173")
