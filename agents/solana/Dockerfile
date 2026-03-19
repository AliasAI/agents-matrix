FROM python:3.12-slim

# System dependencies + Solana CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl bzip2 && \
    rm -rf /var/lib/apt/lists/*

# Install Solana CLI
ARG SOLANA_VERSION=v2.2.12
RUN curl -sSfL "https://release.anza.xyz/${SOLANA_VERSION}/install" | sh
ENV PATH="/root/.local/share/solana/install/active_release/bin:${PATH}"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace root + framework + this agent
# NOTE: build context is agents-matrix/ root (set in docker-compose.yml)
COPY pyproject.toml /app/pyproject.toml
COPY framework /app/framework
COPY agents/solana /app/agents/solana

# Install dependencies
RUN cd /app && uv lock --prerelease=allow && uv sync --prerelease=allow --package solana-agent

WORKDIR /app/agents/solana

EXPOSE 9002

CMD ["uv", "run", "--package", "solana-agent", "python", "main.py"]
