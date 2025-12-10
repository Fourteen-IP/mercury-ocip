## This Dockerfile sets up a MkDocs environment to serve documentation for the project.

FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync --frozen --only-group=docs
ENV PATH=/app/.venv/bin:$PATH
EXPOSE 8080

CMD ["mkdocs", "serve"]
