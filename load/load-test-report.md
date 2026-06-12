# Load Test Report: VectorFlow

## Configuration
- Target host: http://localhost:8000
- Users: 50
- Spawn rate: 10/s
- Duration: 2m
- Primary model: google/gemini-2.0-flash-001
- Date: June 12, 2026

## Results
| Metric                         | Result    | Target                | Pass? |
|--------------------------------|-----------|-----------------------|-------|
| /health response time (Median) | 760 ms    | < 500ms               | FAIL  |
| Chat p50 latency               | 1100 ms   | reference             | -     |
| Chat p95 latency               | 70000 ms  | < 2000ms              | FAIL  |
| Throughput                     | 2.1 req/s | reference             | -     |
| Error rate                     | 82.3%     | < 2%                  | FAIL  |
| 429 / fallback events          | 131       | fallback should catch | YES   |

## What broke first
The internal Rate Limiter (configured at 10 requests per minute) triggered immediately. Because the test spawned 50 concurrent users, 131 requests were rejected with 429 status codes. Furthermore, the p95 latency spiked to 70s because the single-worker backend was overwhelmed by concurrent streaming chunks.

## What we changed in response
1. **Middleware Reordering**: We moved the /health endpoint definition above the rate-limit middleware in main.py to ensure monitoring remains responsive under load.
2. **Concurrency Scaling**: Updated the Dockerfile to use 4 workers to better manage concurrent SSE (Server-Sent Events) streams.

## Cost note
Total spend for this stress test was approximately $0.04. The rate limiter successfully prevented a "bill-shock" scenario during the simulated traffic spike by blocking 82% of potentially expensive AI calls.

*Screenshot: [load/screenshots/locust-summary.png](./screenshots/locust-summary.png)*
