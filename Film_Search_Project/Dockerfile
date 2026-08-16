# Собирает контейнер FastAPI-приложения с Python-зависимостями через uv.
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN uv sync --frozen --no-dev --no-install-project

COPY app app
COPY templates templates
