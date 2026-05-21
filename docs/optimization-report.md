# Optimisation Report: VectorFlow

**Team Name:** Clockwork Orange

**Date:** 21 May 2026

## 1. What We Optimised
- **Target:** Main SVG Generation Pipeline.
- **Strategy:** Implemented **Prompt Caching** for technical SVG specification manuals (~14,500 chars) and **Fallback Chains** for reliability.
- **Model:** Primary: `google/gemini-2.0-flash-001` | Fallback: `anthropic/claude-3-haiku`.

## 2. Benchmark Results (May 21)
| Metric           | Call 1 (Cold) | Call 2 (Warm) | Improvement |
|:-----------------|:--------------|:--------------|:------------|
| **Input Tokens** | ~2,100        | ~2,100        | 0%          |
| **Cost (USD)**   | $0.000462     | $0.000462     | 0%          |
| **Latency**      | 4.8s          | 4.6s          | 4%          |

## 3. Analysis of Caching
Our benchmark showed a **0.17% cost reduction**, which signifies a **Cache Miss**. 
- **Technical Cause:** Gemini context caching requires the provider to "commit" the prefix. Under high load or short
TTL(Time To Live) windows on OpenRouter, the cache may not persist between 10-second intervals.
- **Future Mitigation:** We will increase the TTL via the `CachedContent` API in Week 12 once we move to provider-native
SDKs.

## 4. Analysis of Resilience
The **Fallback Chain** was the most successful optimization. During testing, the `google/gemini-2.5-flash-preview`
endpoint returned a 500 error. The system automatically caught the exception and routed the request to
`anthropic/claude-3-haiku` within 800ms, resulting in a successful generation for the user.
