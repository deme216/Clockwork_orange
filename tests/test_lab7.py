import asyncio
from agents.orchestrator import build_vector_graph


async def test_run():
    # 1. Build the graph
    graph = build_vector_graph()

    # 2. Define the starting state
    initial_state = {
        "session_id": "test-lab7-001",
        "user_request": "A flaming medieval sword",
        "style_context": "Crusaders",
        "use_pro_model": True,  # Set to True to test the Safety Gate (should end early)
        "current_step": "start",
        "retry_count": 0,
        "messages": []
    }

    print("--- Starting VectorFlow Graph ---")

    # 3. Run the graph
    # Use .stream to see each node's output as it happens
    async for event in graph.astream(initial_state):
        for node_name, state_update in event.items():
            print(f"\n[Node: {node_name}]")
            if "creative_brief" in state_update:
                print(f"  Creative Brief: {state_update['creative_brief'][:50]}...")
            if "final_response" in state_update:
                print(f"  Final SVG generated ({len(state_update['final_response'])} chars)")
            if state_update.get("current_step") == "artist_selection":
                print("  Condition met: Moving to Artist selection.")

    print("\n--- Graph Execution Finished ---")


if __name__ == "__main__":
    asyncio.run(test_run())
