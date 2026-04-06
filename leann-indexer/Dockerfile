ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ARG LEANN_VERSION=0.3.7

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

# Keep runtime image minimal while ensuring common C++ runtime libs are present.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgomp1 \
        libstdc++6 \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install --prefer-binary "leann==${LEANN_VERSION}" \
    && python -c "import leann; import leann_backend_hnsw; import leann_backend_diskann"

RUN pip install --no-cache-dir loguru psycopg>=3.3 python-dotenv
COPY src /app/src
WORKDIR /app/src

ENTRYPOINT  ["python", "main.py"]