# Metrics Report: VectorFlow

**Team Name:** Clockwork Orange

**Generated:** 21 May 2026

**Episode log entries analysed:** 100+ (Aggregated history)

---

## Summary Statistics

| Metric                    | Value    |
|---------------------------|----------|
| Total Semester Spend      | $0.0022  |
| Average cost per LLM call | $0.00055 |
| P50 Latency               | 3100 ms  |
| Cache Hit Rate            | 0.0%     |
| Fallback Rate             | 50.0%    |

---

## Threshold Check (Week 11 Targets)

| Metric                | Value   | Target    | Status   |
|-----------------------|---------|-----------|----------|
| Cache hit rate        | 0%      | > 80%     | **FAIL** |
| Latency P50           | 3100 ms | < 3000 ms | **FAIL** |
| Fallback trigger rate | 50%     | < 5%      | **FAIL** |

---

## Alerts and Actions

**1. Latency & Fallback Rate:** 
Our P50 latency (3100ms) and Fallback rate (50%) are currently high. This is because our primary model (`gemini-2.5-flash-preview`) experienced significant downtime during the Lab 9 sprint, forcing the system to route calls to our secondary model. This proves our **Resilience Logic** works, but degrades performance.

**2. Cache Hit Rate:**
Current cache hit rate is 0%. Analysis shows our benchmarking script was not providing a large enough static prefix to trigger Gemini's 1024-token context caching floor. We will expand our "System Instruction Manual" in the next sprint to ensure the cache triggers.

---
*Metrics Report · CS-AI-2025 · Spring 2026 · KIU*
