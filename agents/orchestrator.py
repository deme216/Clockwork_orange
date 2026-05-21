import asyncio
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from models.agent_state import AgentState
from services.llm_service import call_ai, clean_svg
from services.guardrails import check_safety
from services.resilience import retry_with_backoff, with_timeout


MODEL_CREATIVE = "google/gemini-3.1-flash-lite"
MODEL_ARTIST = "google/gemini-2.0-flash-001"


async def creative_node(state: AgentState) -> Dict[str, Any]:
    """Node for the Creative Agent."""

    async def make_call(_attempt: int):
        # call_ai is synchronous, so we run it in a thread to keep the graph async
        return await asyncio.to_thread(
            call_ai,
            model=MODEL_CREATIVE,
            system="You are a creative director. Describe a 2D asset in 50 words.",
            prompt=f"Theme: {state.get('style_context')}. Asset: {state.get('user_request')}"
        )

    try:
        resp = await retry_with_backoff(
            lambda att: with_timeout(make_call(att), timeout_s=10.0)
        )
        return {
            "creative_brief": resp["content"],
            "current_step": "artist_selection"
        }
    except Exception as e:
        return {"last_error": str(e), "current_step": "error"}


async def artist_node(state: AgentState) -> Dict[str, Any]:
    """Node for the Artist Agent."""
    model = "anthropic/claude-4.6-sonnet" if state.get("use_pro_model") else MODEL_ARTIST

    async def make_call(_attempt: int):
        return await asyncio.to_thread(
            call_ai,
            model=model,
            system="ROLE: SVG_COMPILER. Output ONLY raw <svg> code.",
            prompt=state.get("creative_brief", "")
        )

    try:
        resp = await retry_with_backoff(
            lambda att: with_timeout(make_call(att), timeout_s=25.0)
        )
        return {
            "final_response": clean_svg(resp["content"]),
            "current_step": "finalize"
        }
    except Exception as e:
        return {"last_error": str(e), "current_step": "error"}


def route_safety(state: AgentState) -> str:
    """Routing logic for Lab 7 safety checkpoints."""
    if state.get("current_step") == "error":
        return "end"

    # If use_pro_model is True but not approved, halt.
    if check_safety(state) and not state.get("approved"):
        return "end"

    return "artist"


def build_vector_graph():
    # Using 'dict' as the schema type often fixes PyCharm's linter warnings
    builder = StateGraph(AgentState)
    builder.add_node("creative", creative_node)
    builder.add_node("artist", artist_node)
    builder.add_edge(START, "creative")
    builder.add_conditional_edges("creative", route_safety, {"end": END, "artist": "artist"})
    builder.add_edge("artist", END)
    return builder.compile()
