"""
Entry point for the PyInstaller-packaged Yuketang Helper application.
Starts the FastAPI server and opens the browser automatically.
"""

import sys
import webbrowser
from pathlib import Path

# When frozen, add the backend directory (bundled inside _MEIPASS) to sys.path
# so that `import config`, `import monitor`, etc. resolve correctly.
if getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(sys._MEIPASS) / "backend"))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

import uvicorn
from main import app  # noqa: E402

PORT = 8500

if __name__ == "__main__":
    webbrowser.open(f"http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
