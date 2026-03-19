FROM python:3.12-slim

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl git && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Clone drawio harness from git (sparse checkout — only drawio/agent-harness)
ARG HARNESS_REPO=https://github.com/0xouzm/CLI-Anything.git
ARG HARNESS_REF=main
RUN git clone --depth 1 --branch ${HARNESS_REF} --filter=blob:none --sparse \
      ${HARNESS_REPO} /tmp/cli-anything && \
    cd /tmp/cli-anything && git sparse-checkout set drawio/agent-harness && \
    cp -r drawio/agent-harness /app/drawio-harness && \
    rm -rf /tmp/cli-anything

# Copy workspace root + framework + this agent
# NOTE: build context is agents-matrix/ root (set in docker-compose.yml)
COPY pyproject.toml /app/pyproject.toml
COPY framework /app/framework
COPY agents/drawio /app/agents/drawio

# Rewrite path dependency for Docker context
RUN sed -i 's|path = "../../../../CLI-Anything/drawio/agent-harness"|path = "/app/drawio-harness"|' /app/agents/drawio/pyproject.toml

# Install dependencies
RUN cd /app && uv lock --prerelease=allow && uv sync --prerelease=allow --package drawio-agent

WORKDIR /app/agents/drawio

EXPOSE 9001

CMD ["uv", "run", "--package", "drawio-agent", "python", "main.py"]
