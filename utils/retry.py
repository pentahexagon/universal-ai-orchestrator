"""Retry helpers using a simple async exponential backoff.

This small helper avoids an external dependency but provides a behavior similar
to tenacity for common use-cases. Use tenacity if you prefer advanced features.
"""

import asyncio
from typing import Callable, Any, Coroutine


async def retry_async(fn: Callable[..., Coroutine], retries: int = 3, backoff: float = 1.0, *args, **kwargs) -> Any:
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
