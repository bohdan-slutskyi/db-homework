from urllib.parse import urlencode

import mysql.connector
from app.catalog_presentation import serialize_catalog_films
from app.logging_config import ERROR_LOGGER, configure_file_logging
from app.mongo_logger import get_popular_searches, get_recent_searches
from app.mysql_connector import (
    MySQLConfigurationError,
    get_all_actors,
    get_film_details,
)
from app.search_context import build_index_context, log_search_query
from app.search_helpers import (
    LENGTH_GROUP_OPTIONS,
    RATING_CHOICES,
    RENTAL_RATE_OPTIONS,
    build_genre_year_log_params,
    build_length_group_labels,
    build_search_parts,
    build_url_with_query,
    resolve_actor_selection,
)
from app.search_service import run_filtered_search, run_keyword_search
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

# Настройка FastAPI, HTML-шаблонов и файлового логирования.
app = FastAPI(
    title="Film Search Project",
    description="Film search application with MySQL Sakila and MongoDB.",
)
templates = Jinja2Templates(directory="templates")
configure_file_logging()


def template_url_for(endpoint: str, **values: object) -> str:
    """Повторяет нужное шаблонам поведение Flask url_for для FastAPI."""
    route_paths = {
        "index": "/",
        "film_detail": "/films/{film_id}",
        "film_quick_view": "/api/films/{film_id}",
        "search_keyword": "/ui/search/keyword",
        "search_genre": "/ui/search/genre-year",
        "search_genre_year": "/ui/search/genre-year",
        "static": "/static/{path}",
    }
    path = route_paths.get(endpoint, "/")
    query_params: dict[str, object] = {}

    for key, value in values.items():
        if value is None or value == "":
            continue

        placeholder = "{" + key + "}"
        if placeholder in path:
            path = path.replace(placeholder, str(value).lstrip("/"))
        else:
            query_params[key] = value

    if query_params:
        return path + "?" + urlencode(query_params)

    return path


templates.env.globals["url_for"] = template_url_for


# Безопасная обработка ошибок MySQL для HTML-страниц и JSON API.
MYSQL_ERROR_MESSAGE = (
    "Сервис поиска временно не может подключиться к MySQL. "
    "Повторите попытку позже или проверьте параметры подключения."
)
JSON_ROUTE_PREFIXES = ("/api/", "/search/", "/stats/", "/health")


def build_mysql_error_response(request: Request, error: Exception):
    """Возвращает безопасный ответ при ошибке подключения или запроса MySQL."""
    ERROR_LOGGER.error("MySQL request failed: %s", type(error).__name__)

    if request.url.path.startswith(JSON_ROUTE_PREFIXES):
        return JSONResponse(
            status_code=503,
            content={"detail": MYSQL_ERROR_MESSAGE},
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "error_title": "Поиск временно недоступен",
            "error_message": MYSQL_ERROR_MESSAGE,
        },
        status_code=503,
    )


@app.exception_handler(mysql.connector.Error)
def handle_mysql_error(request: Request, error: mysql.connector.Error):
    """Обрабатывает ошибки подключения и выполнения запросов MySQL."""
    return build_mysql_error_response(request, error)


@app.exception_handler(MySQLConfigurationError)
def handle_mysql_configuration_error(
    request: Request,
    error: MySQLConfigurationError,
):
    """Обрабатывает отсутствующие или неверные параметры MySQL."""
    return build_mysql_error_response(request, error)


# HTML-маршруты приложения.
@app.get("/")
def index(
    request: Request,
    keyword: str = "",
    actor_id: str = "",
    genre: str = "",
    exact_year: str = "",
    rating: str = "",
    rental_rate: str = "",
    length_group: str = "",
    year_from: str = "",
    year_to: str = "",
    page: str = "1",
    recent_offset: str = "0",
    popular_offset: str = "0",
    sort: str = "default",
    search_submitted: str = "",
):
    """Главная страница проекта."""
    context = build_index_context(
        request=request,
        keyword=keyword,
        actor_id=actor_id,
        genre=genre,
        exact_year=exact_year,
        rating=rating,
        rental_rate=rental_rate,
        length_group=length_group,
        year_from=year_from,
        year_to=year_to,
        page=page,
        recent_offset=recent_offset,
        popular_offset=popular_offset,
        sort=sort,
        search_submitted=search_submitted,
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/films/{film_id}")
def film_quick_view(film_id: int):
    """Возвращает JSON-данные фильма для quick-view modal."""
    film = get_film_details(film_id)

    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")

    return film


@app.get("/films/{film_id}")
def film_detail(request: Request, film_id: int):
    """Показывает подробную страницу одного фильма."""
    film = get_film_details(film_id)

    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")

    return templates.TemplateResponse(
        request=request,
        name="film_detail.html",
        context={
            "request": request,
            "film": film,
        },
    )


@app.get("/search/keyword")
def search_keyword(
    keyword: str, page: int = 1, sort: str = "default"
) -> dict[str, object]:
    """Возвращает JSON-результаты поиска фильмов по ключевому слову."""
    keyword, safe_page, _, results, total_count = run_keyword_search(
        keyword, page, sort
    )

    if keyword and safe_page == 1:
        log_search_query(
            "keyword",
            params={"keyword": keyword},
            results_count=total_count,
        )

    return {
        "keyword": keyword,
        "page": safe_page,
        "count": total_count,
        "results": serialize_catalog_films(results),
    }


@app.get("/ui/search/keyword")
def search_keyword_ui(
    request: Request,
    keyword: str,
    page: int = 1,
    sort: str = "default",
):
    """Готовит HTML-страницу результатов поиска по ключевому слову."""
    keyword, safe_page, sort_mode, results, total_count = run_keyword_search(
        keyword,
        page,
        sort,
    )
    total_pages = (total_count + 9) // 10 if total_count > 0 else 1
    has_prev = safe_page > 1
    has_next = safe_page < total_pages
    prev_url = build_url_with_query(
        "/ui/search/keyword",
        {"keyword": keyword, "page": safe_page - 1, "sort": sort_mode},
    )
    next_url = build_url_with_query(
        "/ui/search/keyword",
        {"keyword": keyword, "page": safe_page + 1, "sort": sort_mode},
    )
    if keyword and "page" not in request.query_params:
        log_search_query(
            "keyword",
            params={"keyword": keyword},
            results_count=total_count,
        )
    context = {
        "request": request,
        "search_kind": "keyword",
        "title": "Поиск по названию",
        "message": "Результаты поиска по названию: " + keyword,
        "filters": {
            "keyword": keyword,
            "sort": sort_mode,
        },
        "keyword": keyword,
        "page": safe_page,
        "count": total_count,
        "total_pages": total_pages,
        "sort_mode": sort_mode,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_url": prev_url,
        "next_url": next_url,
        "films": results,
        "results": results,
    }
    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context=context,
    )


@app.get("/search/genre-year")
def search_genre_year(
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    page: int = 1,
) -> dict[str, object]:
    """Возвращает JSON-результаты поиска фильмов по жанру и диапазону лет."""
    genre_text = genre or ""
    year_from_text = "" if year_from is None else str(year_from)
    year_to_text = "" if year_to is None else str(year_to)
    safe_page, _, results, total_count = run_filtered_search(
        genre=genre_text,
        year_from=year_from_text,
        year_to=year_to_text,
        page=page,
        sort_mode="default",
    )

    if safe_page == 1 and (genre_text or year_from is not None or year_to is not None):
        log_search_query(
            "genre__years_range",
            params=build_genre_year_log_params(
                actor_id="",
                genre=genre_text,
                exact_year="",
                rating="",
                rental_rate="",
                length_group="",
                year_from=year_from_text,
                year_to=year_to_text,
                sort_mode="default",
            ),
            results_count=total_count,
        )

    return {
        "genre": genre,
        "year_from": year_from,
        "year_to": year_to,
        "page": safe_page,
        "count": total_count,
        "results": serialize_catalog_films(results),
    }


@app.get("/ui/search/genre-year")
def search_genre_year_ui(
    request: Request,
    actor_id: str = "",
    genre: str | None = None,
    exact_year: str = "",
    rating: str = "",
    rental_rate: str = "",
    length_group: str = "",
    year_from: str = "",
    year_to: str = "",
    page: int = 1,
    sort: str = "default",
):
    """Готовит HTML-страницу результатов поиска по жанру и годам."""
    genre_text = genre or ""
    actor_choices = get_all_actors()
    actor_id, actor_name = resolve_actor_selection(actor_id, actor_choices)
    length_group_labels = build_length_group_labels()
    length_group_label = length_group_labels.get(length_group, "")
    safe_page, sort_mode, results, total_count = run_filtered_search(
        genre=genre_text,
        year_from=year_from,
        year_to=year_to,
        page=page,
        sort_mode=sort,
        exact_year=exact_year,
        rating=rating,
        rental_rate=rental_rate,
        length_group=length_group,
        actor_id=actor_id,
    )
    total_pages = (total_count + 9) // 10 if total_count > 0 else 1
    search_parts = build_search_parts(
        actor_name,
        genre_text,
        exact_year,
        year_from,
        year_to,
        rating,
        rental_rate,
        length_group_label,
    )
    if search_parts:
        message = "Результаты поиска: " + ", ".join(search_parts)
    else:
        message = "Введите жанр, год или диапазон годов для поиска."
    has_prev = safe_page > 1
    has_next = safe_page < total_pages
    prev_url = build_url_with_query(
        "/ui/search/genre-year",
        {
            "actor_id": actor_id,
            "genre": genre_text,
            "exact_year": exact_year,
            "rating": rating,
            "rental_rate": rental_rate,
            "length_group": length_group,
            "year_from": year_from,
            "year_to": year_to,
            "page": safe_page - 1,
            "sort": sort_mode,
        },
    )
    next_url = build_url_with_query(
        "/ui/search/genre-year",
        {
            "actor_id": actor_id,
            "genre": genre_text,
            "exact_year": exact_year,
            "rating": rating,
            "rental_rate": rental_rate,
            "length_group": length_group,
            "year_from": year_from,
            "year_to": year_to,
            "page": safe_page + 1,
            "sort": sort_mode,
        },
    )
    if search_parts and "page" not in request.query_params:
        log_search_query(
            "genre__years_range",
            params=build_genre_year_log_params(
                actor_id=actor_id,
                genre=genre_text,
                exact_year=exact_year,
                rating=rating,
                rental_rate=rental_rate,
                length_group=length_group,
                year_from=year_from,
                year_to=year_to,
                sort_mode=sort_mode,
            ),
            results_count=total_count,
        )
    context = {
        "request": request,
        "actor_choices": actor_choices,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "search_kind": "genre_year",
        "title": "Поиск по жанру и году",
        "message": message,
        "filters": {
            "actor_id": actor_id,
            "genre": genre_text,
            "exact_year": exact_year,
            "rating": rating,
            "rental_rate": rental_rate,
            "length_group": length_group,
            "year_from": year_from,
            "year_to": year_to,
            "sort": sort_mode,
        },
        "page": safe_page,
        "count": total_count,
        "total_pages": total_pages,
        "genre": genre_text,
        "exact_year": exact_year,
        "rating": rating,
        "rating_choices": RATING_CHOICES,
        "length_group": length_group,
        "length_group_options": LENGTH_GROUP_OPTIONS,
        "rental_rate": rental_rate,
        "rental_rate_options": RENTAL_RATE_OPTIONS,
        "year_from": year_from,
        "year_to": year_to,
        "sort_mode": sort_mode,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_url": prev_url,
        "next_url": next_url,
        "films": results,
        "results": results,
    }
    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context=context,
    )


@app.get("/stats/recent")
def stats_recent(limit: int = 5) -> dict[str, object]:
    """Возвращает последние поисковые запросы из MongoDB."""
    safe_limit = max(1, min(limit, 20))
    recent = get_recent_searches(safe_limit)
    return {
        "limit": safe_limit,
        "recent": recent,
    }


@app.get("/stats/popular")
def stats_popular(limit: int = 5) -> dict[str, object]:
    """Возвращает самые популярные поисковые запросы из MongoDB."""
    safe_limit = max(1, min(limit, 20))
    popular = get_popular_searches(safe_limit)
    return {
        "limit": safe_limit,
        "popular": popular,
    }
