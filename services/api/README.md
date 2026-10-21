# Brasaland Incident Analysis API

Backend service built with FastAPI for the Brasaland incident analysis project.

## Purpose

This API allows internal users to:

- Upload an incidents CSV file.
- Validate and analyze the records using the same rules as the Python script.
- Receive the analysis summary as JSON.
- Download the latest analysis results as CSV.

## Endpoints

### POST /api/incidents/analyze

Receives a CSV file using `multipart/form-data`.

Returns:

- Total records.
- Valid and invalid records.
- Invalid records breakdown.
- Breakdown by category.
- Breakdown by status.
- Satisfaction metrics.

### GET /api/incidents/results/export

Downloads the latest analysis results as a CSV file.

## Technology

- Python
- FastAPI
- Uvicorn

## Run locally

```bash
cd services/api
uv sync --frozen
cp .env.example .env
# Configure .env with your local test settings before starting.
uv run uvicorn main:app --workers 1
```

Use one worker: analysis results, cache and TinyDB are process-local.
Docker also explicitly starts Uvicorn with `--workers 1` (without reload).
Actual email delivery through Resend has not been verified; authentication
tests do not demonstrate delivery to a real inbox.
