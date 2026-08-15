"""Подготавливает Python-данные для отображения карточек фильмов."""

from typing import Any


def get_film_card_style(film_id: int) -> dict[str, int]:
    """Возвращает детерминированный визуальный fingerprint карточки фильма."""
    return {
        "hue": (film_id * 37) % 360,
        "secondary_hue": (film_id * 53) % 360,
        "pattern_variant": film_id % 10,
        "pattern_angle": (film_id * 29) % 180,
        "pattern_gap": 14 + (film_id % 13),
        "pattern_offset": (film_id * 11) % 37,
        "dot_size": 1 + (film_id % 3),
        "glow_x": (film_id * 17) % 100,
        "glow_y": (film_id * 23) % 100,
        "glow_x_alt": (film_id * 31) % 100,
        "glow_y_alt": (film_id * 43) % 100,
        "wave_stop": 24 + (film_id % 18),
        "shape_size": 6 + (film_id % 9),
        "shape_gap": 18 + (film_id % 17),
        "shape_angle": (film_id * 41) % 180,
        "shape_offset": (film_id * 19) % 43,
        "corner_radius": 10 + (film_id % 21),
        "density": 3 + (film_id % 7),
        "stripe_width": 1 + (film_id % 3),
        "grid_size": 16 + (film_id % 15),
    }


def get_film_poster_panel(title: str, film_id: int) -> dict[str, Any]:
    """Готовит данные title-based постера для карточки каталога."""
    words = title.split()
    if not words:
        words = ["UNTITLED"]

    title_lines: list[str]
    if len(words) == 1:
        title_lines = [words[0]]
    elif len(words) == 2:
        title_lines = [words[0], words[1]]
    elif len(words) == 3:
        line_variants = [
            [words[0], words[1], words[2]],
            [f"{words[0]} {words[1]}", words[2]],
            [words[0], f"{words[1]} {words[2]}"],
        ]
        title_lines = min(
            line_variants, key=lambda lines: max(len(line) for line in lines)
        )
    else:
        target_line_count = 3
        title_lines = []
        start_index = 0

        for line_index in range(target_line_count):
            remaining_words = len(words) - start_index
            remaining_lines = target_line_count - line_index
            words_in_line = max(1, remaining_words // remaining_lines)
            end_index = start_index + words_in_line
            title_lines.append(" ".join(words[start_index:end_index]))
            start_index = end_index

        if start_index < len(words):
            title_lines[-1] = title_lines[-1] + " " + " ".join(words[start_index:])

    main_word = max(words, key=len)
    longest_line_length = max(len(line) for line in title_lines)

    if longest_line_length >= 16:
        title_size = "sm"
    elif longest_line_length >= 10:
        title_size = "md"
    else:
        title_size = "lg"

    if len(words) >= 4:
        title_align = "left"
    elif film_id % 3 == 0:
        title_align = "center"
    else:
        title_align = "left"

    if len(main_word) >= 9:
        title_weight = "black"
    elif len(main_word) >= 6:
        title_weight = "bold"
    else:
        title_weight = "semibold"

    return {
        "title_lines": title_lines,
        "main_word": main_word,
        "title_size": title_size,
        "title_align": title_align,
        "title_weight": title_weight,
        "poster_variant": film_id % 6,
    }


def add_card_styles(films: list[Any]) -> list[Any]:
    """Добавляет карточкам каталога детерминированный визуальный fingerprint."""
    for film in films:
        if isinstance(film, dict):
            film_id = film.get("film_id")
            title = film.get("title")
            if isinstance(film_id, int):
                film["card_style"] = get_film_card_style(film_id)
                if isinstance(title, str):
                    # poster_panel готовит title-based данные для сгенерированной постерной панели.
                    film["poster_panel"] = get_film_poster_panel(title, film_id)
            continue

        film_id = getattr(film, "film_id", None)
        title = getattr(film, "title", None)
        if isinstance(film_id, int):
            film.card_style = get_film_card_style(film_id)
            if isinstance(title, str):
                # poster_panel готовит title-based данные для сгенерированной постерной панели.
                film.poster_panel = get_film_poster_panel(title, film_id)

    return films


def serialize_catalog_films(films: list[Any]) -> list[dict[str, object]]:
    """Преобразует строки каталога в словари для JSON-ответа."""
    serialized_films: list[dict[str, object]] = []

    for film in films:
        if isinstance(film, dict):
            serialized_films.append(dict(film))
            continue

        serialized_films.append(
            {
                "film_id": film.film_id,
                "title": film.title,
                "description": film.description,
                "release_year": film.release_year,
                "rating": film.rating,
                "rental_rate": film.rental_rate,
                "length": film.length,
                "category": film.category,
                "genre": film.genre,
            }
        )

    return serialized_films
