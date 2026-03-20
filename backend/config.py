import json
import os
import sys
from pathlib import Path

APP_NAME = "yuketang-helper"

# ---------------------------------------------------------------------------
# Default course config (replaces the external default_course_config.json)
# ---------------------------------------------------------------------------

DEFAULT_COURSE_CONFIG: dict = {
    "type1": "random",
    "type2": "random",
    "type3": "random",
    "type4": "off",
    "type5": "off",
    "answer_delay_min": 3,
    "answer_delay_max": 10,
    "auto_danmu": True,
    "danmu_threshold": 3,
    "notification": {
        "enabled": True,
        "signin": True,
        "problem": True,
        "call": True,
        "danmu": False,
    },
    "voice_notification": {
        "enabled": False,
        "signin": True,
        "problem": True,
        "call": True,
        "danmu": False,
    },
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def get_config_dir() -> Path:
    # macOS: ~/Library/Application Support/yuketang-helper
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    # Windows: %APPDATA%\yuketang-helper
    elif "APPDATA" in os.environ:
        base = Path(os.environ["APPDATA"])
    # Linux / other: ~/.config/yuketang-helper
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_dir = base / APP_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


# ---------------------------------------------------------------------------
# Core config read/write
# ---------------------------------------------------------------------------


def get_config() -> dict:
    path = get_config_path()
    if not path.exists():
        cfg = {"sessionid": "", "user": {}, "course_list": [], "courses": {}}
        save_config(cfg)
        return cfg
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Cached user info
# ---------------------------------------------------------------------------


def get_cached_user() -> dict:
    return get_config().get("user", {})


def save_cached_user(user: dict) -> None:
    cfg = get_config()
    cfg["user"] = user
    save_config(cfg)


# ---------------------------------------------------------------------------
# Cached course list
# ---------------------------------------------------------------------------


def get_cached_courses() -> list:
    return get_config().get("course_list", [])


def save_cached_courses(course_list: list) -> None:
    cfg = get_config()
    cfg["course_list"] = course_list
    save_config(cfg)


# ---------------------------------------------------------------------------
# Per-course settings
# ---------------------------------------------------------------------------


def get_course_config(course_id: str) -> dict:
    config = get_config()
    course = config.get("courses", {}).get(str(course_id), {})
    defaults = DEFAULT_COURSE_CONFIG
    for key, value in defaults.items():
        if key not in course:
            course[key] = value
        elif isinstance(value, dict):
            merged = dict(value)
            merged.update(course[key])
            course[key] = merged
    return course


def update_course_config(course_id: str, data: dict) -> None:
    config = get_config()
    if "courses" not in config:
        config["courses"] = {}
    existing = config["courses"].get(str(course_id), {})
    existing.update(data)
    config["courses"][str(course_id)] = existing
    save_config(config)


# ---------------------------------------------------------------------------
# Startup initialisation
# ---------------------------------------------------------------------------


def init_all_course_defaults(course_list: list) -> None:
    """Ensure every course in course_list has a settings entry in config.json."""
    config = get_config()
    if "courses" not in config:
        config["courses"] = {}

    changed = False
    for c in course_list:
        cid = str(c.get("classroom_id", ""))
        if not cid:
            continue
        if cid not in config["courses"]:
            config["courses"][cid] = {
                "name": c.get("name", ""),
                **DEFAULT_COURSE_CONFIG,
            }
            changed = True
        else:
            # Ensure name is up-to-date
            name = c.get("name", "")
            if config["courses"][cid].get("name") != name:
                config["courses"][cid]["name"] = name
                changed = True

    if changed:
        save_config(config)
