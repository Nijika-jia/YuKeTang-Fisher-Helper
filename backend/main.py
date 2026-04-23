import asyncio
import json
import logging
import sys
import threading
import time

_fmt = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
_fmt.converter = time.gmtime

logging.basicConfig(level=logging.INFO)
logging.root.handlers[0].setFormatter(_fmt)

for _name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
    _logger = logging.getLogger(_name)
    for _h in _logger.handlers:
        _h.setFormatter(_fmt)
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import base64

from Crypto.PublicKey import RSA as CryptoRSA
from Crypto.Cipher import PKCS1_v1_5

import websocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import event_log
from config import (
    get_config, save_config, get_course_config, update_course_config,
    get_ai_config, update_ai_config,
    get_audio_config, update_audio_config, STORE_DIR,
    get_domain, set_domain,
    make_headers, api_url, http_request,
    DEFAULT_COURSE_CONFIG, DOMAIN_OPTIONS,
)
from monitor import Monitor

# API URLs (used only in main.py)
URL_WSS = "wss://{domain}/wsapp/"
URL_USER_INFO = "https://{domain}/api/v3/user/basic-info"
URL_COURSE_LIST = "https://{domain}/v2/api/web/courses/list?identity=2"
URL_WEB_LOGIN = "https://{domain}/pc/web_login"
URL_PASSWORD_LOGIN = "https://{domain}/pc/login/verify_pwd_login/"
URL_GET_PUBLIC_KEY = "https://{domain}/pc/register/get_pws_public_key/"

# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------

event_queue: asyncio.Queue = asyncio.Queue()
_subscribers: set[asyncio.Queue] = set()
monitor: Optional[Monitor] = None


def get_monitor() -> Optional[Monitor]:
    return monitor


def set_monitor(m: Optional[Monitor]) -> None:
    global monitor
    monitor = m


def _handle_session_expired() -> None:
    cfg = get_config()
    cfg["sessionid"] = ""
    cfg["user"] = {}
    cfg["course_list"] = []
    save_config(cfg)
    set_monitor(None)


def _restart_monitor(sessionid: str) -> None:
    loop = asyncio.get_event_loop()
    m = get_monitor()
    if m:
        m.stop()
    m = Monitor(sessionid=sessionid, event_queue=event_queue, on_session_expired=_handle_session_expired)
    set_monitor(m)
    m.start(loop)


# ---------------------------------------------------------------------------
# Startup cache helper
# ---------------------------------------------------------------------------


def _refresh_local_cache(sessionid: str) -> None:
    cfg = get_config()
    headers = make_headers(sessionid)

    cfg["user"] = http_request("GET", api_url(URL_USER_INFO), headers=headers).json()["data"]

    raw_courses = http_request("GET", api_url(URL_COURSE_LIST), headers=headers).json()["data"]["list"]
    course_list = [
        {
            "classroom_id": str(c["classroom_id"]),
            "name": c["course"]["name"],
            "classroom_name": c["name"],
            "teacher_name": c["teacher"]["name"],
        }
        for c in raw_courses
    ]
    cfg["course_list"] = course_list

    courses = cfg.setdefault("courses", {})
    for c in course_list:
        cid = c["classroom_id"]
        if cid not in courses:
            courses[cid] = {"name": c["name"], **DEFAULT_COURSE_CONFIG}
        elif courses[cid].get("name") != c["name"]:
            courses[cid]["name"] = c["name"]

    save_config(cfg)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


async def _broadcast_events():
    while True:
        event = await event_queue.get()
        dead: list[asyncio.Queue] = []
        for q in _subscribers:
            if q.full():
                dead.append(q)
            else:
                q.put_nowait(event)
        for q in dead:
            _subscribers.discard(q)


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()

    audio_dir = STORE_DIR / "audio"
    if audio_dir.exists():
        for f in audio_dir.iterdir():
            try:
                f.unlink()
            except:
                pass
        try:
            audio_dir.rmdir()
        except:
            pass

    broadcaster = asyncio.create_task(_broadcast_events())

    cfg = get_config()
    if cfg.get("sessionid"):
        _refresh_local_cache(cfg["sessionid"])
        m = Monitor(sessionid=cfg["sessionid"], event_queue=event_queue)
        set_monitor(m)
        m.start(loop)

    yield

    broadcaster.cancel()

    m = get_monitor()
    if m:
        m.stop()


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Yuketang Helper API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class NotificationSub(BaseModel):
    enabled: bool
    signin: bool
    problem: bool
    call: bool
    danmu: bool
    red_packet: bool = True


class CourseConfig(BaseModel):
    type1: str
    type2: str
    type3: str
    type4: str
    type5: str
    answer_delay_min: int
    answer_delay_max: int
    answer_last5s: bool = True
    auto_danmu: bool
    auto_redpacket: bool = True
    danmu_threshold: int
    notification: NotificationSub
    voice_notification: NotificationSub


class AIKeyEntry(BaseModel):
    name: str
    provider: str
    key: str
    base_url: Optional[str] = None
    model: Optional[str] = None

class AIActiveKey(BaseModel):
    active_key: int


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------


@app.get("/api/domain")
async def get_domain_setting():
    return {"domain": get_domain(), "options": DOMAIN_OPTIONS}


@app.put("/api/domain")
async def update_domain_setting(body: dict):
    domain = body.get("domain", "")
    valid_keys = {opt["key"] for opt in DOMAIN_OPTIONS}
    if domain not in valid_keys:
        return {"ok": False, "error": "Invalid domain"}
    set_domain(domain)
    return {"ok": True, "domain": domain}


@app.get("/api/auth/status")
async def auth_status():
    cfg = get_config()
    if not cfg.get("sessionid"):
        return {"logged_in": False, "user": None}
    return {"logged_in": True, "user": cfg["user"]}


@app.get("/api/user/avatar")
async def user_avatar():
    from fastapi.responses import Response as HttpResponse
    cfg = get_config()
    avatar_url = cfg.get("user", {}).get("avatar", "")
    if not avatar_url:
        return HttpResponse(status_code=404, content=b"", media_type="image/png")
    try:
        r = http_request("GET", avatar_url, timeout=10)
        content_type = r.headers.get("Content-Type", "image/png").split(";")[0].strip()
        return HttpResponse(content=r.content, media_type=content_type)
    except Exception:
        return HttpResponse(status_code=502, content=b"", media_type="image/png")


@app.post("/api/auth/logout")
async def auth_logout():
    cfg = get_config()
    cfg["sessionid"] = ""
    cfg["user"] = {}
    cfg["course_list"] = []
    save_config(cfg)

    m = get_monitor()
    if m:
        m.stop()
        set_monitor(None)

    return {"ok": True}


class PasswordLoginBody(BaseModel):
    phone: str
    password: str
    ticket: str
    randstr: str


@app.post("/api/auth/password-login")
async def password_login(body: PasswordLoginBody):
    log = logging.getLogger("auth")
    domain = get_domain()

    # Fetch RSA public key from Yuketang
    key_r = http_request("GET", api_url(URL_GET_PUBLIC_KEY),
        headers={"Referer": f"https://{domain}/"},
    )
    pub_pem = key_r.json()["data"]["public_key"]
    cipher = PKCS1_v1_5.new(CryptoRSA.import_key(pub_pem))
    encrypted = base64.b64encode(cipher.encrypt(body.password.encode())).decode()

    login_url = api_url(URL_PASSWORD_LOGIN)
    payload = {
        "name": body.phone,
        "pwd": encrypted,
        "type": "PP",
        "ticket": body.ticket,
        "randstr": body.randstr,
        "hcaptcha_token": "",
    }
    log.info("Sending login: url=%s, phone=%s, ticket=%s...", login_url, body.phone, body.ticket[:30] if body.ticket else "")

    r = http_request("POST", login_url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Referer": f"https://{domain}/",
        },
    )

    log.info("Response: status=%s", r.status_code)

    data = r.json()
    if not data.get("success"):
        return {"ok": False, "error": data.get("msg") or str(data)}

    sessionid = r.cookies["sessionid"]

    cfg = get_config()
    cfg["sessionid"] = sessionid
    save_config(cfg)

    _refresh_local_cache(sessionid)
    user = get_config()["user"]

    _restart_monitor(sessionid)

    return {"ok": True, "user": user}


# ---------------------------------------------------------------------------
# Login WebSocket
# ---------------------------------------------------------------------------


@app.websocket("/ws/login")
async def ws_login(ws: WebSocket):
    await ws.accept()
    loop = asyncio.get_event_loop()
    login_queue: asyncio.Queue = asyncio.Queue()

    def on_open(wsapp):
        wsapp.send(json.dumps({
            "op": "requestlogin",
            "role": "web",
            "version": 1.4,
            "type": "qrcode",
            "from": "web",
        }))

    def on_message(wsapp, message):
        data = json.loads(message)
        op = data["op"]

        if op == "requestlogin":
            resp = http_request("GET", data["ticket"])
            img_b64 = base64.b64encode(resp.content).decode()
            content_type = resp.headers.get("Content-Type", "image/png").split(";")[0]
            data_url = "data:%s;base64,%s" % (content_type, img_b64)
            asyncio.run_coroutine_threadsafe(
                login_queue.put({"type": "qr", "url": data_url}), loop
            )

        elif op == "loginsuccess":
            r = http_request("POST", api_url(URL_WEB_LOGIN),
                data=json.dumps({"UserID": data["UserID"], "Auth": data["Auth"]}),
            )
            sessionid = dict(r.cookies)["sessionid"]

            cfg = get_config()
            cfg["sessionid"] = sessionid
            save_config(cfg)

            _refresh_local_cache(sessionid)
            user = get_config()["user"]

            asyncio.run_coroutine_threadsafe(
                login_queue.put({"type": "success", "sessionid": sessionid, "user": user}),
                loop,
            )
            wsapp.close()

    def on_error(wsapp, error):
        asyncio.run_coroutine_threadsafe(
            login_queue.put({"type": "error", "message": str(error)}), loop
        )

    def on_close(wsapp, *args):
        pass

    def qr_refresh_loop(wsapp_ref):
        count = 0
        while getattr(wsapp_ref, "_keep_running", True):
            if count >= 55:
                count = 0
                wsapp_ref.send(json.dumps({
                    "op": "requestlogin",
                    "role": "web",
                    "version": 1.4,
                    "type": "qrcode",
                    "from": "web",
                }))
            else:
                time.sleep(1)
                count += 1

    wsapp = websocket.WebSocketApp(
        url=api_url(URL_WSS),
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    threading.Thread(target=wsapp.run_forever, daemon=True, name="login-ws").start()
    threading.Thread(target=qr_refresh_loop, args=(wsapp,), daemon=True, name="login-ws-refresh").start()

    try:
        while True:
            msg = await login_queue.get()
            await ws.send_json(msg)

            if msg["type"] in ("success", "error"):
                break
    except (WebSocketDisconnect, RuntimeError):
        msg = None

    if msg and msg.get("type") == "success":
        _restart_monitor(msg["sessionid"])

    wsapp._keep_running = False
    wsapp.close()


# ---------------------------------------------------------------------------
# Course routes
# ---------------------------------------------------------------------------


@app.get("/api/courses/active")
async def get_active_courses():
    m = get_monitor()
    if not m:
        return {"lessons": []}
    return {"lessons": m.get_active_lessons()}


@app.get("/api/courses/all")
async def get_all_courses_endpoint():
    cfg = get_config()
    if not cfg.get("sessionid"):
        return []
    cached = cfg.get("course_list", [])
    m = get_monitor()
    active_map: dict = {}
    if m:
        for lesson in m.get_active_lessons():
            active_map[str(lesson["classroomid"])] = lesson["lessonid"]
    return [
        {
            "classroom_id": c["classroom_id"],
            "name": c["name"],
            "classroom_name": c["classroom_name"],
            "teacher_name": c["teacher_name"],
            "active": c["classroom_id"] in active_map,
        }
        for c in cached
    ]


@app.get("/api/courses/defaults")
async def get_course_defaults():
    return DEFAULT_COURSE_CONFIG


@app.get("/api/courses/settings")
async def get_all_course_settings():
    cfg = get_config()
    return {cid: get_course_config(cid) for cid in cfg.get("courses", {})}


@app.get("/api/courses/settings/{course_id}")
async def get_course_settings(course_id: str):
    return get_course_config(course_id)


@app.put("/api/courses/settings/{course_id}")
async def update_course_settings(course_id: str, body: CourseConfig):
    data = body.model_dump()
    update_course_config(course_id, data)

    m = get_monitor()
    if m:
        with m._lock:
            lesson = next(
                (l for l in m._active_lessons.values() if str(l.classroomid) == course_id),
                None,
            )
        if lesson:
            lesson.course_config.update(data)

    return {"ok": True, "course_id": course_id, "config": data}


# ---------------------------------------------------------------------------
# AI settings routes
# ---------------------------------------------------------------------------


@app.post("/api/ai/test")
async def test_ai_key(
    provider: str = Form(...),
    key: Optional[str] = Form(None),
    key_index: Optional[str] = Form(default=None),
    image: UploadFile = File(...),
):
    # Multipart form may send key_index as a string; Optional[int] sometimes fails to bind — parse explicitly.
    idx: Optional[int] = None
    if key_index is not None and str(key_index).strip() != "":
        try:
            idx = int(key_index)
        except ValueError:
            return {"ok": False, "error": "Invalid key index"}

    key_entry: Optional[dict] = None
    if idx is not None:
        cfg = get_ai_config()
        if idx < 0 or idx >= len(cfg["keys"]):
            return {"ok": False, "error": "Invalid key index"}
        key_entry = cfg["keys"][idx]
        key = key_entry["key"]
        provider = key_entry.get("provider") or ""
        _logger.info("Testing AI provider: %s using key index: %d", provider, idx)
    else:
        if not provider or not key:
            return {"ok": False, "error": "Missing provider or key"}
        _logger.info("Testing AI provider: %s, key length: %d", provider, len(key))
    
    # Require image for testing
    if not image:
        return {"ok": False, "error": "Image is required for testing"}
    
    from ai_provider import create_provider, create_provider_from_entry, describe_provider_failure
    try:
        if idx is not None and key_entry is not None:
            ai_client = create_provider_from_entry(key_entry)
            if not ai_client:
                _logger.error("Failed to create provider from entry: %s", key_entry.get("provider"))
                return {"ok": False, "error": describe_provider_failure(key_entry)}
        else:
            ai_client = create_provider(provider, key)
            if not ai_client:
                _logger.error("Failed to create provider: %s", provider)
                return {
                    "ok": False,
                    "error": (
                        f"Invalid provider: {provider}. "
                        "Use google, qwen, dashscope, moonshot, or add a custom OpenAI-compatible key with Base URL and model."
                    ),
                }
        
        image_bytes = await image.read()
        _logger.info("Test image size: %d bytes", len(image_bytes))

        _logger.info("Calling test_call for provider: %s", provider)
        result = ai_client.test_call(image_bytes=image_bytes)
        _logger.info("Test successful: %s", result[:100] + "..." if len(result) > 100 else result)
        return {"ok": True, "message": result}
    except Exception as e:
        _logger.error("AI test failed: %s", str(e), exc_info=True)
        return {"ok": False, "error": str(e)}


@app.get("/api/ai/settings")
async def get_ai_settings():
    from ai_provider import effective_ai_entry

    cfg = get_ai_config()
    masked_keys = []
    for entry in cfg["keys"]:
        eff = effective_ai_entry(entry)
        raw = eff["key"]
        masked = raw[:4] + "****" + raw[-4:] if len(raw) > 8 else "****"
        masked_keys.append({**eff, "key": masked})
    return {"keys": masked_keys, "active_key": cfg["active_key"], "fallback_keys": cfg.get("fallback_keys", True)}


@app.post("/api/ai/keys")
async def add_ai_key(body: AIKeyEntry):
    cfg = get_ai_config()
    keys = cfg["keys"]
    keys.append(body.model_dump())
    active = cfg["active_key"]
    if active < 0:
        active = 0
    update_ai_config({"keys": keys, "active_key": active})
    return {"ok": True, "index": len(keys) - 1}


@app.delete("/api/ai/keys/{index}")
async def delete_ai_key(index: int):
    cfg = get_ai_config()
    keys = cfg["keys"]
    keys.pop(index)
    active = cfg["active_key"]
    if active >= len(keys):
        active = len(keys) - 1
    elif active > index:
        active -= 1
    elif active == index:
        active = 0 if keys else -1
    update_ai_config({"keys": keys, "active_key": active})
    return {"ok": True}


@app.put("/api/ai/active")
async def set_active_ai_key(body: AIActiveKey):
    update_ai_config({"active_key": body.active_key})
    return {"ok": True}


@app.put("/api/ai/fallback")
async def set_ai_fallback(body: dict):
    update_ai_config({"fallback_keys": bool(body.get("fallback_keys", True))})
    return {"ok": True}


# ---------------------------------------------------------------------------
# Answer Queue routes
# ---------------------------------------------------------------------------


@app.get("/api/answer/queue")
async def get_answer_queue():
    from config import get_answer_queue as get_queue
    queue = get_queue()
    return {"queue": queue}


@app.post("/api/answer/queue")
async def add_to_answer_queue(body: dict):
    from config import add_answer_to_queue
    add_answer_to_queue(body)
    return {"ok": True}


@app.post("/api/answer/queue/batch")
async def batch_add_to_answer_queue(body: dict):
    from config import batch_add_to_queue
    answers = body.get("answers", [])
    added = batch_add_to_queue(answers)
    return {"ok": True, "added": added}


@app.delete("/api/answer/queue/{index}")
async def remove_from_answer_queue(index: int):
    from config import remove_answer_from_queue
    remove_answer_from_queue(index)
    return {"ok": True}


@app.put("/api/answer/queue/{index}")
async def update_answer_in_queue(index: int, body: dict):
    from config import update_answer_in_queue as update_fn
    update_fn(index, body)
    return {"ok": True}


@app.delete("/api/answer/queue")
async def clear_answer_queue():
    from config import clear_answer_queue
    clear_answer_queue()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Audio settings routes
# ---------------------------------------------------------------------------

@app.get("/api/audio/settings")
async def get_audio_settings_endpoint():
    return get_audio_config()


@app.put("/api/audio/settings")
async def update_audio_settings_endpoint(body: dict):
    update_audio_config({"enabled": bool(body.get("enabled", False))})
    return {"ok": True}


@app.post("/api/audio/upload")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename:
        return {"ok": False, "error": "No file"}
    ext = Path(file.filename).suffix
    if ext.lower() not in [".mp3", ".wav", ".ogg", ".m4a"]:
        return {"ok": False, "error": "Unsupported file type"}
    
    save_path = STORE_DIR / "custom_audio"
    with open(save_path, "wb") as f:
        f.write(await file.read())
    
    return {"ok": True}


@app.get("/api/audio/custom")
async def get_custom_audio():
    save_path = STORE_DIR / "custom_audio"
    if save_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(save_path, media_type="audio/mpeg")
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"ok": False, "error": "No custom audio"})

@app.get("/api/audio/exists")
async def check_audio_exists():
    save_path = STORE_DIR / "custom_audio"
    if save_path.exists():
        return {"exists": True}
    return {"exists": False}


# ---------------------------------------------------------------------------
# Events WebSocket
# ---------------------------------------------------------------------------


@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    await ws.accept()

    history = event_log.load_recent(50)
    if history:
        await ws.send_json({"type": "history", "events": history})

    client_queue: asyncio.Queue = asyncio.Queue(maxsize=200)
    _subscribers.add(client_queue)

    async def heartbeat():
        while True:
            await asyncio.sleep(30)
            await ws.send_json({"type": "heartbeat"})

    hb_task = asyncio.create_task(heartbeat())

    try:
        while True:
            event = await client_queue.get()
            await ws.send_json(event)
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        hb_task.cancel()
        _subscribers.discard(client_queue)


# ---------------------------------------------------------------------------
# Static file serving (production)
# ---------------------------------------------------------------------------


def _get_static_dir() -> Path:
    """Locate the frontend static files in both normal and PyInstaller environments."""
    if getattr(sys, "frozen", False):
        # PyInstaller bundle — files are extracted to sys._MEIPASS
        return Path(sys._MEIPASS) / "static"
    return Path(__file__).resolve().parent / "static"


_STATIC_DIR = _get_static_dir()

if _STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=_STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file = _STATIC_DIR / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(_STATIC_DIR / "index.html")
