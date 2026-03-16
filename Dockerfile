FROM python:3.12-slim

# Install system dependencies and Foundry cast
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl git && \
    rm -rf /var/lib/apt/lists/*

# Install Foundry (cast)
RUN curl -L https://foundry.paradigm.xyz | bash && \
    /root/.foundry/bin/foundryup
ENV PATH="/root/.foundry/bin:${PATH}"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy cli-anything-cast (path dependency, placed by deploy.sh)
COPY cast-harness/ /app/cast-harness/

# Copy application code
COPY . .

# Rewrite path dependency for Docker context
RUN sed -i 's|path = "../../CLI-Anything/cast/agent-harness"|path = "cast-harness"|' pyproject.toml

# Install dependencies (regenerate lockfile for new path)
RUN uv lock --prerelease=allow && uv sync --prerelease=allow

EXPOSE 9000

CMD ["uv", "run", "python", "main.py"]
