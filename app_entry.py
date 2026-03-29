"""
Entry point for the PyInstaller-packaged Yuketang Helper application.
Starts the FastAPI server and opens the browser automatically.
"""

import os
import sys
import webbrowser
from pathlib import Path

# When frozen, add the backend directory (bundled inside _MEIPASS) to sys.path
# and set SSL certificate path so that outbound HTTPS/WSS connections work.
if getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(sys._MEIPASS) / "backend"))
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

# Clear proxy env vars with unsupported schemes (e.g. socks4) that cause
# errors in httpx/requests. http, https, and socks5 proxies are kept.
_PROXY_VARS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
               "http_proxy", "https_proxy", "all_proxy")
for _var in _PROXY_VARS:
    _val = os.environ.get(_var, "")
    if _val and not _val.startswith(("http://", "https://", "socks5://")):
        os.environ.pop(_var, None)

import uvicorn
from main import app  # noqa: E402

PORT = 8500

if __name__ == "__main__":
    webbrowser.open(f"http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info", use_colors=False)
