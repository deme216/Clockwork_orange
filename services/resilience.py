import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")


class TimeoutExceeded(Exception):
    pass


async def with_timeout(coro: Awaitable[T], timeout_s: float) -> T:
    try:
        return await asyncio.wait_for(coro, timeout=timeout_s)
    except asyncio.TimeoutError as exc:
        raise TimeoutExceeded(f"AI Provider exceeded {timeout_s}s limit") from exc


async def retry_with_backoff(
        fn: Callable[[int], Awaitable[T]],
        max_attempts: int = 3,
        base_delay_s: float = 1.0,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn(attempt)
        except Exception as exc:
            last_error = exc
            if attempt == max_attempts:
                raise
            delay = base_delay_s * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
            await asyncio.sleep(delay)
    raise last_error or RuntimeError("Retry failed")
