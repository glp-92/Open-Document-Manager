FROM python:3.12-slim as builder
RUN apt update && apt upgrade -y \
    && apt install -y --no-install-recommends libpq-dev gcc \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv
COPY pyproject.toml uv.lock ./
RUN uv sync \
    --frozen \
    --no-dev \
    --group api \
    --no-install-project
RUN ls -R /app/.venv/bin/fastapi || echo "EL BINARIO NO ESTÁ AQUÍ"
RUN python -c "import sys; print(sys.path)"

FROM python:3.12-slim
RUN apt update && apt install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . /app
ENV PYTHONUNBUFFERED=1
# CMD ["sleep", "infinity"]
CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "8080", "--host", "0.0.0.0"]