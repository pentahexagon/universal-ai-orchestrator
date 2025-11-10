"""
Retry logic with exponential backoff
"""

import asyncio
import functools
from typing import Callable, Type, Tuple
from .logger import get_logger

logger = get_logger(__name__)


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    비동기 함수용 재시도 데코레이터

    Args:
        max_attempts: 최대 시도 횟수
        delay: 초기 대기 시간 (초)
        backoff: 지수 배율
        exceptions: 재시도할 예외 타입들

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
                        logger.error(
                            f"❌ {func.__name__} 실패 " f"({max_attempts}회 시도): {e}"
                        )
                        raise

                    logger.warning(
                        f"⚠️  {func.__name__} 재시도 "
                        f"{attempt}/{max_attempts} (대기: {current_delay}초)"
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator
