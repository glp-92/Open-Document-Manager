FROM python:3.14-slim
RUN apt update && apt upgrade -y \
    && apt install -y --no-install-recommends libpq-dev gcc \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync --group api --no-dev --no-cache
CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "8080", "--host", "0.0.0.0"]