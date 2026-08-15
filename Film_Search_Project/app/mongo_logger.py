import json
import os
from collections.abc import Callable
from datetime import datetime
from functools import wraps

from app.logging_config import ERROR_LOGGER, SEARCH_LOGGER
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError


def log_mongo_action(action_name: str, safe_return: object = None) -> Callable:
    """Логирует успешное или ошибочное выполнение действия в MongoDB."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except PyMongoError as error:
                ERROR_LOGGER.error(
                    "MongoDB: %s не выполнено (%s)",
                    action_name,
                    type(error).__name__,
                )
                return safe_return

            return result

        return wrapper

    return decorator


def get_collection() -> Collection:
    """Возвращает коллекцию MongoDB для логов поиска."""
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/film_search")
    client = MongoClient(mongo_url)
    database = client["film_search"]
    return database["final_project_060326-ptm_Bohdan_Slutskyi"]


def build_normalized_search_projection() -> dict[str, object]:
    """Приводит новые и ранее сохранённые логи к общей структуре."""
    return {
        "$project": {
            "search_type": {
                "$cond": [
                    {"$eq": ["$search_type", "genre_year"]},
                    "genre__years_range",
                    "$search_type",
                ]
            },
            "params": {"$ifNull": ["$params", "$parameters"]},
            "results_count": 1,
            "timestamp": {"$ifNull": ["$timestamp", "$created_at"]},
        }
    }


@log_mongo_action("сохранение поискового запроса")
def log_search(
    search_type: str,
    params: dict[str, object],
    results_count: int,
) -> None:
    """Сохраняет один поисковый запрос в MongoDB."""
    collection = get_collection()
    normalized_search_type = (
        "genre__years_range" if search_type == "genre_year" else search_type
    )

    search_document = {
        "timestamp": datetime.now(),
        "search_type": normalized_search_type,
        "params": params,
        "results_count": results_count,
    }

    # Записываем компактный документ с параметрами поиска.
    collection.insert_one(search_document)
    SEARCH_LOGGER.info(
        "search_type=%s | params=%s | results_count=%s",
        normalized_search_type,
        json.dumps(params, ensure_ascii=False, sort_keys=True),
        results_count,
    )


@log_mongo_action("чтение последних поисковых запросов", safe_return=[])
def get_recent_searches(limit: int = 5) -> list[dict[str, object]]:
    """Возвращает последние уникальные поисковые запросы без _id."""
    collection = get_collection()
    safe_limit = max(limit, 1)

    pipeline = [
        build_normalized_search_projection(),
        {"$sort": {"timestamp": -1}},
        {
            "$group": {
                "_id": {
                    "search_type": "$search_type",
                    "params": "$params",
                },
                "timestamp": {"$first": "$timestamp"},
                "results_count": {"$first": "$results_count"},
            }
        },
        {"$sort": {"timestamp": -1}},
        {"$limit": safe_limit},
        {
            "$project": {
                "_id": 0,
                "search_type": "$_id.search_type",
                "params": "$_id.params",
                "results_count": 1,
                "timestamp": 1,
            }
        },
    ]

    recent_cursor = collection.aggregate(pipeline)
    return [dict(document) for document in recent_cursor]


@log_mongo_action("чтение популярных поисковых запросов", safe_return=[])
def get_popular_searches(limit: int = 5) -> list[dict[str, object]]:
    """Возвращает самые частые поисковые запросы."""
    collection = get_collection()
    safe_limit = max(limit, 1)

    pipeline = [
        build_normalized_search_projection(),
        {"$sort": {"timestamp": -1}},
        {
            "$group": {
                "_id": {
                    "search_type": "$search_type",
                    "params": "$params",
                },
                "count": {"$sum": 1},
                "timestamp": {"$first": "$timestamp"},
                "results_count": {"$first": "$results_count"},
            }
        },
        {"$sort": {"count": -1, "timestamp": -1}},
        {"$limit": safe_limit},
        {
            "$project": {
                "_id": 0,
                "search_type": "$_id.search_type",
                "params": "$_id.params",
                "count": 1,
                "results_count": 1,
                "timestamp": 1,
            }
        },
    ]

    # Aggregation собирает одинаковые поиски в одну запись.
    popular_searches = collection.aggregate(pipeline)
    return [dict(document) for document in popular_searches]
