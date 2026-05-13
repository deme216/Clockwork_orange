"""
Episode Logger — VectorFlow Lab 6
Records every agent event to CSV and stdout for the Week 11 Audit.
"""
import csv
import os
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone


LOG_FILE = "logs/episode-log.csv"

# 2026 Pricing for our Hybrid Tier
MODEL_PRICING = {
    "google/gemini-3.1-flash-lite": {"input": 0.05, "output": 0.20},
    "google/gemini-flash-latest": {"input": 0.10, "output": 0.40},
    "anthropic/claude-4.6-sonnet": {"input": 3.00, "output": 15.00},
}


@dataclass
class Episode:
    session_id: str
    event_type: str
    episode_id: str = field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model: str | None = None
    tool_name: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    success: bool = True
    cost_usd: float = 0.0


def log_episode(ep: Episode) -> Episode:
    """Calculate cost and write to CSV."""
    # Find pricing, default to 0 if model not in list
    pricing = MODEL_PRICING.get(ep.model if ep.model else "", {"input": 0.0, "output": 0.0})

    # Calculate cost per 1 million tokens
    ep.cost_usd = (ep.input_tokens / 1_000_000 * pricing["input"]) + \
                  (ep.output_tokens / 1_000_000 * pricing["output"])

    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(ep).keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(asdict(ep))

    label = ep.model if ep.model else (ep.tool_name if ep.tool_name else "N/A")
    print(f"[EPISODE] {ep.event_type} | {label} | ${ep.cost_usd:.6f}")
    return ep
