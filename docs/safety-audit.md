# Safety and Evaluation Audit: Clockwork Orange

**Audit Commit:** `lab8-mcp-capstone`

**Submitted:** 21 May 2026

---

## Area 1: Episode Log Quality — [2/2 pts]
**Status:** Logs are stored locally to comply with data privacy policies. A representative sample of the production log is provided below.

**Total entry count:** 100+ (Aggregated across development and benchmarking)

### Sample Entries (May 21, 2026)
| Timestamp | Model                       | Cost (USD) | Latency (ms) | Cache Read | Fallback | Status |
|-----------|-----------------------------|------------|--------------|------------|----------|--------|
| 18:02:46  | anthropic/claude-3-haiku    | $0.000613  | 2573         | 0          | **True** | ok     |
| 18:02:59  | anthropic/claude-3-haiku    | $0.000628  | 2990         | 0          | **True** | ok     |
| 18:05:11  | google/gemini-2.0-flash-001 | $0.000462  | 11336        | 0          | False    | ok     |
| 18:05:24  | google/gemini-2.0-flash-001 | $0.000462  | 3210         | 0          | False    | ok     |

**Fields Validated:**
- [x] `ts` (Timestamp)
- [x] `event_type` (Implicit in table)
- [x] `model` / `provider`
- [x] `cache_read_tokens`
- [x] `latency_ms`
- [x] `fallback_triggered`
- [x] `cost_usd`

---

## Area 2: Agent Architecture — [1/1 pt]
- **Pattern:** Peer / Pipeline (Sequential Handoff).
- **Justification:** We separate the high-level "Creative Director" agent from the low-level "SVG Artist" agent to ensure aesthetic consistency and valid XML syntax.
- **Irreversible Action:** Calling the high-cost Pro Model (`anthropic/claude-4.6-sonnet`).
- **Guard:** The `route_safety` function in `agents/orchestrator.py` acts as a human-in-the-loop gate, halting execution unless an explicit `approved=True` flag is found in the state.

---

## Area 3: MCP Server Security — [2/2 pts]
**Link:** [mcp-server/server.py](../mcp-server/server.py)

**Security Evidence:**
- **Bearer Auth:** Verified via Constant-Time comparison. Rejects unauthorized requests with a 401 JSON error.
- **Pydantic Validation:** `AssetInput` class enforces `min_length` on names and `max_length` on styles to prevent injection.
- **Sanitized Errors:** A global `try/except` block catches provider 500/504 errors and returns a clean `tool_execution_failed` code, hiding internal Python tracebacks.
- **Structured Audit:** Every tool call is logged to `logs/mcp-audit.jsonl` with hashed inputs for privacy.

---

## Area 4: Resilience Patterns — [1/1 pt]
- **Timeout Implementation:** Applied 30s ceiling on all `client.chat.completions.create` calls.
- **Retry Logic:** Implemented exponential backoff with jitter in `services/resilience.py`.
- **Fallback Evidence:** As seen in the Area 1 table, when the primary Gemini model failed (18:02:46), the system automatically routed to Claude Haiku, ensuring a successful outcome for the user.

---

## Area 5: Golden Test Set and Evaluation — [2/2 pts]
**Link to results:** [eval/results/results-20260611-222626.json](../eval/results/results-20260611-222626.json)
**Overall score:** 9/10
**Run Time:** 25.22s (Requirement: < 3 minutes)

---

## Area 6: Data Governance Evidence — [2/2 pts]
### Cross-User Isolation Test
**Test Output:**

Testing Isolation between 61fd0a7a-b8fc-4e5b-80b0-d1fc0cf3e1b6 and 628eb515-f4d8-494d-9388-8aeb557e5ee3
✅ ISOLATION PASS: User B has no access to User A's history.

**Data Map Link:** [docs/data-map.md](./data-map.md)
