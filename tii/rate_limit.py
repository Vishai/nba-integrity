"""Rate limiter for NBA API calls."""

import time


class RateLimiter:
    def __init__(self, min_delay: float = 1.5):
        self.min_delay = min_delay
        self.last_call = 0.0
        self.call_count = 0

    def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_call = time.time()
        self.call_count += 1


# Global instance
_limiter = RateLimiter()


def wait():
    """Wait for rate limit before making an API call."""
    _limiter.wait()


def set_delay(delay: float):
    """Override the default delay."""
    _limiter.min_delay = delay


def get_call_count() -> int:
    return _limiter.call_count
