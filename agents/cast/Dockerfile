FROM python:3.12-slim

# System dependencies
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

# Clone cast harness (sparse checkout — only cast/agent-harness)
# NOTE: build context is agents-matrix/ root (set in docker-compose.yml)
ARG HARNESS_REPO=https://github.com/0xouzm/CLI-Anything.git
ARG HARNESS_REF=main
RUN git clone --depth 1 --branch ${HARNESS_REF} --filter=blob:none --sparse \
      ${HARNESS_REPO} /tmp/cli-anything && \
    cd /tmp/cli-anything && git sparse-checkout set cast/agent-harness && \
    cp -r cast/agent-harness /app/cast-harness && \
    rm -rf /tmp/cli-anything

# ── Dependency layer (cached unless pyproject.toml files change) ──
COPY pyproject.toml /app/pyproject.toml
COPY framework/pyproject.toml /app/framework/pyproject.toml
COPY agents/cast/pyproject.toml /app/agents/cast/pyproject.toml

RUN sed -i 's|path = "../../../../CLI-Anything/cast/agent-harness"|path = "/app/cast-harness"|' \
      /app/agents/cast/pyproject.toml

RUN cd /app && uv lock --prerelease=allow && \
    uv sync --prerelease=allow --package cast-agent --no-install-workspace

# ── Source layer (only invalidates cache on code changes) ──
COPY framework/src /app/framework/src
COPY agents/cast /app/agents/cast

RUN sed -i 's|path = "../../../../CLI-Anything/cast/agent-harness"|path = "/app/cast-harness"|' \
      /app/agents/cast/pyproject.toml && \
    cd /app && uv sync --prerelease=allow --package cast-agent --frozen

WORKDIR /app/agents/cast

EXPOSE 9000

CMD ["/app/.venv/bin/python", "main.py"]
