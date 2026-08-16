"""Подключается к MySQL Sakila и выполняет SQL-поиск фильмов."""

import os
from decimal import Decimal

import mysql.connector
from mysql.connector.connection import MySQLConnection


class MySQLConfigurationError(RuntimeError):
    """Сообщает об отсутствии или неверном формате настроек MySQL."""


def get_dbconfig() -> dict[str, object]:
    """Возвращает настройки MySQL из переменных окружения контейнера."""
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE", "sakila")
    port_text = os.getenv("MYSQL_PORT", "3306")

    if not host or not user or not password:
        raise MySQLConfigurationError(
            "MySQL config is missing. Set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD "
            "and optionally MYSQL_PORT, MYSQL_DATABASE."
        )

    try:
        port = int(port_text)
    except ValueError as error:
        raise MySQLConfigurationError("MYSQL_PORT must be an integer.") from error

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


def get_connection() -> MySQLConnection:
    """Создаёт подключение к базе данных MySQL."""
    return mysql.connector.connect(**get_dbconfig())


class CatalogFilmRow:
    """Хранит данные карточки фильма и не ломает старую распаковку в шаблонах."""

    def __init__(
        self,
        film_id: int,
        title: str,
        description: str,
        release_year: int,
        rating: str | None,
        rental_rate: Decimal,
        length: int,
        category: str | None,
    ) -> None:
        self.film_id = film_id
        self.title = title
        self.description = description
        self.release_year = release_year
        self.rating = rating
        self.rental_rate = rental_rate
        self.length = length
        self.category = category
        self.genre = category

    def __iter__(self):
        """Сохраняет старый формат: шаблоны всё ещё получают 4 значения."""
        return iter((self.film_id, self.title, self.description, self.release_year))


def build_catalog_film_rows(
    raw_films: list[tuple[int, str, str, int, str | None, Decimal, int, str | None]],
) -> list[CatalogFilmRow]:
    """Преобразует SQL-строки каталога в совместимый формат для шаблонов."""
    return [
        CatalogFilmRow(
            film_id=film_id,
            title=title,
            description=description,
            release_year=release_year,
            rating=rating,
            rental_rate=rental_rate,
            length=length,
            category=category,
        )
        for (
            film_id,
            title,
            description,
            release_year,
            rating,
            rental_rate,
            length,
            category,
        ) in raw_films
    ]


def build_release_year_condition(
    year_from: str,
    year_to: str,
    exact_year: str | None = None,
) -> tuple[str | None, list[str]]:
    """Собирает условие фильтрации по году выпуска."""
    range_condition = ""
    range_parameters: list[str] = []

    if year_from and year_to:
        range_condition = "f.release_year BETWEEN %s AND %s"
        range_parameters.extend([year_from, year_to])
    elif year_from:
        range_condition = "f.release_year >= %s"
        range_parameters.append(year_from)
    elif year_to:
        range_condition = "f.release_year <= %s"
        range_parameters.append(year_to)

    if exact_year:
        if range_condition:
            # Если есть и диапазон, и точный год, объединяем их через OR.
            return (
                f"({range_condition} OR f.release_year = %s)",
                range_parameters + [exact_year],
            )

        return ("f.release_year = %s", [exact_year])

    if range_condition:
        return (range_condition, range_parameters)

    return (None, [])


def build_length_group_condition(length_group: str | None) -> str | None:
    """Возвращает SQL-условие для выбранной группы длительности фильма."""
    length_conditions = {
        "under_60": "f.length < 60",
        "60_89": "f.length BETWEEN 60 AND 89",
        "90_119": "f.length BETWEEN 90 AND 119",
        "120_149": "f.length BETWEEN 120 AND 149",
        "150_plus": "f.length >= 150",
    }
    return length_conditions.get(length_group)


def add_genre_year_rating_filters(
    query_parts: list[str],
    conditions: list[str],
    parameters: list[str],
    genre: str,
    year_from: str,
    year_to: str,
    exact_year: str | None = None,
    rating: str | None = None,
    rental_rate: str | None = None,
    length_group: str | None = None,
    actor_id: str | None = None,
) -> None:
    """Добавляет в запрос фильтры по жанру, году, рейтингу, аренде, длительности и актёру."""
    if genre:
        query_parts.append(
            "JOIN film_category AS fc_filter ON f.film_id = fc_filter.film_id"
        )
        query_parts.append(
            "JOIN category AS c_filter ON fc_filter.category_id = c_filter.category_id"
        )
        conditions.append("c_filter.name = %s")
        parameters.append(genre)

    year_condition, year_parameters = build_release_year_condition(
        year_from,
        year_to,
        exact_year,
    )
    if year_condition:
        conditions.append(year_condition)
        parameters.extend(year_parameters)

    if rating:
        conditions.append("f.rating = %s")
        parameters.append(rating)

    if rental_rate:
        conditions.append("f.rental_rate = %s")
        parameters.append(rental_rate)

    length_condition = build_length_group_condition(length_group)
    if length_condition:
        conditions.append(length_condition)

    if actor_id:
        query_parts.append("JOIN film_actor AS fa ON f.film_id = fa.film_id")
        conditions.append("fa.actor_id = %s")
        parameters.append(actor_id)


def search_films_by_keyword(
    keyword: str,
    page: int = 1,
    sort_mode: str = "default",
) -> list[CatalogFilmRow]:
    """Ищет фильмы по ключевому слову в названии."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        page = max(page, 1)

        offset = (page - 1) * 10
        order_by = "ORDER BY film_id"

        if sort_mode == "old":
            order_by = "ORDER BY release_year ASC, title ASC"
        elif sort_mode == "new":
            order_by = "ORDER BY release_year DESC, title ASC"

        # Ищем фильмы по части названия и ограничиваем выдачу 10 строками.
        query = (
            """
        SELECT
            f.film_id,
            f.title,
            f.description,
            f.release_year,
            f.rating,
            f.rental_rate,
            f.length,
            MIN(c_display.name) AS category
        FROM film AS f
        LEFT JOIN film_category AS fc_display ON f.film_id = fc_display.film_id
        LEFT JOIN category AS c_display ON fc_display.category_id = c_display.category_id
        WHERE f.title LIKE %s
        GROUP BY
            f.film_id,
            f.title,
            f.description,
            f.release_year,
            f.rating,
            f.rental_rate,
            f.length
        """
            + order_by
            + """
        LIMIT 10 OFFSET %s;
        """
        )
        search_value = f"%{keyword}%"

        cursor.execute(query, (search_value, offset))
        films = cursor.fetchall()
        return build_catalog_film_rows(films)
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def search_films_by_genre_and_year(
    genre: str,
    year_from: str,
    year_to: str,
    page: int = 1,
    sort_mode: str = "default",
    exact_year: str | None = None,
    rating: str | None = None,
    rental_rate: str | None = None,
    length_group: str | None = None,
    actor_id: str | None = None,
) -> list[CatalogFilmRow]:
    """Ищет фильмы по жанру и диапазону лет."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        page = max(page, 1)

        offset = (page - 1) * 10
        category_select = "MIN(c_display.name) AS category"

        if genre:
            category_select = "MAX(c_filter.name) AS category"

        query_parts = [
            "SELECT",
            "    f.film_id,",
            "    f.title,",
            "    f.description,",
            "    f.release_year,",
            "    f.rating,",
            "    f.rental_rate,",
            "    f.length,",
            f"    {category_select}",
            "FROM film AS f",
            "LEFT JOIN film_category AS fc_display ON f.film_id = fc_display.film_id",
            "LEFT JOIN category AS c_display ON fc_display.category_id = c_display.category_id",
        ]
        conditions: list[str] = []
        parameters: list[str] = []

        add_genre_year_rating_filters(
            query_parts,
            conditions,
            parameters,
            genre,
            year_from,
            year_to,
            exact_year,
            rating,
            rental_rate,
            length_group,
            actor_id,
        )

        if conditions:
            query_parts.append("WHERE " + " AND ".join(conditions))

        query_parts.append(
            "GROUP BY f.film_id, f.title, f.description, f.release_year, "
            "f.rating, f.rental_rate, f.length"
        )

        if sort_mode == "old":
            query_parts.append("ORDER BY f.release_year ASC, f.title ASC")
        elif sort_mode == "new":
            query_parts.append("ORDER BY f.release_year DESC, f.title ASC")
        else:
            query_parts.append("ORDER BY f.film_id")
        query_parts.append("LIMIT 10 OFFSET %s;")
        parameters.append(offset)
        query = "\n".join(query_parts)

        cursor.execute(query, tuple(parameters))
        films = cursor.fetchall()
        return build_catalog_film_rows(films)
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def search_films_by_genre_year(
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    page: int = 1,
) -> list[CatalogFilmRow]:
    """Преобразует числовые параметры маршрута и выполняет поиск фильмов."""
    return search_films_by_genre_and_year(
        genre=genre or "",
        year_from="" if year_from is None else str(year_from),
        year_to="" if year_to is None else str(year_to),
        page=page,
    )


def count_films_by_keyword(keyword: str) -> int:
    """Считает количество фильмов по ключевому слову в названии."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query_parts = [
            "SELECT COUNT(*)",
            "FROM film",
        ]
        parameters: list[str] = []

        if keyword:
            query_parts.append("WHERE title LIKE %s")
            parameters.append(f"%{keyword}%")

        query = "\n".join(query_parts)
        cursor.execute(query, tuple(parameters))
        result = cursor.fetchone()
        return result[0] if result is not None else 0
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def count_films_by_genre_and_year(
    genre: str,
    year_from: str,
    year_to: str,
    exact_year: str | None = None,
    rating: str | None = None,
    rental_rate: str | None = None,
    length_group: str | None = None,
    actor_id: str | None = None,
) -> int:
    """Считает количество фильмов по жанру и диапазону лет."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query_parts = [
            "SELECT COUNT(DISTINCT f.film_id)",
            "FROM film AS f",
        ]
        conditions: list[str] = []
        parameters: list[str] = []

        add_genre_year_rating_filters(
            query_parts,
            conditions,
            parameters,
            genre,
            year_from,
            year_to,
            exact_year,
            rating,
            rental_rate,
            length_group,
            actor_id,
        )

        if conditions:
            query_parts.append("WHERE " + " AND ".join(conditions))

        query = "\n".join(query_parts)
        cursor.execute(query, tuple(parameters))
        result = cursor.fetchone()
        return result[0] if result is not None else 0
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def split_group_concat_values(raw_value: str | None) -> list[str]:
    """Преобразует строку из GROUP_CONCAT в список значений."""
    if not raw_value:
        return []

    return [item.strip() for item in raw_value.split(", ") if item.strip()]


def get_film_details(film_id: int) -> dict | None:
    """Возвращает полную информацию о фильме по его id."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            f.film_id,
            f.title,
            f.description,
            f.release_year,
            f.rating,
            f.length,
            f.rental_duration,
            f.rental_rate,
            f.replacement_cost,
            f.special_features,
            l.name AS language,
            GROUP_CONCAT(
                DISTINCT c.name
                ORDER BY c.name
                SEPARATOR ', '
            ) AS categories,
            GROUP_CONCAT(
                DISTINCT CONCAT(a.first_name, ' ', a.last_name)
                ORDER BY a.first_name, a.last_name
                SEPARATOR ', '
            ) AS actors
        FROM film AS f
        LEFT JOIN language AS l ON f.language_id = l.language_id
        LEFT JOIN film_category AS fc ON f.film_id = fc.film_id
        LEFT JOIN category AS c ON fc.category_id = c.category_id
        LEFT JOIN film_actor AS fa ON f.film_id = fa.film_id
        LEFT JOIN actor AS a ON fa.actor_id = a.actor_id
        WHERE f.film_id = %s
        GROUP BY
            f.film_id,
            f.title,
            f.description,
            f.release_year,
            f.rating,
            f.length,
            f.rental_duration,
            f.rental_rate,
            f.replacement_cost,
            f.special_features,
            l.name;
        """

        cursor.execute(query, (film_id,))
        film = cursor.fetchone()

        if film is None:
            return None

        # Подготавливаем списки для удобного вывода на будущей detail page.
        film["categories"] = split_group_concat_values(film["categories"])
        film["actors"] = split_group_concat_values(film["actors"])

        special_features = film.get("special_features")
        if isinstance(special_features, set):
            film["special_features"] = sorted(special_features)
        elif special_features is None:
            film["special_features"] = []

        return film
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_all_categories() -> list[str]:
    """Возвращает список всех жанров из таблицы category."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT name
        FROM category
        ORDER BY name;
        """
        cursor.execute(query)
        categories = cursor.fetchall()
        return [category_name for category_name, in categories]
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_all_actors() -> list[tuple[int, str, str]]:
    """Возвращает список актёров из Sakila для фильтрации."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT actor_id, first_name, last_name
        FROM actor
        ORDER BY last_name, first_name, actor_id;
        """
        cursor.execute(query)
        actors = cursor.fetchall()
        return [
            (actor_id, first_name, last_name)
            for actor_id, first_name, last_name in actors
        ]
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_release_year_range() -> tuple[int | None, int | None]:
    """Возвращает минимальный и максимальный год выпуска фильмов."""
    connection: MySQLConnection | None = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT MIN(release_year), MAX(release_year)
        FROM film;
        """
        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            return (None, None)

        min_year, max_year = result
        return (min_year, max_year)
    finally:
        # Закрываем ресурсы после запроса.
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
