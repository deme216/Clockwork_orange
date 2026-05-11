import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ai_router


app = FastAPI(
    title="VectorFlow API",
    description="Multi-agent SVG generation backend",
    version="0.1.0"
)

# CRITICAL: This allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router.router, prefix="/v1")  # Include the router with a prefix (good practice)


@app.get("/health")
def health_check():
    return {"status": "online", "project": "VectorFlow"}  # Simple sanity check to see if server is alive.


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
