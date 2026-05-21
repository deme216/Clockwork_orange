# Lab 7 Close-Out Checklist

**Team name:** Clockwork Orange

**Date:** Friday 24 April 2026

## Architecture
- [x] Pattern: Peer / Pipeline (Sequential Handoff).
- [x] Defined `AgentState` with session_id, creative_brief, and retry metadata.

## Resilience
- [x] Every LLM call has a timeout (10s for creative, 25s for artist).
- [x] Exponential backoff retries implemented (3 attempts).

## Safety
- [x] Identified Pro Model usage as the highest-risk action.
- [x] Human approval gate added via `route_safety` conditional edge.

## Mini-Build
- [x] Successfully ran LangGraph orchestration proof in `test_lab7.py`.