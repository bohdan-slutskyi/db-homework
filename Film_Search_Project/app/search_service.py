"""Выполняет повторно используемые сценарии поиска фильмов."""

from typing import Any

from app.mysql_connector import (
    count_films_by_genre_and_year,
    count_films_by_keyword,
    search_films_by_genre_and_year,
    search_films_by_keyword,
)

VALID_SORT_MODES = ("default", "old", "new")


def normalize_keyword(keyword: str) -> str:
    """Приводит ключевое слово к общей форме для поиска и статистики."""
    return keyword.strip().lower()


def normalize_page(page: int) -> int:
    """Ограничивает номер страницы значением не меньше единицы."""
    return max(page, 1)


def normalize_sort_mode(sort_mode: str) -> str:
    """Возвращает поддерживаемый режим сортировки."""
    return sort_mode if sort_mode in VALID_SORT_MODES else "default"


def run_keyword_search(
    keyword: str,
    page: int,
    sort_mode: str,
) -> tuple[str, int, str, list[Any], int]:
    """Ищет фильмы по названию и возвращает нормализованные параметры и результат."""
    normalized_keyword = normalize_keyword(keyword)
    safe_page = normalize_page(page)
    safe_sort_mode = normalize_sort_mode(sort_mode)
    results = search_films_by_keyword(
        normalized_keyword,
        safe_page,
        sort_mode=safe_sort_mode,
    )
    total_count = count_films_by_keyword(normalized_keyword)
    return normalized_keyword, safe_page, safe_sort_mode, results, total_count


def run_filtered_search(
    genre: str,
    year_from: str,
    year_to: str,
    page: int,
    sort_mode: str,
    exact_year: str = "",
    rating: str = "",
    rental_rate: str = "",
    length_group: str = "",
    actor_id: str = "",
) -> tuple[int, str, list[Any], int]:
    """Ищет фильмы по фильтрам и возвращает страницу, сортировку и результат."""
    safe_page = normalize_page(page)
    safe_sort_mode = normalize_sort_mode(sort_mode)
    results = search_films_by_genre_and_year(
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        page=safe_page,
        sort_mode=safe_sort_mode,
        exact_year=exact_year,
        rating=rating,
        rental_rate=rental_rate,
        length_group=length_group,
        actor_id=actor_id,
    )
    total_count = count_films_by_genre_and_year(
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        exact_year=exact_year,
        rating=rating,
        rental_rate=rental_rate,
        length_group=length_group,
        actor_id=actor_id,
    )
    return safe_page, safe_sort_mode, results, total_count
