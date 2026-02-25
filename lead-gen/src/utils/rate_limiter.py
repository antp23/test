"""Rate limiter for API calls."""

import time
import threading


class RateLimiter:
    """Token-bucket rate limiter for API calls.

    Usage:
        limiter = RateLimiter(requests_per_minute=100)
        limiter.wait()  # blocks until a request is allowed
        make_api_call()
    """

    def __init__(self, requests_per_minute: int = 60):
        self.min_interval = 60.0 / requests_per_minute
        self._last_request_time = 0.0
        self._lock = threading.Lock()

    def wait(self):
        """Block until a request is allowed under the rate limit."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self._last_request_time = time.monotonic()
