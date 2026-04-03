# Design Review: VectorFlow

**Course:** CS-AI-2025 — Building AI-Powered Applications | Spring 2026

**Team Name:** Clockwork Orange

**Team Members:** Saba Morchilashvili | Demetre Mikeladze | Elguja Tsitaishvili

**Team Lead:** Saba Morchilashvili

**Submission Due:** Thursday 2 April 2026

---

## Section 1: Problem Statement and Real User Need

### 1.1 — Who has this problem?

Indie game developers and solo "game jam" participants who can code game logic but cannot draw. Specifically, those who need rapid prototyping assets that look consistent across an entire project.

### 1.2 — What is the problem?

Generating game assets is a split-brain task. You need a "Creative Director" to decide the look and an "Artist" to execute it. Most AI tools only do the execution, leaving the user to struggle with writing the perfect prompt to get a consistent style.

### 1.3 — How do they currently solve it?

They use generic asset packs (which don't match their art style) or spend hours "prompt engineering" a single image generator, often failing to get a consistent style across multiple items.

### 1.4 — What is the cost of this problem?

Time: Hours spent tweaking prompts per asset. Visual friction: Games look amateur because the hero is "pixel art" but the background is "realistic." Missed deadlines: Game jam participants (typically 48–72 hour events) lose critical hours on art instead of gameplay.

---

## Section 2: Proposed Solution and AI-Powered Differentiator

### 2.1 — What does your application do?

VectorFlow uses a two-stage multi-agent pipeline. The user defines a "Game Bible" (e.g., "Neon Space"). The Creative Agent acts as a consultant, refining user ideas into technical artist prompts. The Artist Agent then generates the file. This ensures that every asset generated for that "Game Bible" shares the same visual DNA.

### 2.2 — Core features

| Feature             | What the user can do                           | Why this matters                                     |
| ------------------- | ---------------------------------------------- | ---------------------------------------------------- |
| Style Locker        | Set a theme once for the whole project.        | Guarantees all assets look consistent.               |
| SVG Generator       | Generate scalable code-based icons and assets. | Perfect for UI and low-file-size games.              |
| Agent-to-Agent Chat | Watch the two agents "discuss" the design.     | Reduces the need for the user to be a prompt expert. |

### 2.3 — The AI-powered differentiator

The Multi-Agent Handoff. By separating "What should we build?" from "How do we draw it?", we use the reasoning power of an LLM (Claude 3.5 Sonnet) to improve the creative output of the generation step. Unlike single-prompt tools, the Creative Agent translates vague user intent into precise technical art direction before anything is drawn.

---

## Section 3: Measurable Success Criteria

### Criterion 1 — SVG validity rate

The Artist Agent produces valid, renderable SVG code (passes `xml.etree.ElementTree` parsing and contains at least one visible shape element) in at least 85% of generation attempts, tested across a 20-prompt benchmark set covering five asset categories: weapons, characters, UI icons, environment objects, and vehicles.

### Criterion 2 — Pipeline latency

90% of full pipeline requests (Creative Agent → Artist Agent → rendered preview) complete within 15 seconds end-to-end, measured from the moment the user clicks "Send" to the moment the SVG appears in the preview panel, tested on a standard home internet connection.

### Criterion 3 — Style consistency

When generating 5 different assets under the same Style Locker configuration, at least 4 out of 5 use the same color palette (matching hex values specified in the Style Brief) as verified by manual inspection.

---

## Section 4: Technology Stack

| Layer           | Technology                                                     | Why this choice                                                                                                                                                         |
| --------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend/UI     | Streamlit                                                      | 100% Python. Fastest way to build a dashboard without over-engineering.                                                                                                 |
| Backend         | FastAPI                                                        | Lightweight and handles asynchronous AI calls well.                                                                                                                     |
| AI Access       | OpenRouter                                                     | Single API for switching between Claude (for SVG) and Flux (for PNG).                                                                                                   |
| AI Models       | Hybrid Tier: Gemini 1.5 Flash (Free) + Claude 3.5 Sonnet (Pro) | Gemini 1.5 Flash will be used for 90% of development/debugging to preserve budget. Claude 3.5 Sonnet reserved for high-complexity SVG generation during the final demo. |
| Data Efficiency | Local JSON Caching                                             | To prevent redundant API calls and credit burn, previously generated assets will be cached locally.                                                                     |
| Language        | Python 3.11                                                    | Required for AI agent libraries.                                                                                                                                        |

---

## Section 5: Prompt and Data Flow

**Feature being traced:** SVG game asset generation via multi-agent pipeline

### Step 1 — User Action

The user types a natural-language asset request (e.g., "I need a sword") into the prompt input field on the main Streamlit dashboard screen and clicks the **Send** button. The "Game Theme" dropdown is already set (e.g., "Cyberpunk") and the Style Locker may contain additional locked style details (e.g., "neon glow, thin outlines, dark background palette").

### Step 2 — Preprocessing

The user's text prompt is trimmed of leading and trailing whitespace and checked for minimum length (at least 3 characters). If the prompt is shorter than 3 characters, the UI displays an inline message: "Please describe the asset you need" and the request is not sent. The Style Locker text and the selected Game Theme are read from the Streamlit session state and concatenated into a single style context string. Before making any API call, the backend checks the local JSON cache (`assets/cache.json`) for an identical prompt + style combination. If a cache hit is found, the cached SVG is returned directly and Steps 3–6 are skipped.

### Step 3 — Prompt Construction

**Stage A — Creative Agent prompt:**

System prompt: "You are a senior creative director for video games. You will receive a game theme, a style brief, and a user's asset request. Your job is to write a detailed 50-word technical art description that a digital artist could follow to draw the asset. Specify: shape, color palette (as hex codes), stroke weight, perspective, and level of detail. Do not draw anything — only describe. Respond with the description only, no preamble."

User message content: "Game Theme: Cyberpunk. Style Brief: neon glow, thin outlines, dark background palette. Asset request: I need a sword."

**Stage B — Artist Agent prompt (constructed after Stage A returns):**

System prompt: "You are a vector artist. You receive a technical art description. Generate a single valid SVG image that matches the description exactly. Output only raw SVG XML code starting with `<svg` and ending with `</svg>`. Do not include markdown fences, explanations, or any text outside the SVG tags. Use a viewBox of 0 0 512 512."

User message content: The full 50-word art description returned by the Creative Agent in Stage A (e.g., "A futuristic katana with a glowing cyan blade (#00FFFF), thin white outlines (#FFFFFF, stroke-width 1.5), dark gunmetal crossguard (#2C3E50), viewed from a 3/4 angle, minimal detail, flat shading, no background.").

### Step 4 — API Call

**Stage A — Creative Agent:**

- Model: `google/gemini-flash-1.5` (free tier) via OpenRouter (`https://openrouter.ai/api/v1`)
- Parameters: `max_tokens=256`, `temperature=0.7` (higher creativity for style interpretation)
- Timeout: 8 seconds

**Stage B — Artist Agent:**

- Model: `anthropic/claude-3.5-sonnet` via OpenRouter (`https://openrouter.ai/api/v1`)
- Parameters: `max_tokens=4096` (SVG code can be long), `temperature=0` (strict adherence to the art description)
- Timeout: 15 seconds (SVG generation takes longer)

If either call times out, the pipeline stops and triggers the API failure fallback path (see Step 7).

### Step 5 — Response Parsing

**Stage A — Creative Agent:**
The API returns a text string in `response.choices[0].message.content`. We verify it is non-empty and between 30 and 300 characters. If it is empty or outside that range, the pipeline stops and triggers the low-confidence fallback.

**Stage B — Artist Agent:**
The API returns a text string containing SVG code. We extract the SVG by finding the substring between the first `<svg` and the last `</svg>` (inclusive). This handles cases where the model wraps the SVG in markdown fences or adds preamble text. The extracted string is then validated using Python's `xml.etree.ElementTree.fromstring()`. If XML parsing raises an `ET.ParseError`, the system automatically retries the Artist Agent call once with `temperature=0` and an appended instruction: "Your previous output was not valid XML. Output only valid SVG." If the retry also fails XML validation, the pipeline triggers the low-confidence fallback.

### Step 6 — Confidence or Validation

We use a two-check heuristic (there is no explicit confidence score from the API):

1. **XML validity check:** The SVG string must parse without errors via `xml.etree.ElementTree`. Pass = valid SVG. Fail = trigger retry (one attempt), then fallback.
2. **Content check:** The parsed SVG must contain at least one visible drawing element (`<path>`, `<rect>`, `<circle>`, `<polygon>`, or `<line>`). An SVG that is technically valid XML but contains only an empty `<svg></svg>` tag with no shapes fails this check.

If both checks pass → show the SVG directly (success path). If XML validity fails after retry → show the generation failure fallback. If content check fails → show the low-confidence fallback with a "Try again" option.

### Step 7 — User Output

**Success path:**
The generated SVG is rendered in the "Asset Preview" panel on the right side of the Streamlit dashboard using `st.components.v1.html()`. The Creative Agent's art description is displayed in the center "Creative Agent" chat panel so the user can see what style decisions were made. A green **Download SVG** button appears below the preview. The prompt, style context, and SVG code are saved to the local JSON cache for future reuse.

**Fallback path — API failure (timeout or network error):**
The loading spinner is replaced with an amber banner in the preview panel reading: "Could not generate your asset right now — please try again in a moment." A **Try Again** button appears below the message that resubmits the same request. The user's prompt text remains in the input field and is not cleared. No error codes, HTTP status numbers, or the word "error" are shown.

**Fallback path — Low confidence (invalid or empty SVG after retry):**
The preview panel displays: "The generated asset did not come out right. Try rephrasing your request or adding more detail (e.g., 'a short broadsword with a wide blade')." A **Try Again** button and a **Change Theme** link (which scrolls to the Style Locker) are shown. The Creative Agent's description is still displayed so the user can see what interpretation caused the issue and adjust accordingly.

---

## Section 6: Architecture Diagram

See `architecture-diagram.png` in this folder.

The diagram shows five required elements: Streamlit UI (frontend), FastAPI (backend), Gemini 1.5 Flash and Claude 3.5 Sonnet via OpenRouter (named AI models), Local JSON Cache (storage), and directional arrows between all connected components. The Creative Agent and Artist Agent are shown as separate model calls, with the multi-agent handoff represented by the arrow passing the art description from Stage A to Stage B.

---

## Section 7: Safety Threats and Fallback UX

### 7.1 — Threat Table

| Threat                                                                                                              | Relevant to our product? | Our mitigation                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prompt injection** — user input overrides system instructions                                                     | Yes                      | User text is inserted only into the `user` message, never concatenated into the system prompt. The system prompt is a separate, fixed message in the API call. User input is length-limited to 500 characters and stripped of any markdown code fences before insertion.                                                                            |
| **Hallucination in high-stakes output** — model returns confident wrong answers in a consequential context          | Partial                  | Our output is visual art, not factual information, so "hallucination" manifests as invalid SVG code rather than dangerous misinformation. We mitigate this with XML validation via `xml.etree.ElementTree` and an automatic single retry on parse failure (see Data Flow Step 5).                                                                   |
| **Bias affecting specific user groups** — systematically different output quality by language, name, or demographic | Partial                  | Asset requests are in English and describe objects (swords, shields, icons), not people. However, if a user requests a character sprite, the model may default to stereotypical representations. We mitigate by including "do not assume gender, ethnicity, or cultural markers unless explicitly specified" in the Creative Agent's system prompt. |
| **Content policy violation** — user-submitted prompts trigger content filters                                       | Yes                      | Users could request violent or explicit assets (e.g., gore-themed weapons). If the API returns a content filter refusal, the UI displays: "That request could not be processed. Try describing a different style or asset." We do not reveal the phrase "content policy" or "blocked" to the user.                                                  |
| **Privacy violation** — user data sent to third-party APIs without adequate disclosure                              | Yes                      | User prompts and style configurations are sent to Google (Gemini) and Anthropic (Claude) via OpenRouter. A footer on the Streamlit app states: "Your prompts are processed by third-party AI services (Google and Anthropic). No personal identification data is collected." No login or account data is required to use the app.                   |
| **Data exfiltration** — malicious prompt causes model to reveal other users' data or internal config                | No                       | VectorFlow is a single-user local application with no shared database. There is no multi-user data store, so there is no other user's data to exfiltrate. The JSON cache is stored locally on the user's own machine. The API key is stored in a `.env` file excluded from version control via `.gitignore`.                                        |

### 7.2 — Top Risk

Our biggest safety concern is **invalid SVG hallucination** because a malformed SVG could, in a worst case, contain embedded JavaScript (`<script>` tags inside SVG XML) that executes when rendered in the browser via Streamlit's HTML component. We mitigate this by stripping any `<script>`, `<foreignObject>`, and `on*` event attributes from the parsed SVG tree before rendering.

### 7.3 — Fallback UX

**Scenario: API failure (timeout, 500 error, or network unavailable)**

The user sees: the loading spinner in the Asset Preview panel is replaced by a soft amber banner. The message reads: "Could not generate your asset right now — please try again in a moment." The action available to the user: a "Try Again" button that resubmits the identical request. The user's prompt text remains in the input field and is not cleared. What is NOT shown: stack traces, error codes, HTTP status numbers, the word "error," or any mention of "AI."

**Scenario: Low-confidence output (invalid or empty SVG after retry)**

The user sees: the Asset Preview panel displays a light amber background instead of the SVG. The message reads: "The generated asset did not come out right. Try rephrasing your request or adding more detail (e.g., 'a short broadsword with a wide blade')." The action available to the user: a "Try Again" button and a "Change Theme" link that scrolls to the Style Locker panel. The Creative Agent's text description remains visible so the user can see what interpretation went wrong. What is NOT shown: XML parsing errors, retry counts, model names, or the phrase "validation failed."

**Scenario: Content filter rejection**

The user sees: the Asset Preview panel shows the message: "That request could not be processed — try describing a different style or asset." The action available to the user: editing their prompt and resubmitting. What is NOT shown: the words "content policy," "blocked," "rejected," or "violation."

**One-paragraph summary:**
The user sees an amber-toned message in the preview panel whenever the AI cannot produce a usable asset, with plain-language guidance on what to do next (retry, rephrase, or adjust the style). A "Try Again" button is always available, the user's original prompt is never lost, and no technical jargon, error codes, or AI terminology is displayed at any point.

---

## Section 8: Data Governance

**1. What user data does your app collect or process?**
User-typed text prompts (asset descriptions), selected game themes, Style Locker text, and the generated SVG/PNG output files.

**2. Where is it stored?**
Locally on the user's machine in an `assets/` folder and a `cache.json` file. No cloud database is used. No data is stored on a remote server by our application.

**3. How long is it retained?**
For the duration of the semester (development and demo period). Users can delete the `assets/` folder and `cache.json` at any time to remove all stored data.

**4. Who has access to it?**
Only the user running the application on their local machine, and the development team (for grading and debugging purposes during the course).

**5. How can a user request deletion?**
By deleting the local `assets/` folder and `cache.json` file. Since there is no remote storage or user accounts, no formal deletion request process is needed.

**6. Does your app send user data to third-party AI APIs? Which ones?**
Yes. User text prompts and style configurations are sent to Google (Gemini 1.5 Flash) and Anthropic (Claude 3.5 Sonnet) via the OpenRouter API for processing. Generated images are returned to the user's local machine. No personal identification data is included in API calls.

---

## Section 9: Team Roles and Week-by-Week Plan

### 9.1 — Team Roles

| Team Member         | Primary Role          | Secondary Role    | What they own                                                    |
| ------------------- | --------------------- | ----------------- | ---------------------------------------------------------------- |
| Saba Morchilashvili | AI Pipeline Architect | Backend Developer | Multi-agent orchestration, OpenRouter API logic, SVG validation. |
| Demetre Mikeladze   | Frontend Lead         | UI/UX Designer    | Streamlit dashboard, SVG rendering, Export/Download features.    |
| Elguja Tsitaishvili | Data & DevOps         | QA Tester         | Caching logic (JSON), Style Brief storage, prompting benchmarks. |

### 9.2 — Week-by-Week Plan

| Week | Dates  | What you will build / complete                               | Who leads           | Risk level |
| ---- | ------ | ------------------------------------------------------------ | ------------------- | ---------- |
| 3    | 27 Mar | Lab 3: Basic Streamlit UI + Gemini Free API link.            | Saba Morchilashvili | Low        |
| 4    | 3 Apr  | Design Review Due (2 Apr). Image upload for sketches.        | Demetre Mikeladze   | Medium     |
| 5    | 10 Apr | Multi-agent Handoff: Creative Agent feeds the Artist Agent.  | Saba Morchilashvili | High       |
| 6    | 17 Apr | SVG Parser: Extracting XML from AI markdown and rendering.   | Elguja Tsitaishvili | Medium     |
| 7    | 24 Apr | Style Locker: Implementing the permanent "Game Bible" logic. | Saba Morchilashvili | Medium     |
| 8    | 1 May  | PNG Support: Integrating Flux/SDXL via OpenRouter.           | Demetre Mikeladze   | Medium     |
| 9    | 8 May  | Midterm week (Testing and Debugging).                        | Whole team          | Low        |
| 11   | 22 May | Safety Audit & FinOps: Optimizing token usage for demo.      | Saba Morchilashvili | High       |
| 12   | 29 May | Demo Day Prep: Final UI polish and asset gallery view.       | Whole team          | Medium     |

### 9.3 — Honest Assessment

**What is the hardest week in your plan?** Week 5 (Agent Handoff). Ensuring the Creative Agent's output is structured well enough for the Artist Agent to produce valid SVG code without human intervention is the core technical challenge.

**What is the biggest technical risk between now and Demo Day?** The "Quality vs. Cost" trade-off. We must ensure our prompts are robust enough to work on free models (Gemini Flash) during development while still being able to leverage the power of paid models (Claude) for the final presentation.

---

## Section 10: IRB-Light Checklist

| Question                                        | Answer     | If yes: explain                                                    |
| ----------------------------------------------- | ---------- | ------------------------------------------------------------------ |
| 1. Does your app collect images of real people? | No         |                                                                    |
| 2. Does your app process photographs of faces?  | No         |                                                                    |
| 3. Does your app handle sensitive documents?    | No         |                                                                    |
| 4. Does your app store user-uploaded data?      | Yes        | We store user sketches (temporarily) and generated SVG/PNG assets. |
| 5. If storing data: for how long and where?     | 1 Semester | Stored in a local `assets/` folder or a lightweight JSON cache.    |
| 6. Do users need to give informed consent?      | Yes        | A "Terms of Use" footer on the Streamlit app.                      |

If any answers above are "yes": Users will be notified that any sketches they upload are processed by Google (Gemini) or Anthropic (Claude) APIs. No personal identification data is stored; we only save the artistic content generated to provide a "Project History" for the user.
