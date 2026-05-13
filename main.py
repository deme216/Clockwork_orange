from fastapi import FastAPI
from routers import ai_router, stream_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VectorFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router.router, prefix="/api/v1")
app.include_router(stream_router.router, prefix="/api/v1")


@app.get("/health")
def health(): return {"status": "ok"}
