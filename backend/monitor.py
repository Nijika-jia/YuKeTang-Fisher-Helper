import asyncio
import logging
import threading
import time
from typing import Dict, Optional

import event_log
from config import get_course_config, update_course_config
from lesson import Lesson
from utils import get_on_lesson

logger = logging.getLogger(__name__)

POLL_INTERVAL = 30  # seconds between lesson polls


class Monitor:
    """
    Background service that:
    - Polls Yuketang for active lessons every POLL_INTERVAL seconds
    - Starts a Lesson thread for each newly detected lesson
    - Cleans up Lesson objects when they end
    - Puts all lesson events onto an asyncio.Queue for the FastAPI layer
    """

    def __init__(self, sessionid: str, event_queue: asyncio.Queue) -> None:
        self.sessionid = sessionid
        self.event_queue = event_queue

        # lessonid -> Lesson
        self._active_lessons: Dict[int, Lesson] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._first_poll_done = False
        # Reference to the asyncio event loop so we can schedule coroutines
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start the monitor background thread."""
        if self._running:
            return
        self._loop = loop
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="monitor")
        self._thread.start()
        logger.info("Monitor started")

    def stop(self) -> None:
        """Stop monitoring and close all active lesson WebSockets."""
        self._running = False
        with self._lock:
            for lesson in list(self._active_lessons.values()):
                lesson.stop_lesson()
            self._active_lessons.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Monitor stopped")

    def get_active_lessons(self) -> list:
        """Return a snapshot of currently active lessons."""
        with self._lock:
            return [
                {
                    "lessonid": lesson.lessonid,
                    "lessonname": lesson.lessonname,
                    "classroomid": lesson.classroomid,
                    "teacher_name": lesson.teacher_name,
                }
                for lesson in self._active_lessons.values()
            ]

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while self._running:
            lesson_list = get_on_lesson(self.sessionid)
            self._sync_lessons(lesson_list)

            # --- Sleep with interruptible 1s ticks ---
            for _ in range(POLL_INTERVAL):
                if not self._running:
                    return
                time.sleep(1)

    def _sync_lessons(self, lesson_list: list) -> None:
        """Start new lessons and remove ended ones."""
        incoming_ids = set()

        for item in lesson_list:
            lesson_id = item.get("lessonId")
            if lesson_id is None:
                continue
            incoming_ids.add(lesson_id)

            with self._lock:
                already_tracked = lesson_id in self._active_lessons

            if not already_tracked:
                lesson_name = item.get("courseName", "Unknown")
                lesson_data = {
                    "lessonid": lesson_id,
                    "lessonname": lesson_name,
                    "classroomid": item.get("classroomId", 0),
                }
                classroom_id = str(item.get("classroomId", ""))
                course_config = get_course_config(classroom_id)
                if course_config.get("name") != lesson_name:
                    course_config["name"] = lesson_name
                    update_course_config(classroom_id, course_config)
                lesson = Lesson(
                    lesson_data=lesson_data,
                    sessionid=self.sessionid,
                    course_config=course_config,
                    on_event=self._on_lesson_event,
                )

                with self._lock:
                    self._active_lessons[lesson_id] = lesson

                if self._first_poll_done:
                    self._emit(
                        "lesson_start",
                        {
                            "lesson": lesson.lessonname,
                            "lessonid": lesson_id,
                            "message": "Started monitoring: %s" % lesson.lessonname,
                        },
                    )
                logger.info("Starting lesson thread for %s", lesson.lessonname)

                t = threading.Thread(
                    target=self._lesson_thread,
                    args=(lesson,),
                    daemon=True,
                    name="lesson-%s" % lesson_id,
                )
                t.start()

        # Remove lessons that are no longer in the active list
        with self._lock:
            ended = [lid for lid in self._active_lessons if lid not in incoming_ids]
        for lid in ended:
            with self._lock:
                lesson = self._active_lessons.pop(lid, None)
            if lesson:
                lesson.stop_lesson()

        self._first_poll_done = True

    def _lesson_thread(self, lesson: Lesson) -> None:
        """Thread target: run lesson and clean up when done."""
        lesson.start_lesson()
        with self._lock:
            self._active_lessons.pop(lesson.lessonid, None)

    def _on_lesson_event(self, event_type: str, data: dict) -> None:
        """Called by Lesson instances from their threads."""
        self._emit(event_type, data)

    def _emit(self, event_type: str, data: dict) -> None:
        """Put an event on the asyncio queue from any thread and persist it."""
        event = {"type": event_type, **data}
        event_log.append(event)
        if self._loop and not self._loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(event), self._loop
            )
