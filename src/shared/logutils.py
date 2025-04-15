from enum import Enum
from contextvars import ContextVar
from contextlib import contextmanager
from collections.abc import Generator

CTX_DEFAULT = ""

ctx_request_id = ContextVar("RequestId", default=CTX_DEFAULT)
ctx_current_user = ContextVar("CurrentUser", default=CTX_DEFAULT)


class CtxVarEnum(Enum):
    RequestId = ctx_request_id
    CurrentUser = ctx_current_user


@contextmanager
def set_logging_var(enum: CtxVarEnum, value: str) -> Generator:
    ctx_var = enum.value
    ctx_var.set(value)
    yield
    ctx_var.set(CTX_DEFAULT)
