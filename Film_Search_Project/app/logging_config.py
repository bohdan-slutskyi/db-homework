"""Настраивает локальные файловые логи приложения."""

import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOG_DIRECTORY = Path(__file__).resolve().parent.parent / "logs"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

SEARCH_LOGGER = logging.getLogger("film_search.search")
ERROR_LOGGER = logging.getLogger("film_search.error")


class BerlinLogFormatter(logging.Formatter):
    """Форматирует время логов в часовом поясе интерфейса."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=ZoneInfo("Europe/Berlin"))
        return timestamp.strftime(datefmt or "%Y-%m-%d %H:%M:%S")


def configure_file_logging() -> None:
    """Подключает отдельные файлы для поисков и ошибок один раз."""
    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    _add_file_handler(SEARCH_LOGGER, "search.log", logging.INFO)
    _add_file_handler(ERROR_LOGGER, "error.log", logging.ERROR)


def _add_file_handler(logger: logging.Logger, filename: str, level: int) -> None:
    """Добавляет файловый обработчик, если его ещё нет у logger."""
    log_path = LOG_DIRECTORY / filename
    resolved_log_path = str(log_path.resolve())

    for handler in logger.handlers:
        if (
            isinstance(handler, logging.FileHandler)
            and handler.baseFilename == resolved_log_path
        ):
            return

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(BerlinLogFormatter(LOG_FORMAT))

    logger.setLevel(level)
    logger.propagate = False
    logger.addHandler(handler)
