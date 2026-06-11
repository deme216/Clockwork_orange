import asyncio
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()

OR_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
JUDGE_MODEL = "anthropic/claude-3-haiku"
APP_ENDPOINT = "http://localhost:8000/api/v1/ai/stream"
RESULTS_DIR = Path("eval/results")
GOLDEN_SET_PATH = Path("eval/golden_set.json")

sem = asyncio.Semaphore(5)


def clean_json_response(text: str) -> str:
    """Strips markdown fences and extra text to find the raw JSON object."""
    # 1. Remove markdown fences
    text = re.sub(r"```(?:json)?", "", text).strip()
    # 2. Find the first '{' and last '}'
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end + 1]
    return text


async def call_your_app(question: str) -> str:
    async with sem:
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
                            except:
                                continue
                    return full_text
                return f"Error {response.status_code}"
            except Exception as e:
                return f"[APP_ERROR: {str(e)}]"


async def judge_response(item: dict, actual: str) -> dict:
    judge_prompt = f"""You are an evaluator for VectorFlow.
    QUESTION: {item['input']}
    EXPECTED: {item['expected']}
    RUBRIC: {item['rubric']}
    ACTUAL OUTPUT: {actual}
    Output ONLY a JSON object: {{"pass": true|false, "reason": "...", "score": 0.0-1.0}}"""

    async with sem:
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OR_API_KEY}"},
                    json={
                        "model": JUDGE_MODEL,
                        "messages": [{"role": "user", "content": judge_prompt}],
                        # Force the model to return JSON if supported
                        "response_format": {"type": "json_object"}
                    }
                )
                raw_content = response.json()["choices"][0]["message"]["content"]
                clean_content = clean_json_response(raw_content)
                return json.loads(clean_content)
            except Exception as e:
                # Fallback verdict so the whole script doesn't crash
                return {"pass": False, "reason": f"Judge error or bad JSON: {str(e)}", "score": 0.0}


async def run_evaluation():
    with open(GOLDEN_SET_PATH, "r") as f:
        golden_set = json.load(f)

    print(f"🚀 Starting Async Eval for {len(golden_set)} items...")
    start_time = time.time()

    # Step 1: Generate all assets
    app_tasks = [call_your_app(item["input"]) for item in golden_set]
    actual_responses = await asyncio.gather(*app_tasks)

    # Step 2: Judge all results
    judge_tasks = [judge_response(item, actual) for item, actual in zip(golden_set, actual_responses)]
    verdicts = await asyncio.gather(*judge_tasks)

    # Step 3: Process results
    results = []
    passing = 0
    for item, actual, verdict in zip(golden_set, actual_responses, verdicts):
        is_pass = verdict.get("pass", False)
        if is_pass:
            passing += 1
        results.append({
            "id": item['id'],
            "input": item['input'],
            "pass": is_pass,
            "reason": verdict.get("reason", "N/A"),
            "actual_snippet": actual[:50] + "..."
        })
        status = "✅ PASS" if is_pass else "❌ FAIL"
        print(f"[{item['id']}] {status} | {verdict.get('reason', '')}")

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = RESULTS_DIR / f"results-{timestamp}.json"
    with open(output_path, "w") as f:
        json.dump({"score": passing / len(golden_set), "results": results}, f, indent=2)

    print(f"\n✨ Done in {round(time.time() - start_time, 2)}s. Score: {passing}/{len(golden_set)}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
