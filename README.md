# TDS Data Analyst Agent (Python)

## Overview

FastAPI agent that accepts multipart POST at `/api/` with `questions.txt` (required) and zero or more files. It parses the question and runs appropriate pipeline (e.g., scrape Wikipedia tables, analyze attachments), returns structured JSON answers and base64-encoded plots.

## Quick start

1. Install:
2. Copy `.env.example` to `.env` and set `AI_PROXY_URL` + `AI_PROXY_KEY` if you want LLM assistance.
3. Start server:
4. Test with curl: 
curl <http://localhost:8000/api/> -F "questions.txt=@tests/sample_question.txt" -F "data.csv=@tests/data.csv"

## Notes

- `questions.txt` must contain the question instructions.
- The app tries to detect tasks (Wikipedia scrape, parquet/duckdb detection, or generic CSV analysis).
- Images returned are `data:image/png;base64,...` (or webp fallback) and are *attempted* to be under 100,000 bytes by iterative compression/resizing.
