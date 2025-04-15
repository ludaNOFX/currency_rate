import os
import logging
import logging.handlers
import sys
from pathlib import Path

from application.settings import Base
from shared.logutils import CtxVarEnum


class CustomLogRecord(logging.LogRecord):
    """Расширенный LogRecord с дополнительными атрибутами."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_message: str = ""


logging.setLogRecordFactory(CustomLogRecord)


class ExtraCtxFilter(logging.Filter):
    """Фильтр для добавления контекстных переменных в логи."""

    CTX_VARIABLES_LIST = [var.value for var in list(CtxVarEnum)]

    def filter(self, record: CustomLogRecord) -> CustomLogRecord:
        extra_ctx_msg_lst = []
        for ctx_var in self.CTX_VARIABLES_LIST:
            value = ctx_var.get()
            if not value:
                continue
            extra_ctx_msg_lst.append(f"{ctx_var.name}: {value}")
        extra_message = ", ".join(extra_ctx_msg_lst)
        record.extra_message = extra_message or ""

        return record


def _disable_loggers(*names: str) -> None:
    """Отключить ненужные логгеры"""
    for n in names:
        lgr = logging.getLogger(n)
        if lgr.hasHandlers():
            lgr.disabled = True


def _set_lvl_loggers(level: int, *names: str) -> None:
    """Настройка уровня логгирования для конкретных логгеров"""
    for n in names:
        lgr = logging.getLogger(n)
        if lgr.hasHandlers():
            lgr.setLevel(level=level)


def logging_setup(settings: Base) -> None:
    """Настройка логгирования для сервиса"""
    format_date = "%d-%m-%Y %H:%M:%S"
    format_ctx_extended = "%(asctime)s - [%(levelname)s] - [%(extra_message)s] - %(name)s(%(lineno)d): %(message)s"  # noqa: E501

    base_level = logging.DEBUG if settings.DEBUG else logging.INFO

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(ExtraCtxFilter())

    handlers = [
        console_handler,
    ]

    # Только для local — добавляем логирование в файл
    if settings.PROJ_ENV == "local":
        log_dir_path = settings.BASE_DIR.joinpath(settings.LOG_DIR)
        os.makedirs(log_dir_path, exist_ok=True)

        log_file_path = Path(os.path.join(log_dir_path, "application.log"))
        file_handler = logging.handlers.WatchedFileHandler(
            filename=log_file_path,
            encoding="utf-8",
        )
        file_handler.addFilter(ExtraCtxFilter())
        handlers.append(file_handler)

    logging.basicConfig(
        format=format_ctx_extended,
        datefmt=format_date,
        level=base_level,
        handlers=handlers,
    )

    info_level_loggers = [
        "faker.factory",
        "asyncio",
    ]
    _set_lvl_loggers(logging.INFO, *info_level_loggers)

    # Настройка логгеров HTTP-библиотек в зависимости от debug-режима
    http_loggers = ["httpx", "httpcore"]
    _set_lvl_loggers(logging.WARNING, *http_loggers)
