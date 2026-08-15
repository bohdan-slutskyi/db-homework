"""Содержит повторно используемые функции подготовки параметров поиска."""

from urllib.parse import urlencode

RATING_CHOICES = ["G", "PG", "PG-13", "R", "NC-17"]
RENTAL_RATE_CHOICES = ["0.99", "2.99", "4.99"]
RENTAL_RATE_OPTIONS = [
    ("0.99", "$0.99"),
    ("2.99", "$2.99"),
    ("4.99", "$4.99"),
]
LENGTH_GROUP_CHOICES = ["under_60", "60_89", "90_119", "120_149", "150_plus"]
LENGTH_GROUP_OPTIONS = [
    ("under_60", "до 60 мин."),
    ("60_89", "60-89 мин."),
    ("90_119", "90-119 мин."),
    ("120_149", "120-149 мин."),
    ("150_plus", "150+ мин."),
]


def build_url_with_query(path: str, params: dict[str, object]) -> str:
    """Собирает URL с query-параметрами, пропуская пустые значения."""
    filtered_params = {
        key: value for key, value in params.items() if value is not None and value != ""
    }
    return f"{path}?{urlencode(filtered_params)}"


def is_exact_year_outside_range(
    exact_year: str,
    year_from: str,
    year_to: str,
) -> bool:
    """Проверяет, нужно ли показывать точный год отдельно от диапазона."""
    if not exact_year:
        return False

    if not year_from or not year_to:
        return True

    try:
        exact_year_int = int(exact_year)
        year_from_int = int(year_from)
        year_to_int = int(year_to)
    except ValueError:
        return True

    return exact_year_int < year_from_int or exact_year_int > year_to_int


def build_search_parts(
    actor_name: str,
    genre: str,
    exact_year: str,
    year_from: str,
    year_to: str,
    rating: str = "",
    rental_rate: str = "",
    length_group_label: str = "",
) -> list[str]:
    """Собирает текст активных фильтров для сообщения."""
    search_parts: list[str] = []

    if actor_name:
        search_parts.append("Актёр: " + actor_name)

    if genre:
        search_parts.append(genre)

    if year_from and year_to:
        search_parts.append("Годы: " + year_from + " - " + year_to)
    elif year_from:
        search_parts.append("Годы от: " + year_from)
    elif year_to:
        search_parts.append("Годы до: " + year_to)

    if exact_year and is_exact_year_outside_range(exact_year, year_from, year_to):
        search_parts.append("Год: " + exact_year)

    if rating:
        search_parts.append("Рейтинг: " + rating)

    if rental_rate:
        search_parts.append("Стоимость: $" + rental_rate)

    if length_group_label:
        search_parts.append("Длительность: " + length_group_label)

    return search_parts


def build_genre_year_log_params(
    actor_id: str,
    genre: str,
    exact_year: str,
    rating: str,
    rental_rate: str,
    length_group: str,
    year_from: str,
    year_to: str,
    sort_mode: str,
) -> dict[str, str]:
    """Собирает params для логирования поиска по фильтрам."""
    years_range = ""
    if year_from and year_to:
        years_range = year_from + "-" + year_to
    elif exact_year:
        years_range = exact_year
    elif year_from:
        years_range = year_from + "-"
    elif year_to:
        years_range = "-" + year_to

    params = {
        "actor_id": actor_id,
        "genre": genre,
        "years_range": years_range,
        "exact_year": exact_year,
        "rating": rating,
        "year_from": year_from,
        "year_to": year_to,
        "sort": sort_mode,
    }

    if rental_rate:
        params["rental_rate"] = rental_rate

    if length_group:
        params["length_group"] = length_group

    return params


def build_length_group_labels() -> dict[str, str]:
    """Возвращает словарь подписей для групп длительности."""
    return {value: label for value, label in LENGTH_GROUP_OPTIONS}


def resolve_actor_selection(
    actor_id_text: str,
    actor_choices: list[tuple[int, str, str]],
) -> tuple[str, str]:
    """Проверяет actor_id и возвращает id с отображаемым именем актёра."""
    if not actor_id_text or not actor_id_text.isdigit():
        return ("", "")

    actor_names = {
        str(actor_id): first_name + " " + last_name
        for actor_id, first_name, last_name in actor_choices
    }
    actor_id = actor_id_text if actor_id_text in actor_names else ""
    actor_name = actor_names.get(actor_id, "")
    return (actor_id, actor_name)


def parse_positive_int(value: str, default: int = 1) -> int:
    """Преобразует строку в положительный номер страницы."""
    try:
        number = int(value)
    except ValueError:
        return default

    if number < 1:
        return default

    return number


def parse_non_negative_int(value: str, default: int = 0) -> int:
    """Преобразует строку в неотрицательное число для offset-параметров."""
    try:
        number = int(value)
    except ValueError:
        return default

    if number < 0:
        return default

    return number


def get_last_offset(total_count: int, page_size: int) -> int:
    """Возвращает offset для последней страницы статистики."""
    if total_count <= 0:
        return 0
    return ((total_count - 1) // page_size) * page_size
