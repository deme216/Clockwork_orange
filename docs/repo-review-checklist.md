# Repository Review Checklist

## Hard Gates
- [x] No secrets in git history (Purged with git-filter-repo and rotated).
- [x] Working Dockerfile (Verified locally with 3.12-slim).
- [x] /health endpoint responds (Median 760ms; optimization applied to move under 500ms).
- [x] Green CI run on main branch (10/10 Golden Set result).
- [x] 3+ evaluation run files committed in eval/results/.

## Portfolio
- [x] One-command setup documented in README.
- [x] README includes overview, architecture, setup, and cost analysis.
- [x] 2-minute narrated demo video.
- [x] Case study (2-3 pages) committed at docs/case-study.md.
- [x] AGENTS.md added for AI coding assistance.
- [x] Model selection decisions table in README.
- [x] Data governance and retention policy documented.
