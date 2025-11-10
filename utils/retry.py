"""Retry helpers using a simple async exponential backoff.

This small helper avoids an external dependency but provides a behavior similar
to tenacity for common use-cases. Use tenacity if you prefer advanced features.
"""

import asyncio
import functools
from typing import Callable, Any, Coroutine, Type, Tuple


async def retry_async(
    fn: Callable[..., Coroutine],
    retries: int = 3,
    backoff: float = 1.0,
    *args,
    **kwargs,
) -> Any:
    """Simple async retry with exponential backoff.
    - fn: async callable
    - retries: max retry attempts (on top of the initial try)
    - backoff: initial backoff seconds, doubled each attempt
    """
    attempt = 0
    while True:
        try:
            return await fn(*args, **kwargs)
        except Exception:
            attempt += 1
            if attempt > retries:
                raise
            await asyncio.sleep(backoff * (2 ** (attempt - 1)))


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator version for backward compatibility.
    Usage:
        @async_retry(max_attempts=3, delay=1.0)
        async def fetch_data():
            ...
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator
