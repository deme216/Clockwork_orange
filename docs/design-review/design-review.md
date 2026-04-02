# Design Review: VectorFlow

**Course:** CS-AI-2025 — Building AI-Powered Applications | Spring 2026

**Team Name:** Clockwork Orange

**Team Members:** Saba Morchilashvili | Demetre Mikeladze | Elguja Tsitaishvili

**Team Lead:** Saba Morchilashvili

**Submission Due:** Thursday 2 April 2026

---

## Section 1: Problem Statement and Real User Need

### 1.1 — Who has this problem?
Indie game developers and solo "game jam" participants who can code game logic but cannot draw. Specifically,
those who need rapid prototyping assets that look consistent.

### 1.2 — What is the problem?
Generating game assets is a split-brain task. You need a "Creative Director" to decide the look and an "Artist" to
execute it. Most AI tools only do the execution, leaving the user to struggle with writing the perfect prompt to get
a consistent style.

### 1.3 — How do they currently solve it?
They use generic asset packs (which don't match) or spend hours "prompt engineering" a single image generator,
often failing to get a consistent style across multiple items.

### 1.4 — What is the cost of this problem?
- **Time:** Hours spent tweaking prompts.
- **Visual Friction:** Games look amateur because the hero is "pixel art" but the background is "realistic."

---

## Section 2: Proposed Solution and AI-Powered Differentiator

### 2.1 — What does your application do?
VectorFlow uses a two-stage pipeline. The user defines a "Game Bible" (e.g., "Neon Space"). The **Creative Agent** acts
as a consultant, refining user ideas into technical artist prompts. The **Artist Agent** then generates the file.
This ensures that every asset generated for that "Game Bible" shares the same visual DNA.

### 2.2 — Core features
| Feature                | What the user can do                       | Why this matters                                     |
|------------------------|--------------------------------------------|------------------------------------------------------|
| 1. Style Locker        | Set a theme once for the whole project.    | Guarantees all assets look consistent.               |
| 2. SVG Generator       | Generate scalable code-based icons.        | Perfect for UI and low-file-size games.              |
| 3. Agent-to-Agent Chat | Watch the two agents "discuss" the design. | Reduces the need for the user to be a prompt expert. |

### 2.3 — The AI-powered differentiator
The **Multi-Agent Handoff**. By separating "What should we build?" from "How do we draw it?", we use the reasoning power
of Claude 3.5 Sonnet to improve the creative output of the image generator.

---

## Section 3: Technical Architecture

### 3.1 — Technology Stack
| Layer           | Technology                                                             | Why this choice                                                                                                                                                                         |
|-----------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Frontend/UI     | **Streamlit**                                                          | 100% Python. Fastest way to build a dashboard without over-engineering.                                                                                                                 |
| Backend         | **FastAPI**                                                            | Lightweight and handles asynchronous AI calls well.                                                                                                                                     |
| AI Access       | **OpenRouter**                                                         | Single API for switching between Claude (for SVG) and Flux (for PNG).                                                                                                                   |
| AI Models       | Hybrid Tier: **Gemini 1.5 Flash (Free)** + **Claude 3.5 Sonnet (Pro)** | Gemini 1.5 Flash (:free) will be used for 90% of development/debugging to preserve budget. Claude 3.5 Sonnet will be reserved for high-complexity SVG generation during the final demo. |
| Data Efficiency | Local JSON Caching                                                     | To prevent redundant API calls and credit burn, previously generated assets will be cached locally during the development phase.                                                        |
| Language        | **Python 3.11**                                                        | Required for AI agent libraries.                                                                                                                                                        |

### 3.2 — Core Data Flow
1. User enters: "I need a sword."
2. **Creative Agent** looks at the "Style Locker" (e.g., "Cyberpunk") and generates a 50-word technical art description.
3. **Artist Agent** receives this description and outputs a raw SVG code block.
4. **Python Parser** strips the markdown and saves the string as `asset.svg`.
5. **Streamlit** renders the SVG using an HTML component.

---

## Section 4: Risk and Failure Mode Analysis

### Risk 1: Invalid SVG Hallucination
**What happens when this occurs:** The Artist Agent generates code that isn't valid XML (e.g., missing tags or improper nesting),
resulting in a broken image or a console error.
**Likelihood:** Medium
**Impact on user:** High (The asset will not render in the preview window).
**Mitigation strategy:** Use a Python-based XML validator (like `xml.etree.ElementTree`) to verify the string before it
hits the frontend. If invalid, the system will automatically send a "Retry" prompt to the agent with a
temperature of 0 to force a strict correction.

### Risk 2: API Budget Exhaustion ($30 Limit)
**What happens when this occurs:** High-cost models (like Claude 3.5 Sonnet) or image-generation models (like Flux)
consume the instructor's credit before the final demo.
**Likelihood:** High (if testing without limits).
**Impact on user:** Critical (System shuts down).
**Mitigation strategy:** Implement a **Tiered Model Strategy**. We will use the `google/gemini-flash-1.5-free`
endpoint for 90% of development and logic testing. We will only switch to Claude 3.5 Sonnet for the final "Artist"
output during the demo phase.

### Risk 3: High Latency in Multi-Agent Handoff
**What happens when this occurs:** The "Creative Agent" + "Artist Agent" pipeline takes 15-25 seconds to complete,
leading the user to believe the app is frozen.
**Likelihood:** High
**Impact on user:** Medium (Frustrating UX).
**Mitigation strategy:** Use **Streamlit’s `st.status` containers** to provide "Live Reasoning" updates.
The UI will show exactly what is happening: "🤖 Creative Agent is brainstorming style..." → "🎨 Artist Agent is
writing SVG code..." This manages user expectations through visual feedback.

### Risk 4: Style Inconsistency
**What happens when this occurs:** New assets generated for the same "Game Bible" look visually different from the previous ones.
**Likelihood:** Medium
**Impact on user:** High (Ruins the game's aesthetic).
**Mitigation strategy:** The **Creative Agent** will generate a permanent "Style Brief" for each project.
This text block will be injected into every subsequent "Artist Agent" call as a `system_prompt` to
ensure consistent color palettes and stroke weights.

---

## Section 5: Team Roles and Week-by-Week Plan (1.5 pts)

### 5.1 — Team Roles

| Team Member         | Primary Role          | Secondary Role    | What they own                                                    |
|---------------------|-----------------------|-------------------|------------------------------------------------------------------|
| Saba Morchilashvili | AI Pipeline Architect | Backend Developer | Multi-agent orchestration, OpenRouter API logic, SVG validation. |
| Demetre Mikeladze   | Frontend Lead         | UI/UX Designer    | Streamlit dashboard, SVG rendering, Export/Download features.    |
| Elguja Tsitaishvili | Data & DevOps         | QA Tester         | Caching logic (JSON), Style Brief storage, prompting benchmarks. |

### 5.2 — Week-by-Week Plan

| Week | Dates  | What you will build / complete                               | Who leads           | Risk level |
|------|--------|--------------------------------------------------------------|---------------------|------------|
| 3    | 27 Mar | Lab 3: Basic Streamlit UI + Gemini Free API link.            | Saba Morchilashvili | Low        |
| 4    | 3 Apr  | **Design Review Due (2 Apr).** Image upload for sketches.    | Demetre Mikeladze   | Medium     |
| 5    | 10 Apr | Multi-agent Handoff: Creative Agent feeds the Artist Agent.  | Saba Morchilashvili | **High**   |
| 6    | 17 Apr | SVG Parser: Extracting XML from AI markdown and rendering.   | Elguja Tsitaishvili | Medium     |
| 7    | 24 Apr | Style Locker: Implementing the permanent "Game Bible" logic. | Saba Morchilashvili | Medium     |
| 8    | 1 May  | PNG Support: Integrating Flux/SDXL via OpenRouter.           | Demetre Mikeladze   | Medium     |
| 9    | 8 May  | **Midterm week** (Testing and Debugging).                    | Whole team          | Low        |
| 11   | 22 May | Safety Audit & FinOps: Optimizing token usage for demo.      | Saba Morchilashvili | **High**   |
| 12   | 29 May | **Demo Day Prep:** Final UI polish and asset gallery view.   | Whole team          | Medium     |

### 5.3 — Honest Assessment
**What is the hardest week in your plan?** 
Week 5 (Agent Handoff). Ensuring the Creative Agent’s output is structured well enough for the Artist Agent to produce
valid SVG code without human intervention is the core technical challenge.

**What is the biggest technical risk between now and Demo Day?** 
The **"Quality vs. Cost"** trade-off. We must ensure our prompts are robust enough to work on free models (Gemini Flash)
during development while still being able to leverage the power of paid models (Claude) for the final presentation.

---

## Section 6: IRB-Light Checklist (0.5 pts)

| Question                                        | Answer     | If yes: explain                                                    |
|-------------------------------------------------|------------|--------------------------------------------------------------------|
| 1. Does your app collect images of real people? | No         |                                                                    |
| 2. Does your app process photographs of faces?  | No         |                                                                    |
| 3. Does your app handle sensitive documents?    | No         |                                                                    |
| 4. Does your app store user-uploaded data?      | Yes        | We store user sketches (temporarily) and generated SVG/PNG assets. |
| 5. If storing data: for how long and where?     | 1 Semester | Stored in a local `assets/` folder or a lightweight JSON cache.    |
| 6. Do users need to give informed consent?      | Yes        | A "Terms of Use" footer on the Streamlit app.                      |

**If any answers above are "yes":** 
Users will be notified that any sketches they upload are processed by Google (Gemini) or Anthropic (Claude) APIs.
No personal identification data is stored; we only save the artistic content generated to provide a "Project History" for the user.

---
