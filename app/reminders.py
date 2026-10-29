"""In-app reminder polling using Tkinter's event loop (no hidden daemon)."""
from __future__ import annotations

from datetime import datetime
from typing import Callable, List, Set, Tuple

POLL_MS = 15_000


class ReminderService:
    def __init__(self, root, get_tasks: Callable[[], List[dict]],
                 notify: Callable[[str, str], None],
                 enabled_getter: Callable[[], bool]):
        self.root = root
        self.get_tasks = get_tasks
        self.notify = notify
        self.enabled = enabled_getter
        self._fired: Set[Tuple[str, str, str]] = set()
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self) -> None:
        self._running = False

    def _tick(self) -> None:
        try:
            if self.enabled():
                self._check()
        finally:
            if self._running:
                self.root.after(POLL_MS, self._tick)

    def _check(self) -> None:
        now = datetime.now()
        hhmm = now.strftime("%H:%M")
        today = now.date().isoformat()
        for t in self.get_tasks():
            if t.get("status") != "pending":
                continue
            if t.get("reminder") != hhmm:
                continue
            key = (t.get("id", ""), today, hhmm)
            if key in self._fired:
                continue
            self._fired.add(key)
            body = f"{t.get('title', 'Task')}\nCategory: {t.get('category', '-')}"
            self.notify("Task Reminder", body)
        if len(self._fired) > 2000:
            self._fired.clear()