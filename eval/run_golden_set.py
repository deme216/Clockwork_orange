import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
import httpx
from dotenv import load_dotenv


# 1. Load the .env file (Fixes the "Key not set" error)
load_dotenv()

# ─── Configuration ─────────────────────────────────────────────────────────

OR_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
# Use a different model family for the judge to avoid self-bias (Slide 8)
JUDGE_MODEL = "anthropic/claude-3-haiku"

# FastAPI endpoint
APP_ENDPOINT = os.environ.get("APP_ENDPOINT", "http://localhost:8000/api/v1/ai/stream")

GOLDEN_SET_PATH = Path("eval/golden_set.json")
RESULTS_DIR = Path("eval/results")

# ─── Load Golden Set from File ─────────────────────────────────────────────

if not GOLDEN_SET_PATH.exists():
    raise FileNotFoundError(f"Could not find {GOLDEN_SET_PATH}. Please create it first.")

with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as golden_file:
    GOLDEN_SET = json.load(golden_file)

# ─── LLM Judge ─────────────────────────────────────────────────────────────

JUDGE_PROMPT = """You are an expert technical evaluator for a 2D game asset generator called VectorFlow.
Evaluate the AI Assistant's response based on the provided rubric.

USER QUESTION: {question}
EXPECTED OUTPUT: {expected}
RUBRIC: {rubric}

ACTUAL RESPONSE: 
{actual}

Output ONLY a valid JSON object:
{{"pass": true|false, "reason": "concise explanation", "score": 0.0-1.0}}"""


async def judge_response(item: dict, actual: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OR_API_KEY}"},
                json={
                    "model": JUDGE_MODEL,
                    "messages": [{"role": "user", "content": JUDGE_PROMPT.format(
                        question=item["input"],
                        expected=item["expected"],
                        rubric=item["rubric"],
                        actual=actual
                    )}],
                    "response_format": {"type": "json_object"}
                }
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
            return {"pass": False, "reason": f"Judge failed: {str(e)}", "score": 0.0}


# ─── App Caller (VectorFlow Specific) ──────────────────────────────────────

async def call_your_app(question: str) -> str:
    """Calls VectorFlow using the StreamRequest schema from Lab 6/7."""
    async with httpx.AsyncClient(timeout=40) as client:
        try:
            payload = {
                "message": question,
                "session_id": "eval-session-999",
                "system": "### PROTOCOL ### ROLE: SVG_GENERATOR. Output ONLY raw SVG code."
            }
            response = await client.post(APP_ENDPOINT, json=payload)

            if response.status_code == 200:
                full_text = ""
                for line in response.text.splitlines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            full_text += chunk.get("token", "")
                        except json.JSONDecodeError:
                            continue
                return full_text if full_text else response.text
            return f"Error {response.status_code}: {response.text}"
        except httpx.RequestError as e:
            return f"[APP_ERROR: {str(e)}]"


# ─── Main Evaluation Loop ──────────────────────────────────────────────────

async def run_evaluation():
    if not OR_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set in .env")
        return

    print(f"🚀 VectorFlow Golden Set Evaluation — {len(GOLDEN_SET)} items")
    print("-" * 60)

    results = []
    passing = 0
    start_time = time.time()  # Start timer

    # Step 1: Get all app responses (Async Batching - Slide 12)
    print("Step 1: Generating assets from app...")
    app_calls = [call_your_app(item["input"]) for item in GOLDEN_SET]
    actual_responses = await asyncio.gather(*app_calls)

    # Step 2: Judge all responses
    print("Step 2: Judging responses with LLM-as-Judge...")
    judge_calls = [judge_response(item, actual) for item, actual in zip(GOLDEN_SET, actual_responses)]
    verdicts = await asyncio.gather(*judge_calls)

    # Step 3: Compile
    for item, actual, verdict in zip(GOLDEN_SET, actual_responses, verdicts):
        is_pass = verdict.get("pass", False)
        if is_pass:
            passing += 1

        results.append({
            **item,
            "actual_response": actual[:200] + "...",
            "pass": is_pass,
            "reason": verdict.get("reason", "No reason provided"),
            "score": verdict.get("score", 0.0)
        })
        status_icon = "✅ PASS" if is_pass else "❌ FAIL"
        print(f"[{item['id']}] {status_icon} - {item['category']}")

    # Final Stats
    total_time = round(time.time() - start_time, 2)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = RESULTS_DIR / f"results-{timestamp}.json"

    summary = {
        "timestamp": timestamp,
        "total": len(GOLDEN_SET),
        "passing": passing,
        "score": passing / len(GOLDEN_SET),
        "total_time_seconds": total_time,
        "results": results
    }

    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(summary, out_f, indent=2)

    print("-" * 60)
    print(f"FINAL SCORE: {passing}/{len(GOLDEN_SET)} | Duration: {total_time}s")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
