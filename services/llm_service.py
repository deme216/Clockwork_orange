import os
import time
import csv
import re
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


# 1. Dataclass for structured logging (Uses dataclasses)
@dataclass
class CallRecord:
    timestamp: str
    prompt: str
    model: str
    cost_usd: float
    latency_ms: int


# 2. 2026 Pricing
MODEL_PRICING = {
    "google/gemini-flash-latest": {"input": 0.10, "output": 0.40},
    "google/gemini-3.1-flash-lite": {"input": 0.05, "output": 0.20},
    "anthropic/claude-4.6-sonnet": {"input": 3.00, "output": 15.00},
}

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


def _log_to_csv(record: CallRecord):
    """Automatically writes every AI call to a CSV file (Uses csv, datetime, dataclasses)"""
    log_path = "logs/cost-log.csv"
    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(record).keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(asdict(record))


def _clean_svg(text: str) -> str:
    """Extracts SVG code and removes backslashes/markdown."""
    match = re.search(r"(<svg.*?</svg>)", text, re.DOTALL)
    if match:
        text = match.group(1)
    text = text.replace("```xml", "").replace("```", "")
    text = text.replace('\\"', '"').replace('\\n', '\n')
    return text.strip()


def run_asset_pipeline(prompt: str, style: str, use_pro: bool) -> dict:
    """Handles the Multi-Agent Handoff: Creative -> Artist"""
    start_time = time.time()

    # 1. Creative Agent
    creative_brief = _call_ai(
        model="google/gemini-3.1-flash-lite",
        system="You are a creative director. Describe a 2D game asset in 50 words.",
        prompt=f"Theme: {style}. Asset: {prompt}"
    )

    # 2. Artist Agent
    artist_model = "anthropic/claude-4.6-sonnet" if use_pro else "~google/gemini-flash-latest"
    raw_svg = _call_ai(
        model=artist_model,
        system="You are a vector artist. Output ONLY raw SVG XML. No talk.",
        prompt=creative_brief["content"]
    )

    # 3. Clean SVG
    final_svg = _clean_svg(raw_svg["content"])

    total_latency = int((time.time() - start_time) * 1000)
    total_cost = creative_brief["cost"] + raw_svg["cost"]

    # 4. PERSISTENT LOGGING (Fulfills Lab 5 requirement)
    record = CallRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        prompt=prompt,
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


def _call_ai(model: str, system: str, prompt: str) -> dict:
    """Internal helper to call OpenRouter and calculate cost."""
    response = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    in_tok = response.usage.prompt_tokens
    out_tok = response.usage.completion_tokens

    prices = MODEL_PRICING.get(model, {"input": 0.10, "output": 0.40})
    cost = (in_tok / 1_000_000 * prices["input"]) + (out_tok / 1_000_000 * prices["output"])

    return {"content": response.choices[0].message.content, "cost": cost}
