FROM python:3.12-slim

WORKDIR /app/services/api

RUN pip install --no-cache-dir uv

COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-dev

COPY api/ .

ENV PATH="/app/services/api/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]