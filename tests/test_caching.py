import asyncio
from services.llm_service import call_ai


async def prove_caching():
    # 1. Create a VERY LONG system prompt (~2,500 tokens)
    # This guarantees we hit the 1024 limit for Gemini caching
    long_system_prompt = "ROLE: SVG_COMPILER. MANUAL: "
    technical_manual_chunk = (
        "In section 4.2 of the graphics protocol, we define the coordinate "
        "mapping for 2D vectors. Every path must be normalized to a 512 unit "
        "grid. Gradients are disallowed for performance. "
    )

    # Repeat 80 times to be safe
    long_system_prompt += technical_manual_chunk * 80

    user_prompt = "Draw a simple medieval sword"

    print(f"Prompt length: {len(long_system_prompt)} chars. Starting tests...")

    print("\n--- Call 1: Populating Cache (Expensive) ---")
    result1 = call_ai(user_prompt, long_system_prompt)
    print(f"Model: {result1['model']} | Cost: ${result1['cost']:.6f}")

    # Wait for the cache to commit on the provider side
    print("...Waiting 10 seconds for Google context cache to commit...")
    await asyncio.sleep(10)

    print("\n--- Call 2: Reading from Cache (Cheap hit) ---")
    result2 = call_ai(user_prompt, long_system_prompt)
    print(f"Model: {result2['model']} | Cost: ${result2['cost']:.6f}")

    if result1['cost'] > 0:
        savings = (1 - (result2['cost'] / result1['cost'])) * 100
        print(f"\n--- SUCCESS ---")
        print(f"Calculated Cost Reduction: {round(savings, 2)}%")
    else:
        print("\n--- ERROR: Cost was reported as $0. Check API key status. ---")


if __name__ == "__main__":
    asyncio.run(prove_caching())
