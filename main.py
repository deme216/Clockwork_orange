import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import ai_router, stream_router
from services.rate_limiter import check_rate_limit
from fastapi.responses import JSONResponse


app = FastAPI(title="VectorFlow API", version="1.0.0")
START_TIME = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for Rate Limiting (Part 4)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1/ai"):
        user_id = request.headers.get("X-User-ID") or request.client.host
        try:
            check_rate_limit(user_id)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
    return await call_next(request)


app.include_router(ai_router.router, prefix="/api/v1")
app.include_router(stream_router.router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Liveness check for Docker/Railway. Must stay under 100ms."""
    return {
        "status": "ok",
        "uptime": round(time.time() - START_TIME),
        "server_time": datetime.now(timezone.utc).isoformat()
    }
