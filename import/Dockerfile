FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS uv

WORKDIR /app

# avoids hardlink issues in containers
ENV UV_LINK_MODE=copy  

# copy dependency files for caching
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# copy application code
COPY main.py .
 
CMD ["uv", "run", "main.py" ]
