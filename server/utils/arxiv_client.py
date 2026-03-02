import random
import threading
import time

import arxiv

# Keep requests comfortably below the legacy API limit (1 req / 3s).
ARXIV_BASE_DELAY_SECONDS = 4.0
ARXIV_JITTER_SECONDS = 1.0

_ARXIV_CLIENT = arxiv.Client(delay_seconds=ARXIV_BASE_DELAY_SECONDS)
_LAST_QUERY_START = 0.0
_RATE_LOCK = threading.Lock()


def _apply_query_jitter() -> None:
    """Throttle query starts with base delay + jitter across the whole process."""
    global _LAST_QUERY_START
    with _RATE_LOCK:
        min_interval = ARXIV_BASE_DELAY_SECONDS + random.uniform(0.0, ARXIV_JITTER_SECONDS)
        now = time.monotonic()
        wait_seconds = max(0.0, (_LAST_QUERY_START + min_interval) - now)
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        _LAST_QUERY_START = time.monotonic()


def iter_results(search: arxiv.Search):
    """Yield arXiv results with process-wide request pacing."""
    _apply_query_jitter()
    return _ARXIV_CLIENT.results(search)
