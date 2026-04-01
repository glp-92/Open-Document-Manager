# API

FastAPI is fully integrated with [uv](https://docs.astral.sh/uv). For development purposes, install uv and all needed dependencies

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

To be able to use `psycopg3`

```bash
apt install libpq-dev gcc
```

`pyproject.toml` is already provided with Python version, needed dependencies and configuration for code static analysis

`uv sync --all-groups --no-cache` to install all dependencies

Install `pre-commit` to run code checks on commit phase

```bash
uv run pre-commit install
uv run pre-commit run --all-files # test pre-commit on code manually
```

## Run API

```bash
uv run fastapi run api/src/main.py --port 8080
```
