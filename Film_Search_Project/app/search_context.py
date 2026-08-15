"""Готовит данные главной страницы поиска и статистики."""

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from app.catalog_presentation import add_card_styles
from app.mongo_logger import get_popular_searches, get_recent_searches, log_search
from app.mysql_connector import (
    get_all_actors,
    get_all_categories,
    get_release_year_range,
)
from app.search_helpers import (
    LENGTH_GROUP_CHOICES,
    LENGTH_GROUP_OPTIONS,
    RATING_CHOICES,
    RENTAL_RATE_CHOICES,
    RENTAL_RATE_OPTIONS,
    build_genre_year_log_params,
    build_length_group_labels,
    build_search_parts,
    get_last_offset,
    parse_non_negative_int,
    parse_positive_int,
    resolve_actor_selection,
)
from app.search_service import (
    normalize_keyword,
    run_filtered_search,
    run_keyword_search,
)
from fastapi import Request

STATS_LOOKUP_LIMIT = 10000
STATS_PAGE_SIZE = 5


def log_search_query(
    search_type: str,
    params: dict[str, object],
    results_count: int,
) -> None:
    """Передаёт поисковый запрос в MongoDB-логирование."""
    log_search(search_type, params, results_count)


def clean_search_param(value: object) -> str:
    """Возвращает строковое значение параметра поиска без лишних пробелов."""
    if value is None:
        return ""
    return str(value).strip()


def format_search_timestamp(value: object) -> str:
    """Форматирует время поиска для статистического блока."""
    if isinstance(value, datetime):
        utc_timestamp = value.replace(tzinfo=timezone.utc)
        berlin_timestamp = utc_timestamp.astimezone(ZoneInfo("Europe/Berlin"))
        return berlin_timestamp.strftime("%d.%m.%Y %H:%M")
    return clean_search_param(value)


def get_actor_name_for_log(actor_id: str) -> str:
    """Возвращает имя актёра для подписи в истории поиска."""
    if not actor_id:
        return ""

    try:
        _, actor_name = resolve_actor_selection(actor_id, get_all_actors())
    except Exception:
        return ""

    return actor_name


def normalize_search_item(search: dict[str, object]) -> dict[str, object]:
    """Готовит MongoDB-документ к отображению в шаблоне."""
    search_type = str(search.get("search_type", ""))
    if search_type == "genre_year":
        search_type = "genre__years_range"

    params_raw = search.get("params")
    if not isinstance(params_raw, dict):
        params_raw = search.get("parameters")
    params = dict(params_raw) if isinstance(params_raw, dict) else {}

    search_text = clean_search_param(search.get("search_text"))
    display_subtitle = clean_search_param(search.get("display_subtitle"))

    if not search_text:
        if search_type == "keyword":
            search_text = clean_search_param(params.get("keyword"))
        elif search_type == "genre__years_range":
            search_parts: list[str] = []
            subtitle_parts: list[str] = []

            actor_id = clean_search_param(params.get("actor_id"))
            if actor_id:
                actor_name = get_actor_name_for_log(actor_id)
                search_parts.append(actor_name or "Актёр ID " + actor_id)
                subtitle_parts.append("актёр")

            genre = clean_search_param(params.get("genre"))
            if genre:
                search_parts.append(genre)
                subtitle_parts.append("жанр")

            exact_year = clean_search_param(params.get("exact_year"))
            if exact_year:
                search_parts.append(exact_year)
                subtitle_parts.append("точный год")

            year_from = clean_search_param(params.get("year_from"))
            year_to = clean_search_param(params.get("year_to"))
            if year_from and year_to:
                search_parts.append(year_from + " - " + year_to)
                subtitle_parts.append("диапазон лет")
            elif year_from:
                search_parts.append("от " + year_from)
                subtitle_parts.append("год от")
            elif year_to:
                search_parts.append("до " + year_to)
                subtitle_parts.append("год до")

            rating = clean_search_param(params.get("rating"))
            if rating:
                search_parts.append(rating)
                subtitle_parts.append("рейтинг")

            rental_rate = clean_search_param(params.get("rental_rate"))
            if rental_rate:
                search_parts.append("$" + rental_rate)
                subtitle_parts.append("аренда")

            length_group = clean_search_param(params.get("length_group"))
            length_group_label = build_length_group_labels().get(length_group, "")
            if length_group_label:
                search_parts.append(length_group_label)
                subtitle_parts.append("длительность")

            search_text = ", ".join(search_parts)
            display_subtitle = " + ".join(subtitle_parts)

    if not display_subtitle:
        display_subtitle = {
            "keyword": "по названию",
            "genre__years_range": "фильтры каталога",
        }.get(search_type, "поиск")

    normalized = dict(search)
    normalized["search_type"] = search_type
    normalized["params"] = params
    normalized["search_text"] = search_text
    normalized["display_title"] = (
        clean_search_param(search.get("display_title")) or search_text
    )
    normalized["display_subtitle"] = display_subtitle
    timestamp = search.get("timestamp")
    if timestamp is None:
        timestamp = search.get("created_at")
    normalized["display_time"] = search.get("display_time") or format_search_timestamp(
        timestamp
    )
    normalized["count"] = search.get("count", 1)
    return normalized


def normalize_searches(searches: list[dict[str, object]]) -> list[dict[str, object]]:
    """Преобразует список поисков для панелей последних и популярных запросов."""
    return [normalize_search_item(search) for search in searches]


def build_index_context(
    request: Request,
    keyword: str,
    actor_id: str,
    genre: str,
    exact_year: str,
    rating: str,
    rental_rate: str,
    length_group: str,
    year_from: str,
    year_to: str,
    page: str,
    recent_offset: str,
    popular_offset: str,
    sort: str,
    search_submitted: str,
) -> dict[str, object]:
    """Собирает контекст каталога, поиска и статистики для главного шаблона."""
    keyword = normalize_keyword(keyword)
    actor_id = actor_id.strip()
    genre = genre.strip()
    exact_year = exact_year.strip()
    rating = rating.strip()
    rental_rate = rental_rate.strip()
    length_group = length_group.strip()
    year_from = year_from.strip()
    year_to = year_to.strip()
    search_submitted = search_submitted.strip()
    sort_mode = sort

    if sort_mode not in ("default", "old", "new"):
        sort_mode = "default"
    if rating not in RATING_CHOICES:
        rating = ""
    if rental_rate not in RENTAL_RATE_CHOICES:
        rental_rate = ""
    if length_group not in LENGTH_GROUP_CHOICES:
        length_group = ""
    if exact_year:
        try:
            int(exact_year)
        except ValueError:
            exact_year = ""
    if year_from and year_to:
        year_from_int = int(year_from)
        year_to_int = int(year_to)
        if year_from_int > year_to_int:
            year_from, year_to = year_to, year_from
            sort_mode = "new"

    page_number = parse_positive_int(page)
    recent_offset_number = parse_non_negative_int(recent_offset)
    popular_offset_number = parse_non_negative_int(popular_offset)
    is_pagination = "page" in request.query_params
    actor_choices = get_all_actors()
    actor_id, actor_name = resolve_actor_selection(actor_id, actor_choices)
    length_group_labels = build_length_group_labels()
    length_group_label = length_group_labels.get(length_group, "")
    categories = get_all_categories()
    year_min, year_max = get_release_year_range()
    years = list(range(year_min, year_max + 1)) if year_min and year_max else []

    has_active_filters = any(
        [
            keyword,
            actor_id,
            genre,
            exact_year,
            rating,
            rental_rate,
            length_group,
            year_from,
            year_to,
        ]
    )
    is_empty_search_submission = search_submitted == "1" and not has_active_filters
    films: list[Any] = []
    total_count = 0
    total_pages = 1
    title = "Каталог фильмов"
    message = "Первая страница каталога Sakila. Используйте поиск и фильтры для уточнения выдачи."

    if keyword:
        keyword, page_number, sort_mode, films, total_count = run_keyword_search(
            keyword,
            page_number,
            sort_mode,
        )
        total_pages = (total_count + 9) // 10 if total_count > 0 else 1
        title = "Поиск по названию"
        message = "Результаты поиска по названию: " + keyword
        if not is_pagination:
            log_search_query("keyword", {"keyword": keyword}, total_count)
    elif any(
        [
            actor_id,
            genre,
            exact_year,
            rating,
            rental_rate,
            length_group,
            year_from,
            year_to,
        ]
    ):
        page_number, sort_mode, films, total_count = run_filtered_search(
            genre=genre,
            year_from=year_from,
            year_to=year_to,
            page=page_number,
            sort_mode=sort_mode,
            exact_year=exact_year,
            rating=rating,
            rental_rate=rental_rate,
            length_group=length_group,
            actor_id=actor_id,
        )
        total_pages = (total_count + 9) // 10 if total_count > 0 else 1
        search_parts = build_search_parts(
            actor_name,
            genre,
            exact_year,
            year_from,
            year_to,
            rating,
            rental_rate,
            length_group_label,
        )
        title = "Поиск по жанру и году"
        if search_parts:
            message = "Результаты поиска: " + ", ".join(search_parts)
            if not is_pagination:
                log_search_query(
                    "genre__years_range",
                    build_genre_year_log_params(
                        actor_id,
                        genre,
                        exact_year,
                        rating,
                        rental_rate,
                        length_group,
                        year_from,
                        year_to,
                        sort_mode,
                    ),
                    total_count,
                )
        else:
            message = "Введите жанр, год или диапазон годов для поиска."
    else:
        _, page_number, sort_mode, films, total_count = run_keyword_search(
            "",
            page_number,
            sort_mode,
        )
        total_pages = (total_count + 9) // 10 if total_count > 0 else 1
        if is_empty_search_submission:
            message = "Введите название фильма или выберите хотя бы один фильтр."

    recent_total_count = len(get_recent_searches(limit=STATS_LOOKUP_LIMIT))
    popular_total_count = len(get_popular_searches(limit=STATS_LOOKUP_LIMIT))
    recent_last_offset = get_last_offset(recent_total_count, STATS_PAGE_SIZE)
    popular_last_offset = get_last_offset(popular_total_count, STATS_PAGE_SIZE)
    recent_offset_number = min(recent_offset_number, recent_last_offset)
    popular_offset_number = min(popular_offset_number, popular_last_offset)

    recent_searches = normalize_searches(
        get_recent_searches(limit=recent_offset_number + STATS_PAGE_SIZE)[
            recent_offset_number : recent_offset_number + STATS_PAGE_SIZE
        ]
    )
    popular_searches = normalize_searches(
        get_popular_searches(limit=popular_offset_number + STATS_PAGE_SIZE)[
            popular_offset_number : popular_offset_number + STATS_PAGE_SIZE
        ]
    )
    films = add_card_styles(films)

    return {
        "request": request,
        "actor_choices": actor_choices,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "categories": categories,
        "exact_year": exact_year,
        "films": films,
        "genre": genre,
        "has_active_filters": has_active_filters,
        "has_catalog_query": True,
        "is_empty_search_submission": is_empty_search_submission,
        "keyword": keyword,
        "message": message,
        "page": page_number,
        "popular_first_offset": 0,
        "popular_last_offset": popular_last_offset,
        "popular_next_offset": popular_offset_number + STATS_PAGE_SIZE,
        "popular_offset": popular_offset_number,
        "popular_prev_offset": max(0, popular_offset_number - STATS_PAGE_SIZE),
        "popular_searches": popular_searches,
        "popular_total_count": popular_total_count,
        "rating": rating,
        "rating_choices": RATING_CHOICES,
        "length_group": length_group,
        "length_group_options": LENGTH_GROUP_OPTIONS,
        "rental_rate": rental_rate,
        "rental_rate_options": RENTAL_RATE_OPTIONS,
        "recent_first_offset": 0,
        "recent_last_offset": recent_last_offset,
        "recent_next_offset": recent_offset_number + STATS_PAGE_SIZE,
        "recent_offset": recent_offset_number,
        "recent_prev_offset": max(0, recent_offset_number - STATS_PAGE_SIZE),
        "recent_searches": recent_searches,
        "recent_total_count": recent_total_count,
        "sort_mode": sort_mode,
        "title": title,
        "total_count": total_count,
        "total_pages": total_pages,
        "years": years,
        "year_from": year_from,
        "year_min": year_min,
        "year_max": year_max,
        "year_to": year_to,
        "recent": recent_searches,
        "popular": popular_searches,
        "catalog_page": page_number,
        "catalog_count": total_count,
        "catalog_has_next": page_number < total_pages,
    }
