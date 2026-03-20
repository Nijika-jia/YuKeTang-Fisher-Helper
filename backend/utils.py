import json
import requests

from domains import TSINGHUA_DOMAIN


def _make_headers(sessionid: str) -> dict:
    return {
        "Cookie": "sessionid=%s" % sessionid,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) "
            "Gecko/20100101 Firefox/97.0"
        ),
        "Referer": "https://%s/" % TSINGHUA_DOMAIN,
        "xt-agent": "web",
    }


def get_user_info(sessionid: str) -> dict:
    """
    Fetch basic user info from Yuketang.
    Returns the data dict on success, raises on failure.
    """
    headers = _make_headers(sessionid)
    r = requests.get(
        url="https://%s/api/v3/user/basic-info" % TSINGHUA_DOMAIN,
        headers=headers,
        proxies={"http": None, "https": None},
        timeout=10,
    )
    result = json.loads(r.text)
    if result.get("code") != 0:
        raise ValueError("Failed to get user info: %s" % result.get("msg", "unknown"))
    return result["data"]


def get_all_courses(sessionid: str) -> list:
    """
    Return list of all enrolled course classrooms.
    Each item has keys: classroom_id, course (with name), teacher, name, etc.
    """
    headers = _make_headers(sessionid)
    r = requests.get(
        url="https://%s/v2/api/web/courses/list?identity=2" % TSINGHUA_DOMAIN,
        headers=headers,
        proxies={"http": None, "https": None},
        timeout=10,
    )
    result = json.loads(r.text)
    return result.get("data", {}).get("list", [])


def get_on_lesson(sessionid: str) -> list:
    """
    Return list of currently active lesson classrooms.
    Each item has keys: lessonId, courseName, classroomId, etc.
    """
    headers = _make_headers(sessionid)
    r = requests.get(
        url="https://%s/api/v3/classroom/on-lesson-upcoming-exam" % TSINGHUA_DOMAIN,
        headers=headers,
        proxies={"http": None, "https": None},
        timeout=10,
    )
    result = json.loads(r.text)
    return result.get("data", {}).get("onLessonClassrooms", [])
