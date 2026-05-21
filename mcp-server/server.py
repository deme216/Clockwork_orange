import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError


# 1. Setup & Config
load_dotenv()
# Use your choices secret from .env, or a hardcoded fallback for dev
MCP_SECRET = os.environ.get("MCP_SECRET_KEY", "lab8_secret_token_123")
LOG_PATH = Path("logs/mcp-audit.jsonl")

# Internal server logger (tracebacks stay here, never go to the AI)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

app = Server("vectorflow-tools-prod")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))


# 2. Layer 1: Authentication Logic
def verify_token(token: str) -> bool:
    if not token:
        return False
    return hmac.compare_digest(MCP_SECRET.encode(), token.encode())


# 3. Layer 2: Pydantic Validation Schema
class AssetInput(BaseModel):
    # Renamed from _auth_token to auth_token to satisfy Pydantic v2
    auth_token: str = Field(..., description="Required bearer token for security")
    asset_name: str = Field(..., min_length=1, max_length=100, description="Name of the asset")
    style: str = Field(default="Standard", max_length=50, description="Art style")


# 4. Layer 3: Structured Audit Logging
def log_audit(tool_name: str, input_dict: dict, status: str, latency: int, error: str = None):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Hash input so we don't log potentially sensitive user prompts
    input_hash = hashlib.sha256(json.dumps(input_dict, sort_keys=True).encode()).hexdigest()[:12]

    entry = {
        "ts": time.time(),
        "tool": tool_name,
        "input_hash": input_hash,
        "status": status,
        "latency_ms": latency,
        "error": error
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_vector_asset",
            description="Generates raw SVG code for a 2D game asset. Requires an auth token.",
            # model_json_schema is the Pydantic v2 way
            inputSchema=AssetInput.model_json_schema()
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    start_time = time.time()

    if name != "generate_vector_asset":
        return [types.TextContent(type="text", text=json.dumps({"error": "unknown_tool"}))]

    # --- STEP 1: AUTHENTICATION ---
    token = arguments.get("auth_token", "")
    if not verify_token(token):
        latency = int((time.time() - start_time) * 1000)
        log_audit(name, {}, "unauthorized", latency)
        return [types.TextContent(type="text", text=json.dumps({"error": "unauthorized"}))]

    # --- STEP 2: VALIDATION ---
    try:
        validated = AssetInput(**arguments)
    except ValidationError as e:
        latency = int((time.time() - start_time) * 1000)
        log_audit(name, arguments, "validation_failed", latency, error="invalid_schema")
        return [types.TextContent(type="text", text=json.dumps({"error": "invalid_input"}))]

    # --- STEP 3: EXECUTION & ERROR SANITIZATION ---
    try:
        # Using 2.5 Flash Preview - Recommended in Lab 8 slides
        resp = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": "Output ONLY raw SVG code. No markdown."},
                {"role": "user", "content": f"Draw a {validated.style} {validated.asset_name}."}
            ],
            timeout=30.0  # Increased timeout
        )

        latency = int((time.time() - start_time) * 1000)
        log_audit(name, validated.model_dump(), "ok", latency)
        return [types.TextContent(type="text", text=resp.choices[0].message.content)]

    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        # Log to FILE only, do not print to console/stderr
        log_audit(name, arguments, "error", latency, error=type(e).__name__)

        # This is what the user/AI sees. Clean and safe.
        return [types.TextContent(type="text", text=json.dumps({
            "error": "provider_timeout",
            "message": "The AI provider is currently busy. Please try again in a few seconds."
        }))]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
