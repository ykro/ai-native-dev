FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY traderpulse_api ./traderpulse_api
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.13-slim-bookworm
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
USER 10001
# Cloud Run inyecta PORT; exec para que uvicorn reciba SIGTERM como PID 1.
CMD ["sh", "-c", "exec uvicorn traderpulse_api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
