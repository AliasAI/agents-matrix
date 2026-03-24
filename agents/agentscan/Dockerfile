FROM python:3.12-slim

# System dependencies (curl for healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace root + framework + this agent
# NOTE: build context is agents-matrix/ root (set in docker-compose.yml)
COPY pyproject.toml /app/pyproject.toml
COPY framework /app/framework
COPY agents/agentscan /app/agents/agentscan

# Install dependencies
RUN cd /app && uv lock --prerelease=allow && uv sync --prerelease=allow --package agentscan-agent

WORKDIR /app/agents/agentscan

EXPOSE 9010

CMD ["uv", "run", "--package", "agentscan-agent", "python", "main.py"]
