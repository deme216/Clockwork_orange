import os
import time
import csv
import re
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(PROJECT_ROOT, "logs", "episode-log.csv")


@dataclass
class CallRecord:
    timestamp: str
    prompt_hash: str
    model: str
    cost_usd: float
    latency_ms: int
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    fallback_triggered: bool = False
    status: str = "ok"


# --- Lab 11 Configuration ---
FALLBACK_CHAIN = [
    os.getenv("PRIMARY_MODEL", "google/gemini-2.0-flash-001"),
    os.getenv("SECONDARY_MODEL", "google/gemini-flash-latest"),
    os.getenv("OSS_FALLBACK", "qwen/qwen-2.5-72b-instruct")
]

MODEL_PRICING = {
    "google/gemini-2.5-flash-preview": {"input": 0.15, "output": 0.60, "cache_read": 0.03},
    "google/gemini-2.0-flash-001": {"input": 0.10, "output": 0.40, "cache_read": 0.02},
    "google/gemini-3.1-flash-lite": {"input": 0.05, "output": 0.20, "cache_read": 0.01},
    "anthropic/claude-4.6-sonnet": {"input": 3.00, "output": 15.00, "cache_read": 0.30},
    "google/gemini-flash-latest": {"input": 0.10, "output": 0.40, "cache_read": 0.02},
}

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


def _log_to_csv(record: CallRecord):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(record).keys(), quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writeheader()
        writer.writerow(asdict(record))


def call_ai(prompt: str, system: str, model: str | None = None) -> dict:
    """Tries models in the fallback chain until one succeeds."""
    chain = [model] if model else FALLBACK_CHAIN
    last_error = None

    for model_name in chain:
        start_time = time.perf_counter()
        is_fallback = model_name != chain[0]
        try:
            response = _client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                timeout=float(os.getenv("LLM_TIMEOUT_SECONDS", "30.0"))
            )

            latency = int((time.perf_counter() - start_time) * 1000)
            usage = response.usage
            cache_read = getattr(usage, 'cache_read_input_tokens', 0)

            # REAL COST CALCULATION (A5 Requirement)
            pricing = MODEL_PRICING.get(model_name, {"input": 0.15, "output": 0.60, "cache_read": 0.03})
            cost = ((usage.prompt_tokens - cache_read) / 1_000_000 * pricing["input"]) + \
                   (cache_read / 1_000_000 * pricing["cache_read"]) + \
                   (usage.completion_tokens / 1_000_000 * pricing["output"])

            record = CallRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                prompt_hash=str(hash(prompt))[:10],
                model=model_name,
                cost_usd=round(cost, 6),
                latency_ms=latency,
                cache_read_tokens=cache_read,
                fallback_triggered=is_fallback
            )
            _log_to_csv(record)

            return {
                "content": response.choices[0].message.content,
                "model_used": model_name,
                "fallback_used": is_fallback,
                "latency_ms": latency,
                "cost_usd": cost
            }

        except Exception as e:
            print(f"[FALLBACK] {model_name} failed: {str(e)[:50]}")
            last_error = e
            continue

    raise RuntimeError(f"All models in fallback chain failed. Last error: {last_error}")


def clean_svg(text: str) -> str:
    match = re.search(r"(<svg.*?</svg>)", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    text = text.replace("```xml", "").replace("```", "")
    text = text.replace('\\"', '"').replace('\\n', '\n')
    return text.strip()


def run_asset_pipeline(prompt: str, style: str, use_pro: bool) -> dict:
    start_time = time.time()

    # 1. Creative Agent (UPDATED ARGUMENTS)
    creative_result = call_ai(
        prompt=f"Theme: {style}. Asset: {prompt}",
        system="You are a creative director. Describe a 2D game asset in 50 words.",
        model="google/gemini-3.1-flash-lite"
    )
    brief = creative_result["content"]

    # 2. Artist Agent (UPDATED ARGUMENTS & DYNAMIC MODEL)
    artist_model = "anthropic/claude-4.6-sonnet" if use_pro else os.getenv("PRIMARY_MODEL")
    artist_result = call_ai(
        prompt=brief,
        system="You are a vector artist. Output ONLY raw SVG XML. No talk.",
        model=artist_model
    )

    # 3. Clean SVG
    final_svg = clean_svg(artist_result["content"])
    total_latency = int((time.time() - start_time) * 1000)
    total_cost = creative_result["cost_usd"] + artist_result["cost_usd"]

    return {
        "svg": final_svg,
        "brief": brief,
        "model_used": artist_result["model_used"],
        "fallback_triggered": artist_result["fallback_used"],
        "latency_ms": total_latency,
        "cost_usd": total_cost
    }
