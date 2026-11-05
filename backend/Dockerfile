FROM python:3.14.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt constraints.txt ./
RUN python -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install --no-cache-dir pip==26.2.2 && \
    /opt/venv/bin/python -m pip install --no-cache-dir -r requirements.txt

FROM python:3.14.9-slim AS runner
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

ENV UVICORN_WORKERS=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
