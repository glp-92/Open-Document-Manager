FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 libstdc++6 libpq-dev gcc \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-cache
COPY . /app
WORKDIR /app/src
ENTRYPOINT  ["/app/.venv/bin/python", "main.py"]