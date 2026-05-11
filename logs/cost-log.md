# Cost Log — Lab 5 Sprint

**Team Name:** Clockwork Orange

**Date:** 10 April 2026

## Log Table

| # | Timestamp | Model                         | Endpoint / Purpose           | Input Tokens | Output Tokens | Total Tokens | Latency (ms) | Input Price/1M | Output Price/1M | Cost (USD) |
|---|-----------|-------------------------------|------------------------------|--------------|---------------|--------------|--------------|----------------|-----------------|------------|
| 1 | 10:30 AM  | google/gemini-2.0-flash-001   | /api/health (Env Check)      | 45           | 12            | 57           | 450          | $0.10          | $0.40           | $0.000009  |
| 2 | 11:15 AM  | google/gemini-2.0-flash-001   | /api/generate/svg (Sword)    | 115          | 620           | 735          | 5820         | $0.10          | $0.40           | $0.000259  |
| 3 | 11:20 AM  | google/gemini-2.0-flash-001   | /api/generate/svg (Crusader) | 102          | 570           | 672          | 5994         | $0.10          | $0.40           | $0.000238  |
| 4 | 11:45 PM  | google/gemini-3-flash-preview | /api/generate/svg (Heater)   | 98           | 1395          | 1493         | 12017        | $0.10          | $0.40           | $0.000568  |
| 5 | 12:15 AM  | anthropic/claude-4.6-sonnet   | /api/generate/svg (Master)   | 124          | 3667          | 3791         | 46322        | $3.00          | $15.00          | $0.055377  |

---

## Sprint Summary

**Total calls made:** 5

**Total input tokens:** 484

**Total output tokens:** 6264

**Total cost (USD):** $0.056451

**Highest-cost single call:** #5 ($0.055377)

**Lowest-latency call:** #1 (450ms)
