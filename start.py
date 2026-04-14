import json, subprocess, sys
from pathlib import Path
from stop import stop

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"


def start():
    stop()
    LOG_DIR.mkdir(exist_ok=True)

    kwargs = {"start_new_session": True} if sys.platform != "win32" else \
             {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}

    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8500"],
        cwd=ROOT / "backend",
        stdout=open(LOG_DIR / "backend.log", "w"),
        stderr=subprocess.STDOUT, **kwargs,
    )

    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend = subprocess.Popen(
        [npm, "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"],
        cwd=ROOT / "frontend",
        stdout=open(LOG_DIR / "frontend.log", "w"),
        stderr=subprocess.STDOUT, **kwargs,
    )

    (LOG_DIR / "pids.json").write_text(
        json.dumps({"backend": backend.pid, "frontend": frontend.pid})
    )
    print("Yuketang Helper is running")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8500/docs")


if __name__ == "__main__":
    start()