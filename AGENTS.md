# Agent Instructions: VectorFlow

This repository is optimized for collaboration with AI coding agents (Cursor, Claude Code, etc.).

## Project Structure
- `main.py`: FastAPI entry point and middleware configuration.
- `agents/orchestrator.py`: LangGraph state machine logic.
- `services/llm_service.py`: Model fallback logic and SVG regex cleaning.
- `services/rate_limiter.py`: Token bucket implementation.
- `streamlit_app.py`: Frontend UI.

## Technical Standards
1. **Type Safety**: Always use Python 3.14+ type hinting (e.g., `str | None`).
2. **Resilience**: All external model calls must be wrapped in `retry_with_backoff` from `services/resilience.py`.
3. **SVG Handling**: Never return raw AI output to the frontend; always pass it through `clean_svg()` first.
4. **Observability**: Every LLM interaction must update the `CallRecord` and be appended to the episode log.
