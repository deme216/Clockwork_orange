from typing import TypedDict, List, Dict


class AgentState(TypedDict, total=False):
    session_id: str
    user_request: str
    messages: List[Dict[str, str]]
    current_step: str
    approval_required: bool
    approved: bool | None
    retry_count: int
    timeout_ms: int
    last_error: str | None
    final_response: str | None  # This will hold our final SVG code

    # VectorFlow Specific Fields
    style_context: str
    creative_brief: str | None
    use_pro_model: bool
    svg_valid: bool
