## This Dockerfile sets up a MkDocs environment to serve documentation for the project.

FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync --locked --only-group=docs
RUN uv export --only-group=docs | uv pip install --requirements=-
ENV PATH=/app/.venv/bin:$PATH
EXPOSE 8000

CMD ["mkdocs", "serve"]
