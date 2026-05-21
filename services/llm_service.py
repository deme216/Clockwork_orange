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


# 1. Dataclass for Lab 8 Audit requirements
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


# 2. Production Fallback Chain
MODEL_CHAIN = [
    "google/gemini-2.0-flash-001",  # Primary
    "anthropic/claude-3-haiku"  # Fallback 1
]

MODEL_PRICING = {
    "google/gemini-2.5-flash-preview": {"input": 0.15, "output": 0.60, "cache_read": 0.03},
    "google/gemini-2.0-flash-001": {"input": 0.10, "output": 0.40, "cache_read": 0.02},
    "google/gemini-3.1-flash-lite": {"input": 0.05, "output": 0.20, "cache_read": 0.01},
    "anthropic/claude-4.6-sonnet": {"input": 3.00, "output": 15.00, "cache_read": 0.30},
}

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


def _log_to_csv(record: CallRecord):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(record).keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(asdict(record))


# 3. Fixed call_ai signature to match callers
def call_ai(prompt: str, system: str, model: str = None) -> dict:
    # If a specific model is requested (like in run_asset_pipeline), use only that.
    # Otherwise, use the fallback chain.
    models_to_try = [model] if model else MODEL_CHAIN
    last_error = None

    for i, model_name in enumerate(models_to_try):
        start_time = time.time()
        is_fallback = i > 0

        try:
            response = _client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                extra_headers={"X-Title": "VectorFlow Production"}
            )

            usage = response.usage
            latency = int((time.time() - start_time) * 1000)
            cache_read = getattr(usage, 'cache_read_input_tokens', 0)

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

            return {"content": response.choices[0].message.content, "cost": cost, "model": model_name}

        except Exception as e:
            last_error = e
            print(f"Model {model_name} failed. Trying next...")
            continue

    raise Exception(f"All models failed. Last error: {last_error}")


def clean_svg(text: str) -> str:
    match = re.search(r"(<svg.*?</svg>)", text, re.DOTALL)
    if match:
        text = match.group(1)
    text = text.replace("```xml", "").replace("```", "")
    text = text.replace('\\"', '"').replace('\\n', '\n')
    return text.strip()


def run_asset_pipeline(prompt: str, style: str, use_pro: bool) -> dict:
    start_time = time.time()

    # 1. Creative Agent
    creative_brief = call_ai(
        model="google/gemini-3.1-flash-lite",
        system="You are a creative director. Describe a 2D game asset in 50 words.",
        prompt=f"Theme: {style}. Asset: {prompt}"
    )

    # 2. Artist Agent (Removed the ~ from the model ID)
    artist_model = "anthropic/claude-4.6-sonnet" if use_pro else "google/gemini-flash-latest"
    raw_svg = call_ai(
        model=artist_model,
        system="You are a vector artist. Output ONLY raw SVG XML. No talk.",
        prompt=creative_brief["content"]
    )

    # 3. Clean SVG
    final_svg = clean_svg(raw_svg["content"])
    total_latency = int((time.time() - start_time) * 1000)
    total_cost = creative_brief["cost"] + raw_svg["cost"]

    # 4. Corrected CallRecord Instantiation
    record = CallRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        prompt_hash=str(hash(prompt))[:10],  # Fixed: used prompt_hash instead of prompt
        model=artist_model,
        cost_usd=total_cost,
        latency_ms=total_latency
    )
    _log_to_csv(record)

    return {
        "svg": final_svg,
        "brief": creative_brief["content"],
        "model_used": artist_model,
        "latency_ms": total_latency,
        "cost_usd": total_cost
    }
