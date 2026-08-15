#!/bin/sh
# Быстрая проверка ключевых маршрутов без создания новых MongoDB-логов.
set -eu

podman compose -f compose.yml exec -T app /app/.venv/bin/python -c '
import json
from urllib.request import urlopen


checks = (
    ("главная HTML-страница", "/", "html", "Film Search"),
    ("healthcheck", "/health", "json", "status"),
    (
        "JSON-поиск по названию (страница 2)",
        "/search/keyword?keyword=a&page=2",
        "json-results",
        "results",
    ),
    (
        "JSON-поиск по жанру и годам (страница 2)",
        "/search/genre-year?genre=Action&year_from=2000&year_to=2020&page=2",
        "json-results",
        "results",
    ),
    ("последние запросы", "/stats/recent?limit=5", "json", "recent"),
    ("популярные запросы", "/stats/popular?limit=5", "json", "popular"),
)

for label, path, response_kind, expected_key in checks:
    with urlopen(f"http://127.0.0.1:8000{path}", timeout=10) as response:
        body = response.read().decode("utf-8")

        if response.status != 200:
            raise SystemExit(f"{label}: ожидается HTTP 200, получен {response.status}")

    if response_kind == "html":
        if expected_key not in body:
            raise SystemExit(f"{label}: не найден ожидаемый текст {expected_key!r}")
    else:
        payload = json.loads(body)
        if expected_key not in payload:
            raise SystemExit(f"{label}: в JSON нет ключа {expected_key!r}")
        if response_kind == "json-results" and not payload[expected_key]:
            raise SystemExit(f"{label}: поиск не вернул результатов")

    print(f"OK: {label}")
'

printf '%s\n' 'Smoke-тесты пройдены.'
