import requests

from domains import DOMAIN


def _make_headers(sessionid: str) -> dict:
    return {
        "Cookie": "sessionid=%s" % sessionid,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) "
            "Gecko/20100101 Firefox/97.0"
        ),
        "Referer": "https://%s/" % DOMAIN,
        "xt-agent": "web",
    }


def get_user_info(sessionid: str) -> dict:
    headers = _make_headers(sessionid)
    r = requests.get(
        url="https://%s/api/v3/user/basic-info" % DOMAIN,
        headers=headers,
        proxies={"http": None, "https": None},
        timeout=10,
    )
    return r.json()["data"]


def get_all_courses(sessionid: str) -> list:
    headers = _make_headers(sessionid)
    r = requests.get(
        url="https://%s/v2/api/web/courses/list?identity=2" % DOMAIN,
        headers=headers,
        proxies={"http": None, "https": None},
        timeout=10,
    )
    return r.json()["data"]["list"]


def get_on_lesson(sessionid: str) -> list:
    headers = _make_headers(sessionid)
    r = requests.get(
        url="https://%s/api/v3/classroom/on-lesson-upcoming-exam" % DOMAIN,
        headers=headers,
        proxies={"http": None, "https": None},
        timeout=10,
    )
    return r.json()["data"]["onLessonClassrooms"]
