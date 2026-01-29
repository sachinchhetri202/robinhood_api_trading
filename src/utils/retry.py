"""Retry utilities with exponential backoff."""

import time
import random
from typing import Callable, Iterable, Optional, Tuple, Type


def retry(
    exceptions: Tuple[Type[BaseException], ...],
    max_retries: int = 3,
    backoff_base: float = 0.5,
    backoff_max: float = 8.0,
    jitter: float = 0.1,
    retry_on_statuses: Optional[Iterable[int]] = None,
) -> Callable:
    """
    Retry decorator with exponential backoff and optional status-based retries.

    Args:
        exceptions: Exception types that trigger retries.
        max_retries: Maximum number of retries.
        backoff_base: Base backoff in seconds.
        backoff_max: Maximum backoff in seconds.
        jitter: Random jitter factor.
        retry_on_statuses: Optional iterable of HTTP status codes to retry.
    """
    retry_on_statuses = set(retry_on_statuses or [])

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    attempts += 1
                    if attempts > max_retries:
                        raise
                    sleep_time = min(backoff_base * (2 ** (attempts - 1)), backoff_max)
                    sleep_time += random.uniform(0, jitter)
                    time.sleep(sleep_time)
                except RetryableStatusError as exc:
                    attempts += 1
                    if attempts > max_retries or exc.status_code not in retry_on_statuses:
                        raise
                    sleep_time = min(backoff_base * (2 ** (attempts - 1)), backoff_max)
                    sleep_time += random.uniform(0, jitter)
                    time.sleep(sleep_time)
        return wrapper

    return decorator


class RetryableStatusError(Exception):
    """Raised for retryable HTTP status codes."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
