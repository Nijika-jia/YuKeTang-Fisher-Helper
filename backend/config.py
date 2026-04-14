import json
import logging
import os
import sys
import time as _time
from pathlib import Path
from typing import Any

# Bypass system proxy for Yuketang and ModelScope domains.
# On Windows the system proxy (e.g. socks4 from Clash/V2Ray) is read from the
# registry and can cause "Unknown scheme" errors in requests/httpx.  These
# domains are domestic and don't need a proxy.  Google AI requests are NOT
# included so they can still go through the user's proxy.
_NO_PROXY_DOMAINS = ",".join([
    "pro.yuketang.cn",
    "www.yuketang.cn",
    "changjiang.yuketang.cn",
    "huanghe.yuketang.cn",
    "api-inference.modelscope.cn",
])
_existing = os.environ.get("NO_PROXY", "")
os.environ["NO_PROXY"] = f"{_existing},{_NO_PROXY_DOMAINS}" if _existing else _NO_PROXY_DOMAINS

import requests


def _get_base_dir() -> Path:
    """Return the project root directory, handling both normal and PyInstaller environments."""
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle — use the directory containing the exe
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


STORE_DIR = _get_base_dir() / "store"
STORE_DIR.mkdir(parents=True, exist_ok=True)

_CONFIG_PATH = STORE_DIR / "config.json"
_ANSWER_QUEUE_PATH = STORE_DIR / "answer_queue.json"

DEFAULT_COURSE_CONFIG: dict = {
    "type1": "ai",
    "type2": "ai",
    "type3": "random",
    "type4": "off",
    "type5": "ai",
    "answer_delay_min": 1,
    "answer_delay_max": 2,
    "answer_last5s": True,
    "auto_danmu": True,
    "auto_redpacket": True,
    "danmu_threshold": 3,
    "notification": {
        "enabled": False,
        "signin": True,
        "problem": True,
        "call": True,
        "danmu": True,
        "red_packet": True,
    },
    "voice_notification": {
        "enabled": False,
        "signin": True,
        "problem": True,
        "call": True,
        "danmu": True,
        "red_packet": True,
    },
}

DEFAULT_AI_CONFIG: dict = {
    "keys": [],
    "active_key": -1,
    "fallback_keys": True,
}

DEFAULT_AUDIO_CONFIG: dict = {
    "enabled": False,
}

DOMAIN_OPTIONS = [
    {"key": "www.yuketang.cn", "label": "Yuketang", "label_zh": "雨课堂"},
    {"key": "pro.yuketang.cn", "label": "Hetang Yuketang", "label_zh": "荷塘雨课堂"},
    {"key": "changjiang.yuketang.cn", "label": "Changjiang Yuketang", "label_zh": "长江雨课堂"},
    {"key": "huanghe.yuketang.cn", "label": "Huanghe Yuketang", "label_zh": "黄河雨课堂"},
]

DEFAULT_DOMAIN = "pro.yuketang.cn"

_EMPTY_CONFIG = {"sessionid": "", "domain": DEFAULT_DOMAIN, "user": {}, "course_list": [], "courses": {}, "ai": dict(DEFAULT_AI_CONFIG), "audio": dict(DEFAULT_AUDIO_CONFIG)}


def get_config() -> dict:
    if not _CONFIG_PATH.exists():
        save_config(dict(_EMPTY_CONFIG))
        return dict(_EMPTY_CONFIG)
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_course_config(course_id: str) -> dict:
    course = get_config().get("courses", {}).get(str(course_id), {})
    for key, value in DEFAULT_COURSE_CONFIG.items():
        if key not in course:
            course[key] = value
        elif isinstance(value, dict):
            merged = dict(value)
            merged.update(course[key])
            course[key] = merged
    return course


def update_course_config(course_id: str, data: dict) -> None:
    cfg = get_config()
    cfg.setdefault("courses", {}).setdefault(str(course_id), {}).update(data)
    save_config(cfg)


def get_ai_config() -> dict:
    cfg = get_config()
    ai = cfg.get("ai", {})
    merged = dict(DEFAULT_AI_CONFIG)
    merged.update(ai)
    return merged


def get_active_ai_key() -> tuple:
    ai = get_ai_config()
    keys = ai["keys"]
    idx = ai["active_key"]
    if idx < 0 or idx >= len(keys):
        return ("", "")
    entry = keys[idx]
    return (entry["provider"], entry["key"])


def get_all_ai_keys() -> list:
    """Return all AI key entries as a list of (provider, key) tuples, active key first."""
    ai = get_ai_config()
    keys = ai["keys"]
    active = ai["active_key"]
    if not keys:
        return []
    ordered = []
    if 0 <= active < len(keys):
        ordered.append((keys[active]["provider"], keys[active]["key"]))
    for i, entry in enumerate(keys):
        if i != active:
            ordered.append((entry["provider"], entry["key"]))
    return ordered


def update_ai_config(data: dict) -> None:
    cfg = get_config()
    ai = cfg.setdefault("ai", dict(DEFAULT_AI_CONFIG))
    ai.update(data)
    save_config(cfg)


def get_audio_config() -> dict:
    cfg = get_config()
    audio = cfg.get("audio", {})
    merged = dict(DEFAULT_AUDIO_CONFIG)
    merged.update(audio)
    return merged


def update_audio_config(data: dict) -> None:
    cfg = get_config()
    audio = cfg.setdefault("audio", dict(DEFAULT_AUDIO_CONFIG))
    audio.update(data)
    save_config(cfg)


def get_answer_queue() -> list:
    """Get the answer queue."""
    if not _ANSWER_QUEUE_PATH.exists():
        save_answer_queue([])
        return []
    with open(_ANSWER_QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_answer_queue(queue: list) -> None:
    """Save the answer queue."""
    with open(_ANSWER_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def add_answer_to_queue(answer: dict) -> None:
    """Add an answer to the queue."""
    queue = get_answer_queue()
    queue.append(answer)
    save_answer_queue(queue)


def remove_answer_from_queue(index: int) -> None:
    """Remove an answer from the queue by index."""
    queue = get_answer_queue()
    if 0 <= index < len(queue):
        queue.pop(index)
        save_answer_queue(queue)


def clear_answer_queue() -> None:
    """Clear the answer queue."""
    save_answer_queue([])


def get_domain() -> str:
    cfg = get_config()
    return cfg.get("domain")


def set_domain(domain: str) -> None:
    cfg = get_config()
    cfg["domain"] = domain
    save_config(cfg)


# ---------------------------------------------------------------------------
# Shared HTTP helpers
# ---------------------------------------------------------------------------


def make_headers(sessionid: str) -> dict:
    domain = get_domain()
    return {
        "Cookie": "sessionid=%s" % sessionid,
        "Referer": "https://%s/" % domain,
        "xt-agent": "web",
    }


def api_url(template: str, **kwargs: Any) -> str:
    return template.format(domain=get_domain(), **kwargs)


_http_log = logging.getLogger("http")

_DEFAULT_PROXIES = {"http": None, "https": None}
_DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"


def http_request(
    method: str,
    url: str,
    retries: int = 10,
    timeout: int = 5,
    **kwargs: Any,
) -> requests.Response:
    """Send an HTTP request with automatic retry on non-2xx or network errors."""
    kwargs.setdefault("proxies", _DEFAULT_PROXIES)
    kwargs.setdefault("timeout", timeout)
    headers = kwargs.setdefault("headers", {})
    headers.setdefault("User-Agent", _DEFAULT_UA)

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.request(method, url, **kwargs)
            if r.status_code < 500:
                return r
            _http_log.warning("HTTP %s %s → %s (attempt %d/%d)", method, url, r.status_code, attempt, retries)
        except requests.RequestException as e:
            _http_log.warning("HTTP %s %s failed: %s (attempt %d/%d)", method, url, e, attempt, retries)
            last_exc = e
        if attempt < retries:
            _time.sleep(min(attempt, 3))

    if last_exc:
        raise last_exc
    return r  # type: ignore[possibly-undefined]


