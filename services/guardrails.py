from models.agent_state import AgentState


def check_safety(state: AgentState) -> bool:
    """
    Returns True if the action requires human approval.
    Rule: Any request using the Pro model (Claude 4.6) requires approval.
    """
    return state.get("use_pro_model", False)


def get_approval_message(state: AgentState) -> str:
    return (
        f"CONFIRMATION REQUIRED: This request for a '{state['user_request']}' "
        "will use the Pro Model (Claude 4.6 Sonnet). Confirm expenditure?"
    )
