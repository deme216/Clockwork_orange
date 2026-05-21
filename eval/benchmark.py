import asyncio
import time
from services.llm_service import call_ai


async def run_benchmark():
    test_prompt = "Draw a simple sword"
    system_prompt = "You are a vector artist..."  # Make this long (>1024 tokens) to trigger cache

    print("Running 10 calls to test caching and latency...")
    results = []

    for i in range(10):
        start = time.time()
        # Call the production function
        resp = call_ai(test_prompt, system_prompt)
        end = time.time()
        results.append(end - start)
        print(f"Call {i + 1}: {round(end - start, 2)}s")

    # We will use these numbers to fill out docs/optimization-report.md
    print(f"Average Latency: {sum(results) / len(results)}s")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
