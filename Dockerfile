# Stage 1: Python base
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Stage 2: Development
FROM base AS development
# Install dependencies
RUN uv sync --no-cache --no-install-project
# Keep container alive for dev
CMD ["tail", "-f", "/dev/null"]
