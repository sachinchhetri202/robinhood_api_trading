"""Simple in-memory rate limiter."""

import time
from collections import deque
from typing import Deque


class RateLimiter:
    """Token bucket style rate limiter with per-minute limits."""

    def __init__(self, max_per_minute: int):
        self.max_per_minute = max(0, int(max_per_minute))
        self._timestamps: Deque[float] = deque()

    def wait(self):
        """Block until a request is allowed."""
        if self.max_per_minute <= 0:
            return
        now = time.time()
        window_start = now - 60
        while self._timestamps and self._timestamps[0] < window_start:
            self._timestamps.popleft()
        if len(self._timestamps) < self.max_per_minute:
            self._timestamps.append(now)
            return
        sleep_time = 60 - (now - self._timestamps[0])
        if sleep_time > 0:
            time.sleep(sleep_time)
        self._timestamps.append(time.time())
