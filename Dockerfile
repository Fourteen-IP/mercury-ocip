## This Dockerfile sets up a MkDocs environment to serve documentation for the project.

FROM python:3.12 AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync --frozen --only-group=docs
ENV PATH=/app/.venv/bin:$PATH

ARG MKDOCS_CONFIG=mkdocs-ocip.yml
RUN mkdocs build -f ${MKDOCS_CONFIG} -d /site

FROM nginx:alpine
COPY --from=builder /site /usr/share/nginx/html
EXPOSE 80
