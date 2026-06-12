import json
import os
import time
from pathlib import Path
import openai
from dotenv import load_dotenv


load_dotenv()

GOLDEN_SET_PATH = Path("eval/golden_set.json")
OUTPUT_PATH = Path("eval/model-comparison.json")

# Models to compare - Using verified 2026 strings
MODELS = [
    "anthropic/claude-sonnet-4-6",     # Premium
    "google/gemini-2.5-flash-lite",     # Fast/Cheap
    "qwen/qwen-2.5-72b-instruct"      # OSS Fallback
]

# 2026 Pricing table
MODEL_PRICING = {
    "anthropic/claude-sonnet-4-6": (3.00, 15.00),
    "google/gemini-2.5-flash-lite": (0.10, 0.40),
    "qwen/qwen-2.5-72b-instruct": (0.35, 0.40),
}

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)


def estimate_cost(model, in_tokens, out_tokens):
    if model not in MODEL_PRICING:
        return 0.0
    price_in, price_out = MODEL_PRICING[model]
    return (in_tokens * price_in + out_tokens * price_out) / 1_000_000


def run_benchmark():
    if not GOLDEN_SET_PATH.exists():
        print(f"Error: {GOLDEN_SET_PATH} not found.")
        return

    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        gs = json.load(f)

    # FIXED: Handle both list and dict formats safely
    questions = gs if isinstance(gs, list) else gs.get("questions", [])

    all_results = []

    for model in MODELS:
        print(f"\n🚀 Benchmarking Model: {model}")
        for q in questions:
            # Handle different key names for the prompt
            prompt_text = q.get("input") or q.get("prompt") or ""
            q_id = q.get("id", "unknown")

            start = time.perf_counter()
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt_text}],
                    max_tokens=512
                )
                latency = int((time.perf_counter() - start) * 1000)

                in_tokens = resp.usage.prompt_tokens
                out_tokens = resp.usage.completion_tokens
                cost = estimate_cost(model, in_tokens, out_tokens)

                all_results.append({
                    "model": model,
                    "question_id": q_id,
                    "question": prompt_text[:100] + "...",
                    "answer": resp.choices[0].message.content,
                    "latency_ms": latency,
                    "input_tokens": in_tokens,
                    "output_tokens": out_tokens,
                    "cost_usd": round(cost, 6),
                    "error": None
                })
                print(f"  ✅ [{q_id}] Done ({latency}ms)")
            except Exception as e:
                all_results.append({
                    "model": model,
                    "question_id": q_id,
                    "error": str(e),
                    "latency_ms": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0
                })
                print(f"  ❌ [{q_id}] FAILED: {str(e)[:50]}")

            # Avoid hitting rate limits during benchmark
            time.sleep(1.5)

    # Save final JSON results (Required for A1)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✨ Benchmark complete. Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_benchmark()
