# Agent Architecture: VectorFlow

## 1. Chosen Pattern
**Pattern name:** Peer / Pipeline (Sequential Handoff)

## 2. Rationale
VectorFlow solves a visual consistency coordination problem. A single prompt often leads the model to "chat" rather
than "code." Our pipeline separates the **Creative Design** (textual) from the **Technical Implementation** (SVG XML).
The Peer / Pipeline pattern is ideal because the output of the Creative Agent is the necessary input for the Artist Agent.

## 3. Resilience Policy
- **Timeout:** 8,000ms for Flash models; 45,000ms for Claude Pro models.
- **Retries:** 3 attempts with exponential backoff (multiplier 2x).
- **Triggers:** Retries on 429 (Rate Limit) and 500 (Provider Error).

## 4. Safety Checkpoint
- **Risky Action:** Invoking the Pro Model (`anthropic/claude-4.6-sonnet`).
- **Why:** This is a high-cost action that can rapidly deplete the $30 budget.
- **Checkpoint:** If `use_pro_model` is detected, the flow redirects to a `human_approval` step.