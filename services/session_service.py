"""
Session Service — VectorFlow Lab 6
In-memory conversation state management with sliding window trimming.
"""

_sessions: dict[str, list] = {}
MAX_TURNS = 20  # Keep last 20 turns (40 messages) + system prompt


def load_session(session_id: str) -> list:
    return list(_sessions.get(session_id, []))  # Return a copy of the message history for this session.


def save_session(session_id: str, messages: list) -> None:
    _sessions[session_id] = _trim(messages)  # Save history with a sliding window trim.


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)  # Wipe history for a specific session.


def _trim(messages: list) -> list:
    """Keeps system prompt at index 0 and trims the rest."""
    system_messages = [m for m in messages if m.get("role") == "system"]
    non_system = [m for m in messages if m.get("role") != "system"]

    max_non_system = MAX_TURNS * 2

    # Slice the non_system list to the allowed max
    trimmed_non_system = non_system[-max_non_system:] if len(non_system) > max_non_system else non_system

    return system_messages + trimmed_non_system
