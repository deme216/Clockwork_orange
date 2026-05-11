# Design Decisions — Lab 5

**Team Name:** Clockwork Orange

**Team Members:** Saba Morchilashvili, Demetre Mikeladze, Elguja Tsitaishvili

**Date:** Friday 10 April 2026

## Section 1: Design Review Feedback Acknowledgement

### Feedback Item 1
**Feedback received:** "SVG code hallucination is a high risk; how will you prevent the UI from crashing?"

**Our decision:** We implemented a modular `llm_service.py` that includes a regex-based `_clean_svg` function to strip markdown fences and non-XML text.

**Impact on our design:** The system is now robust against "chatty" AI responses. We also added an XML validation step to catch malformed code before it reaches the frontend.

### Feedback Item 2
**Feedback received:** "The cost of using Claude 3.5 Sonnet for every test will burn the $30 budget too fast."

**Our decision:** We implemented a "Hybrid Tier" toggle in our `AssetRequest` model.

**Impact on our design:** Developers use Gemini 3.1 Flash Lite by default (near-zero cost). The high-fidelity Claude 4.6 Sonnet model is only triggered when the `use_pro` flag is set to true.

---

## Section 2: What We Are Keeping
| Decision               | Reason we are keeping it                                                                                           |
|------------------------|--------------------------------------------------------------------------------------------------------------------|
| Streamlit Frontend     | Enables 100% Python development, accelerating our UI iteration.                                                    |
| Multi-Agent Handoff    | Separating 'Creative Intent' from 'SVG Coding' significantly improved the artistic detail of generated shields.    |
| Separation of Concerns | Using the `routers/`, `models/`, and `services/` structure ensures the code is maintainable for the full 15 weeks. |

---

## Section 3: Today's Prototype Milestone
**The one feature we are building today:**
A modular FastAPI POST route at `/api/generate/svg` that orchestrates a multi-agent handoff between a Creative Agent (Gemini) and an Artist Agent (Claude/Gemini) to return a cleaned, renderable SVG.

**How we will know it is working:**
A successful request to the endpoint returns a JSON object with a clean SVG string (no backslashes or markdown) and a total cost calculation.

---

## Section 4: Technical Decisions for Today
**Which model are you using for the sprint?**
- Creative Agent: `google/gemini-3.1-flash-lite`
- Artist Agent: `google/gemini-flash-latest` (with `anthropic/claude-4.6-sonnet` for Pro mode)

**Which stack scaffold are you using?**
Custom modular FastAPI stack (Python 3.11).

**What is the output your endpoint will return?**
A JSON object: `{"svg": str, "brief": str, "model_used": str, "latency_ms": int, "cost_usd": float}`.

---

## Section 5: Dependency Declaration
| Dependency        | Purpose                     | Fallback             |
|-------------------|-----------------------------|----------------------|
| OpenRouter API    | AI model orchestration      | Google AI Studio     |
| FastAPI / Uvicorn | Web server and routing      | Flask                |
| Pydantic          | Data validation and schemas | Standard Dicts       |
| python-dotenv     | Secure API key management   | Hardcoded (Dev only) |
