# Data Map: VectorFlow

| Data Type            | Storage Location                | Retention Period     | Deletion Method                     |
|----------------------|---------------------------------|----------------------|-------------------------------------|
| Conversation History | In-memory (FastAPI `_sessions`) | Until server restart | Reset button in UI / Server restart |
| SVG Assets           | Local `logs/` (CSV hashes only) | 1 Semester           | Manual file deletion                |
| API Usage Logs       | `logs/episode-log.csv`          | 1 Semester           | Manual file deletion                |
| Prompt Fingerprints  | `logs/mcp-audit.jsonl`          | 1 Semester           | Manual file deletion                |

**PII Policy:** No names, emails, or IP addresses are stored. User prompts are hashed before logging to ensure privacy.
