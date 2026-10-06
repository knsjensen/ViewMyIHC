"""Live list of value changes, fed by the ihc integration's own notifications.

The controller hands out changes through one long-poll queue per session, and the ihc integration's thread owns it.
Polling that queue ourselves would steal changes from Home Assistant's entities, so instead we register callbacks
with ``IHCController.add_notify_event`` like the entities do. ihcsdk has no way to unregister, so once started the
monitor keeps recording until Home Assistant restarts; that costs one small callback per change.
"""

from __future__ import annotations

from collections import deque
import itertools
import threading
import time
from typing import Any

from .ihc_bridge import json_value, runtime_values

MAX_EVENTS = 2000
_CHUNK = 250


class EventMonitor:
    """Changes for one controller, newest last."""

    def __init__(self) -> None:
        self._events: deque[dict[str, Any]] = deque(maxlen=MAX_EVENTS)
        self._last: dict[int, Any] = {}
        self._registered: set[int] = set()
        self._seq = itertools.count(1)
        self._lock = threading.Lock()
        self.started: float | None = None

    @property
    def watching(self) -> int:
        return len(self._registered)

    def start(self, controller: Any, ids: list[int]) -> int:
        """Watch ``ids`` (blocking). Current values become the baseline, so only real changes are recorded."""
        new = [i for i in ids if i not in self._registered]
        for start in range(0, len(new), _CHUNK):
            chunk = new[start:start + _CHUNK]
            baseline = runtime_values(controller, chunk)
            with self._lock:
                for resource_id in chunk:
                    self._last.setdefault(resource_id, baseline.get(resource_id))
        for resource_id in new:
            # delayed: the ihc thread enables all of them in one request instead of one request per id
            controller.add_notify_event(resource_id, self._changed, True)
            self._registered.add(resource_id)
        if self.started is None:
            self.started = time.time()
        return len(new)

    def _changed(self, resource_id: int, value: Any) -> None:
        value = json_value(value)
        with self._lock:
            old = self._last.get(resource_id, value)
            self._last[resource_id] = value
            if old == value:
                return
            self._events.append({"seq": next(self._seq), "time": time.time(), "id": resource_id, "old": old, "new": value})

    def events(self, after: int = 0) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(e) for e in self._events if e["seq"] > after]

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
