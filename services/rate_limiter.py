import time
from collections import defaultdict
from fastapi import HTTPException


# Config: 10 requests per minute
REFILL_RATE = 10
MAX_TOKENS = 10

_BUCKETS = defaultdict(lambda: {
    "tokens": float(MAX_TOKENS),
    "last_refill": time.time(),
})


def check_rate_limit(user_id: str):
    bucket = _BUCKETS[user_id]
    now = time.time()

    # Refill
    elapsed = (now - bucket["last_refill"]) / 60.0
    bucket["tokens"] = min(float(MAX_TOKENS), bucket["tokens"] + (elapsed * REFILL_RATE))
    bucket["last_refill"] = now

    if bucket["tokens"] < 1.0:
        retry_after = round((1.0 - bucket["tokens"]) / (REFILL_RATE / 60.0), 1)
        raise HTTPException(
            status_code=429,
            detail={"error": "rate_limit_exceeded", "retry_after_seconds": retry_after}
        )

    bucket["tokens"] -= 1.0
