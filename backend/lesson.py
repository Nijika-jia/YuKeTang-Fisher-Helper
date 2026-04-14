import json
import logging
import random
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import websocket

from ai_provider import AIProvider, create_provider
from config import api_url, http_request, get_active_ai_key, get_ai_config, get_all_ai_keys, get_config, make_headers, get_answer_queue, remove_answer_from_queue

logger = logging.getLogger(__name__)

# API URLs
URL_WSS = "wss://{domain}/wsapp/"
URL_CHECKIN = "https://{domain}/api/v3/lesson/checkin"
URL_BASIC_INFO = "https://{domain}/api/v3/lesson/basic-info"
URL_DANMU_SEND = "https://{domain}/api/v3/lesson/danmu/send"
URL_PROBLEM_ANSWER = "https://{domain}/api/v3/lesson/problem/answer"
URL_PRESENTATION_FETCH = "https://{domain}/api/v3/lesson/presentation/fetch?presentation_id={presentation_id}"
URL_REDENVELOPE_PREPARE = "https://{domain}/api/v3/lesson/redenvelope/prepare"


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
        self._used_answers: List[Dict[str, Any]] = []

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
        r = http_request("POST", api_url(URL_DANMU_SEND), headers=self.headers, data=json.dumps(payload))
        self.on_event("danmu", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "content": content,
            "status": "success" if r.json()["code"] == 0 else "error",
        })

    def _check_answer_queue(self, problem: dict) -> Optional[Any]:
        """Get the next answer from the queue that matches the problem type."""
        queue = get_answer_queue()
        problemtype = problem.get("problemType")
        
        if not queue:
            return None
            
        # Get the first answer from the queue
        answer_entry = queue[0]
        answer = answer_entry.get("answer")
        answer_type = answer_entry.get("type")
        
        if not answer:
            return None
            
        # Process answer based on problem type
        if problemtype == 1:  # Single choice
            if answer_type == "single" or answer_type == "multiple":
                # For single choice, just take the first character
                processed_answer = [answer.strip()[0].upper()]
            else:
                return None
                
        elif problemtype == 2:  # Multiple choice
            if answer_type == "multiple" or answer_type == "single":
                # For multiple choice, split by comma and strip whitespace
                processed_answer = [c.strip().upper() for c in answer.split(",") if c.strip()]
            else:
                return None
                
        elif problemtype == 5:  # Short answer
            if answer_type == "short":
                processed_answer = answer
            else:
                return None
                
        else:
            return None
            
        self._used_answers.append({
            "problem_id": problem.get("problemId"),
            "ppt_page": answer_entry.get("page"),
            "answer": processed_answer,
            "timestamp": time.time()
        })
        remove_answer_from_queue(0)
        return processed_answer

    def _grab_red_packet(self, red_envelope_id: int) -> None:
        payload = {
            "lessonId": self.lessonid,
            "redEnvelopeId": red_envelope_id,
        }
        r = http_request("POST", api_url(URL_REDENVELOPE_PREPARE), headers=self.headers, data=json.dumps(payload))
        result = r.json()
        self.on_event("red_packet", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "redEnvelopeId": red_envelope_id,
            "status": "success" if result.get("code") == 0 else "error",
            "message": result.get("msg", ""),
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _checkin(self) -> None:
        r = http_request("POST", api_url(URL_CHECKIN), headers=self.headers, data=json.dumps({"source": 21, "lessonId": self.lessonid}))
        set_auth = r.headers.get("Set-Auth")
        if set_auth:
            self.headers["Authorization"] = "Bearer %s" % set_auth

        result = r.json()
        self.auth = result["data"]["lessonToken"]

        user = get_config().get("user", {})
        self.user_uid = user.get("id")
        self.user_uname = user.get("name")

        info = http_request("GET", api_url(URL_BASIC_INFO), headers=self.headers).json()["data"]
        self.teacher_name = (info.get("teacher") or {}).get("name")

        self.on_event("signin", {
            "lesson": self.lessonname,
            "lessonid": self.lessonid,
            "status": "success" if result["code"] == 0 else "error",
            "message": result.get("msg", ""),
        })

    def _get_problems_from_presentation(self, presentation_id: Any) -> List[dict]:
        r = http_request("GET", api_url(URL_PRESENTATION_FETCH, presentation_id=presentation_id), headers=self.headers)
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
        ai_cfg = get_ai_config()
        fallback = ai_cfg.get("fallback_keys", True)

        if fallback:
            keys_to_try = get_all_ai_keys()
        else:
            provider_name, api_key = get_active_ai_key()
            keys_to_try = [(provider_name, api_key)] if api_key else []

        if not keys_to_try:
            raise RuntimeError("No AI provider available")

        cover_url = problem.get("_cover", "")
        problemtype = problem["problemType"]
        last_error = None

        for provider_name, api_key in keys_to_try:
            provider = create_provider(provider_name, api_key)
            if not provider:
                continue
            try:
                if problemtype == 5:
                    return provider.answer_short(cover_url)
                else:
                    return provider.answer_choice(cover_url, [opt["key"] for opt in problem["options"]], problemtype)
            except Exception as e:
                logger.warning("AI call failed with %s key, trying next: %s", provider_name, e)
                last_error = e

        raise RuntimeError("All AI providers failed") from last_error

    # ------------------------------------------------------------------
    # Answer submission
    # ------------------------------------------------------------------
    #
    # Answering logic (unified for all modes):
    #   1. Generate the answer immediately (AI call / random / blank).
    #   2. Wait until answer_delay seconds after the problem was received.
    #   3. Submit the answer.
    #   Safety net: if the deadline is approaching (<=5s left) and AI
    #   hasn't returned, submit a fallback (random for choice, blank for
    #   short answer).

    _FALLBACK_RESERVE = 5  # seconds before deadline to submit fallback

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
        r = http_request("POST", api_url(URL_PROBLEM_ANSWER), headers=self.headers, data=json.dumps(payload))
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

    def _build_fallback_answer(self, problem: dict, problemtype: int):
        if problemtype == 5:
            return " ", "blank"
        else:
            return self._build_random_answers(problem), "random"

    def _compute_delay(self, start_time: float, limit: int) -> float:
        """Compute how long to wait before submitting an answer."""
        if self.course_config.get("answer_last5s", False) and limit > 0:
            # Submit in the last 5 seconds: wait until (limit - random(1,5)) seconds after start
            delay = max(0, limit - random.uniform(1, min(5, limit)))
        else:
            delay = random.uniform(
                self.course_config["answer_delay_min"],
                self.course_config["answer_delay_max"],
            )
            if limit > 0:
                delay = min(delay, max(0, limit - 2))
        return delay

    def _wait_for_delay(self, start_time: float, limit: int) -> bool:
        """Wait for answer_delay since start_time. Returns False if lesson stopped."""
        delay = self._compute_delay(start_time, limit)
        remaining = delay - (time.time() - start_time)
        if remaining > 0:
            time.sleep(remaining)
        return self._running

    def _answer_problem(self, problem: dict, problemid: Any, problemtype: int, mode: str, limit: int) -> None:
        start_time = time.time()
        
        # Check answer queue only when mode is "queue"
        if mode == "queue":
            queue_answer = self._check_answer_queue(problem)
            if queue_answer is not None:
                logger.info("Using answer from queue for problem %s", problemid)
                if not self._wait_for_delay(start_time, limit):
                    return
                self._submit_answer(problemid, problemtype, queue_answer, "queue")
                return

        if mode == "ai" and self._get_ai_provider():
            # Start AI call in background thread.
            result_holder = [None]
            ai_done = threading.Event()

            logger.info("Attempting AI answer for problem %s", problemid)

            def _call_ai():
                try:
                    result_holder[0] = self._build_ai_answers(problem)
                except Exception:
                    logger.exception("AI answering failed for problem %s", problemid)
                finally:
                    ai_done.set()

            threading.Thread(target=_call_ai, daemon=True).start()

            # Wait for answer_delay first.
            delay = self._compute_delay(start_time, limit)
            if not self.course_config.get("answer_last5s", False) and limit > 0:
                delay = min(delay, max(0, limit - self._FALLBACK_RESERVE))
            remaining_delay = delay - (time.time() - start_time)
            if remaining_delay > 0:
                ai_done.wait(timeout=remaining_delay)

            if not self._running:
                return

            # If AI is done and succeeded, submit AI answer.
            if ai_done.is_set() and result_holder[0] is not None:
                self._submit_answer(problemid, problemtype, result_holder[0], "ai")
                return

            # AI not done yet — wait until deadline - FALLBACK_RESERVE.
            if not ai_done.is_set() and limit > 0:
                time_left = limit - (time.time() - start_time)
                extra_wait = max(0, time_left - self._FALLBACK_RESERVE)
                if extra_wait > 0:
                    ai_done.wait(timeout=extra_wait)

            if not self._running:
                return

            # Check AI result one more time.
            if result_holder[0] is not None:
                self._submit_answer(problemid, problemtype, result_holder[0], "ai")
                return

            # AI failed — emit notification and submit fallback.
            self.on_event("problem", {
                "lesson": self.lessonname,
                "lessonid": self.lessonid,
                "problemid": problemid,
                "problemtype": problemtype,
                "status": "ai_failed",
            })
            fallback_answer, fallback_source = self._build_fallback_answer(problem, problemtype)
            self._submit_answer(problemid, problemtype, fallback_answer, fallback_source)

        elif mode == "blank":
            if not self._wait_for_delay(start_time, limit):
                return
            self._submit_answer(problemid, problemtype, " ", "blank")

        else:
            # random mode (or ai mode without provider configured)
            if mode == "ai":
                logger.warning("AI mode selected but no API key configured, falling back to random for problem %s", problemid)
            answers = self._build_random_answers(problem)
            if not self._wait_for_delay(start_time, limit):
                return
            self._submit_answer(problemid, problemtype, answers, "random")

    def _start_answer_for_problem(self, problemid: Any, limit: int) -> None:
        for problem in self.problems_ls:
            if problem["problemId"] == problemid:
                if problem.get("result") is not None:
                    return
                problemtype = problem["problemType"]
                mode = self.course_config.get("type%d" % problemtype, "off")
                if mode == "off":
                    return

                threading.Thread(
                    target=self._answer_problem,
                    args=(problem, problemid, problemtype, mode, limit),
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
        logger.info("[WS %s] op=%s", self.lessonname, op)

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
            self.on_event("problem_received", {
                "lesson": self.lessonname,
                "lessonid": self.lessonid,
                "problemid": problem["sid"],
            })
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

        elif op == "gainbonus":
            logger.info("[WS %s] gainbonus raw: %s", self.lessonname, message)
            redpacket = data.get("redpacket", data)
            red_envelope_id = redpacket.get("redEnvelopeId")
            if red_envelope_id and self.course_config.get("auto_redpacket", True):
                threading.Thread(
                    target=self._grab_red_packet,
                    args=(red_envelope_id,),
                    daemon=True,
                ).start()

        elif op == "callpaused":
            if data.get("name") == self.user_uname:
                self.on_event("call", {"lesson": self.lessonname, "lessonid": self.lessonid})
