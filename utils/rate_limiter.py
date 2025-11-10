"""
Rate limiting with token bucket algorithm
"""

import asyncio
import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    토큰 버킷 알고리즘 기반 속도 제한
    """

    def __init__(
        self,
        max_requests: int,
        time_window: float,
        name: Optional[str] = None
    ):
        """
        Args:
            max_requests: 시간 윈도우 내 최대 요청 수
            time_window: 시간 윈도우 (초)
            name: 식별자 (로깅용)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.name = name or "RateLimiter"
        self.requests = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """
        요청 허가 대기
        속도 제한 초과시 자동으로 대기
        """
        async with self._lock:
            now = time.time()

            # 오래된 요청 제거
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()

            # 제한 초과시 대기
            if len(self.requests) >= self.max_requests:
                sleep_time = self.requests[0] + self.time_window - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()

            # 요청 기록
            self.requests.append(now)

    def reset(self):
        """카운터 리셋"""
        self.requests.clear()


# 전역 레이트 리미터 인스턴스
rate_limiters = {
    'gemini': RateLimiter(max_requests=60, time_window=60, name='Gemini'),
    'openai': RateLimiter(max_requests=50, time_window=60, name='OpenAI'),
    'anthropic': RateLimiter(max_requests=50, time_window=60, name='Anthropic'),
    'notion': RateLimiter(max_requests=3, time_window=1, name='Notion')
}
