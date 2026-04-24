from __future__ import annotations

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


def retryable(
    attempts: int = 3,
    min_wait_seconds: int = 1,
    max_wait_seconds: int = 8,
):
    return retry(
        reraise=True,
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(min=min_wait_seconds, max=max_wait_seconds),
        retry=retry_if_exception_type(Exception),
    )
