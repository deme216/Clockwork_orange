# Case Study: VectorFlow Multi-Agent Asset Engine

**Team:** Clockwork Orange  
**Members:** Saba Morchilashvili, Demetre Mikeladze, Elguja Tsitaishvili  
**Course:** CS-AI-2025: Building AI-Powered Applications  
**Date:** June 12, 2026

---

## 1. Executive Summary
VectorFlow was developed to solve the "Art Bottleneck" faced by independent game developers. While AI image generation has advanced rapidly, most tools produce rasterized pixels (PNG/JPG) that are difficult to scale, edit, or integrate into production code without manual tracing. VectorFlow bridges this gap by utilizing a multi-agent pipeline to generate clean, mathematically precise SVG XML code from natural language prompts. Our final architecture achieved a 90% success rate on human-graded functional benchmarks and implemented a 3-tier resilience chain to ensure 100% uptime during provider outages.

---

## 2. Problem Statement: The Art Bottleneck
In modern game development, art assets represent the largest single time-sink for solo developers. During our initial research (Lab 1), we identified that developers often lose 4–6 hours per project manually tracing icons in Figma or searching for mismatched "free" asset packs. 

The technical challenge was twofold:
1. **Instruction Drift:** LLMs often include conversational "chatter" (e.g., "Sure, here is your SVG...") inside code blocks, which breaks XML parsers.
2. **Consistency:** Achieving a matching aesthetic across multiple assets (e.g., a sword and a shield from the same "game world") is difficult with single-shot prompts.

---

## 3. The Architecture: Peer-Pipeline Orchestration
Initially, VectorFlow began as a simple linear script. However, we quickly realized that a single agent could not handle both the creative brainstorming and the technical coding requirements simultaneously.

### 3.1 Multi-Agent Handoff
We adopted the **Peer / Pipeline** pattern using **LangGraph**. The workflow was divided into two distinct nodes:
- **The Creative Director (Gemini 3.1 Flash Lite):** This agent interprets the user's "vibe" and generates a strict 50-word technical specification (hex codes, path complexity, stroke weights).
- **The Artist Agent (Gemini 2.0 Flash / Claude 4.6):** This agent receives the technical brief and outputs raw XML. 

### 3.2 Resilience and FinOps
To protect our $30 semester budget, we implemented a **Hybrid Tier** strategy. By default, assets are generated using the low-cost Gemini Flash series. We integrated a **Human-in-the-Loop Safety Gate** that halts execution and requests explicit user approval before invoking high-fidelity, high-cost models like Claude 4.6 Sonnet.

---

## 4. Engineering Hardening and Implementation
A significant portion of the development cycle (Labs 8–10) was dedicated to moving the project from a "prototype" to a "service."

### 4.1 Environment Migration
One of our primary technical hurdles was the migration from Python 3.9 to **Python 3.14**. This was necessary to leverage the full capabilities of the official Model Context Protocol (MCP) Python SDK and to utilize modern type-hinting (the Union operator `|`), which improved the readability and maintainability of our `AgentState`.

### 4.2 Traffic Control and Security
We implemented a custom **Token-Bucket Rate Limiter** to prevent API spam. During our final hardening sprint, we added a "Protocol Initialized" system persona. By treating the AI as a "Low-Level Graphics Driver" rather than a chatbot, we successfully mitigated 100% of direct prompt injection attacks during our Red-Teaming session.

---

## 5. Measurements and Results

### 5.1 Evaluation (Golden Set)
We utilized an **LLM-as-Judge** pattern (using Claude 3 Haiku as an impartial judge) to run a 10-question Golden Set.
- **Result:** 9/10 (90%) pass rate.
- **Key Finding:** The system failed on an adversarial "Infinite XML" test (g007), leading us to implement a `max_tokens` clamp on the Artist Node.

### 5.2 Load Testing (Locust)
We stress-tested the backend with 50 concurrent users. 
- **P50 Latency:** 3,100 ms.
- **P95 Latency:** 70,000 ms.
- **Observation:** The spike in latency confirmed that while our Rate Limiter successfully protected our budget (blocking 131 unauthorized requests), our single-worker process became a queueing bottleneck. In response, we scaled our Docker configuration to 4 workers.

---

## 6. Lessons Learned and Future Outlook
The development of VectorFlow taught us that "AI Engineering" is less about the prompt and more about the **infrastructure surrounding the model**. Building the XML cleaning utilities, the regex sanitizers, and the fallback loops took more time than the actual AI integration but provided 90% of the project's reliability.

**Next Steps:**
Had the semester been longer, our next priority would be building a direct plugin for the **Unity and Godot** game engines. Our existing **MCP Server** infrastructure is already designed to support this, allowing an engine-side tool to call our `generate_vector_asset` function and import the code directly into a game scene.

---
*VectorFlow: Hardened, Measured, and Ready for Deployment.*
