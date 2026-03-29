import json
import logging
import random
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import requests
import websocket

from ai_provider import AIProvider, create_provider
from config import api_get, api_post, api_url, get_active_ai_key, get_config, make_headers

logger = logging.getLogger(__name__)

# API URLs
URL_WSS = "wss://{domain}/wsapp/"
URL_CHECKIN = "https://{domain}/api/v3/lesson/checkin"
URL_BASIC_INFO = "https://{domain}/api/v3/lesson/basic-info"
URL_DANMU_SEND = "https://{domain}/api/v3/lesson/danmu/send"
URL_PROBLEM_ANSWER = "https://{domain}/api/v3/lesson/problem/answer"
URL_PRESENTATION_FETCH = "https://{domain}/api/v3/lesson/presentation/fetch?presentation_id={presentation_id}"


class Lesson:
    def __init__(
        self,
        lesson_data: dict,
        sessionid: str,
        course_config: dict,
        on_event: Callable[[str, dict], None],
    ):
        self.lessonid: int = lesson_data["lessonid"]
        self.lessonname: str = lesson_data["lessonname"]
        self.classroomid: int = lesson_data["classroomid"]
        self.sessionid = sessionid
        self.course_config = course_config
        self.on_event = on_event

        self.headers = make_headers(sessionid)
        self.auth: Optional[str] = None
        self.wsapp: Optional[websocket.WebSocketApp] = None
        self._running = False

        self.danmu_dict: Dict[str, List[float]] = {}
        self.sent_danmu_dict: Dict[str, float] = {}
        self.problems_ls: List[dict] = []

        self.user_uid: Optional[int] = None
        self.user_uname: Optional[str] = None
        self.teacher_name: Optional[str] = None
        self._stopped_externally = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_lesson(self) -> None:
        self._running = True
        self._checkin()
        self.wsapp = websocket.WebSocketApp(
            url=api_url(URL_WSS),
            header=self.headers,
            on_open=self._on_open,
            on_message=self._on_message,
        )
        self.wsapp.run_forever(ping_interval=30, ping_timeout=10)
        self._running = False
        if not self._stopped_externally:
            self.on_event("lesson_end", {"lesson": self.lessonname, "lessonid": self.lessonid})

    def stop_lesson(self) -> None:
        self._stopped_externally = True
        self._running = False
        if self.wsapp:
            self.wsapp.close()

    def send_danmu(self, content: str) -> None:
        payload = {
            "lessonId": self.lessonid,
            "target": "",
            "userName": "",
            "message": content,
            "extra": "",
            "requiredCensor": False,
            "wordCloud": True,
            "showStatus": True,
            "fromStart": "50",
        }
        r = self._post(URL_DANMU_SEND, payload)
        self.on_event("danmu", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "content": content,
            "status": "success" if r.json()["code"] == 0 else "error",
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post(self, url_template: str, payload: dict, **url_kwargs: Any) -> requests.Response:
        return api_post(url_template, self.headers, payload, **url_kwargs)

    def _get(self, url_template: str, **url_kwargs: Any) -> requests.Response:
        return api_get(url_template, self.headers, **url_kwargs)

    def _checkin(self) -> None:
        r = self._post(URL_CHECKIN, {"source": 21, "lessonId": self.lessonid})
        set_auth = r.headers.get("Set-Auth")
        if set_auth:
            self.headers["Authorization"] = "Bearer %s" % set_auth

        result = r.json()
        self.auth = result["data"]["lessonToken"]

        user = get_config().get("user", {})
        self.user_uid = user.get("id")
        self.user_uname = user.get("name")

        info = self._get(URL_BASIC_INFO).json()["data"]
        self.teacher_name = (info.get("teacher") or {}).get("name")

        self.on_event("signin", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "status": "success" if result["code"] == 0 else "error",
            "message": result.get("msg", ""),
        })

    def _get_problems_from_presentation(self, presentation_id: Any) -> List[dict]:
        r = self._get(URL_PRESENTATION_FETCH, presentation_id=presentation_id)
        data = r.json()["data"]
        problems = []
        for slide in data.get("slides", []):
            if "problem" in slide:
                problem = slide["problem"]
                problem["_cover"] = slide.get("cover", "")
                problems.append(problem)
        return problems

    def _add_problems(self, problems: List[dict]) -> None:
        existing_ids = {p["problemId"] for p in self.problems_ls}
        for p in problems:
            if p["problemId"] not in existing_ids:
                self.problems_ls.append(p)
                existing_ids.add(p["problemId"])

    def _build_random_answers(self, problem: dict) -> list:
        problemtype = problem["problemType"]
        options = [opt["key"] for opt in problem.get("options", [])]
        if problemtype == 1:
            return [random.choice(options)]
        elif problemtype == 2:
            k = random.randint(1, len(options))
            return random.sample(options, k)
        elif problemtype == 3:
            count = int(problem.get("pollingCount", 1))
            return random.sample(options, min(count, len(options)))

    def _get_ai_provider(self) -> Optional[AIProvider]:
        provider_name, api_key = get_active_ai_key()
        return create_provider(provider_name, api_key)

    def _build_ai_answers(self, problem: dict) -> list | str:
        provider = self._get_ai_provider()
        if not provider:
            raise RuntimeError("No AI provider available")

        cover_url = problem.get("_cover", "")
        problemtype = problem["problemType"]
        if problemtype == 5:
            return provider.answer_short(cover_url)
        else:
            return provider.answer_choice(cover_url, [opt["key"] for opt in problem["options"]], problemtype)

    # ------------------------------------------------------------------
    # Answer submission
    # ------------------------------------------------------------------
    #
    # Answering logic:
    #   - AI mode: send LLM API request immediately, submit answer as soon
    #     as the response arrives. If any error occurs or remaining time
    #     <= _AI_FALLBACK_RESERVE seconds, emit an "ai_failed" notification so the user can
    #     answer manually, and submit a random/blank answer at the _AI_FALLBACK_RESERVE-second mark
    #     as a safety net.
    #   - Random mode: wait for answer_delay, then submit a random answer.
    #   - Blank mode: wait for answer_delay, then submit a blank answer.

    _AI_FALLBACK_RESERVE = 5  # seconds before deadline to submit random fallback

    def _submit_answer(self, problemid: Any, problemtype: int, real_answer: Any, source: str) -> None:
        if problemtype == 5:
            payload_result = {"content": real_answer, "pics": [{"pic": "", "thumb": ""}]}
        else:
            payload_result = real_answer
        payload = {
            "problemId": problemid,
            "problemType": problemtype,
            "dt": int(time.time() * 1000),
            "result": payload_result,
        }
        r = self._post(URL_PROBLEM_ANSWER, payload)
        result = r.json()
        self.on_event("problem", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "problemid": problemid,
            "problemtype": problemtype,
            "answers": real_answer,
            "source": source,
            "status": "success" if result["code"] == 0 else "error",
            "message": result.get("msg", ""),
        })

    def _answer_with_ai(self, problem: dict, problemid: Any, problemtype: int, limit: int) -> None:
        start_time = time.time()

        # Try AI with a timeout so we still have time for the random fallback.
        ai_timeout = max(1, limit - self._AI_FALLBACK_RESERVE) if limit > 0 else None
        result_holder = [None]

        logger.info("Attempting AI answer for problem %s with timeout %s seconds", problemid, ai_timeout)
        def _call_ai():
            try:
                result_holder[0] = self._build_ai_answers(problem)
            except Exception:
                logger.exception("AI answering failed for problem %s", problemid)

        t = threading.Thread(target=_call_ai, daemon=True)
        t.start()
        t.join(timeout=ai_timeout)

        if not self._running:
            return

        if result_holder[0] is not None:
            # AI succeeded — submit immediately.
            self._submit_answer(problemid, problemtype, result_holder[0], "ai")
            return

        self.on_event("problem", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "problemid": problemid,
            "problemtype": problemtype,
            "status": "ai_failed",
        })

        if limit > 0:
            # Wait until 5 seconds before deadline.
            elapsed = time.time() - start_time
            fallback_wait = max(0, limit - self._AI_FALLBACK_RESERVE - elapsed)
            if fallback_wait > 0:
                time.sleep(fallback_wait)
            if not self._running:
                return
        # For short answer, submit blank; for choice questions, submit random.
        if problemtype == 5:
            self._submit_answer(problemid, problemtype, " ", "blank")
        else:
            random_answers = self._build_random_answers(problem)
            self._submit_answer(problemid, problemtype, random_answers, "random")

    def _answer_with_random(self, problem: dict, problemid: Any, problemtype: int, limit: int) -> None:
        delay = random.uniform(
            self.course_config["answer_delay_min"],
            self.course_config["answer_delay_max"],
        )
        if limit > 0:
            delay = min(delay, max(0, limit - 2))
        if delay > 0:
            time.sleep(delay)
        if not self._running:
            return
        answers = self._build_random_answers(problem)
        self._submit_answer(problemid, problemtype, answers, "random")

    def _answer_with_blank(self, problemid: Any, problemtype: int, limit: int) -> None:
        delay = random.uniform(
            self.course_config["answer_delay_min"],
            self.course_config["answer_delay_max"],
        )
        if limit > 0:
            delay = min(delay, max(0, limit - 2))
        if delay > 0:
            time.sleep(delay)
        if not self._running:
            return
        self._submit_answer(problemid, problemtype, " ", "blank")

    def _start_answer_for_problem(self, problemid: Any, limit: int) -> None:
        for problem in self.problems_ls:
            if problem["problemId"] == problemid:
                if problem.get("result") is not None:
                    return
                problemtype = problem["problemType"]
                mode = self.course_config.get("type%d" % problemtype, "off")
                if mode == "off":
                    return

                if mode == "ai" and self._get_ai_provider():
                    threading.Thread(
                        target=self._answer_with_ai,
                        args=(problem, problemid, problemtype, limit),
                        daemon=True,
                    ).start()
                elif mode == "blank":
                    threading.Thread(
                        target=self._answer_with_blank,
                        args=(problemid, problemtype, limit),
                        daemon=True,
                    ).start()
                else:
                    threading.Thread(
                        target=self._answer_with_random,
                        args=(problem, problemid, problemtype, limit),
                        daemon=True,
                    ).start()
                return

    def _handle_danmu(self, content: str) -> None:
        if not self.course_config.get("auto_danmu", True):
            return

        key = content.lower().strip()
        now = time.time()
        self.danmu_dict.setdefault(key, [])
        self.danmu_dict[key] = [t for t in self.danmu_dict[key] if now - t <= 60]

        if now - self.sent_danmu_dict.get(key, 0) <= 60:
            return

        danmu_limit = max(1, self.course_config.get("danmu_threshold", 3))
        if len(self.danmu_dict[key]) + 1 >= danmu_limit:
            self.danmu_dict[key] = []
            self.sent_danmu_dict[key] = now
            threading.Thread(target=self.send_danmu, args=(content,), daemon=True).start()
        else:
            self.danmu_dict[key].append(now)

    # ------------------------------------------------------------------
    # WebSocket callbacks
    # ------------------------------------------------------------------

    def _on_open(self, wsapp: websocket.WebSocketApp) -> None:
        wsapp.send(json.dumps({
            "op": "hello",
            "userid": self.user_uid,
            "role": "student",
            "auth": self.auth,
            "lessonid": self.lessonid,
        }))

    def _on_message(self, wsapp: websocket.WebSocketApp, message: str) -> None:
        data = json.loads(message)
        op = data.get("op", "")

        if op == "hello":
            timeline = data.get("timeline", [])
            presentation_ids = list({
                slide["pres"]
                for slide in timeline
                if slide.get("type") == "slide" and "pres" in slide
            })
            current = data.get("presentation")
            if current and current not in presentation_ids:
                presentation_ids.append(current)
            for pid in presentation_ids:
                self._add_problems(self._get_problems_from_presentation(pid))

        elif op == "unlockproblem":
            problem = data["problem"]
            self._start_answer_for_problem(problem["sid"], problem.get("limit", -1) - 1)

        elif op == "lessonfinished":
            wsapp.close()

        elif op in ("presentationupdated", "presentationcreated", "showpresentation"):
            pid = data.get("presentation")
            if pid:
                self._add_problems(self._get_problems_from_presentation(pid))

        elif op == "newdanmu":
            content = data.get("danmu", "")
            if content:
                self._handle_danmu(content)

        elif op == "callpaused":
            if data.get("name") == self.user_uname:
                self.on_event("call", {"lesson": self.lessonname, "lessonid": self.lessonid})
