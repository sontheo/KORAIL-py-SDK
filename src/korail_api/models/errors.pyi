from __future__ import annotations

import collections.abc
import typing
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Literal, Mapping, Self, Sequence

import httpx

class KorailApiError(Exception):
    status_code: int | None
    retry_after: float | None
    next_probe_at: float | None
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, *args: object) -> None: ...

class KorailAppError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, code: str | None, message: str | None, *, raw: object = ...) -> None: ...

class KorailAppUpdateRequiredError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailAuthError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailDynaPathError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, message: str | None = ..., *, raw: object | None = ...) -> None: ...

class KorailDynaPathRequiredError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailInvalidRequestError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailNetFunnelError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, code: str | None, message: str | None, *, raw: object = ...) -> None: ...

class KorailNoResultsError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailNotEntitledError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailProcessingError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailRateLimitError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailQueueRejectedError(KorailNetFunnelError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailReservationRefusedError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailProtocolError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailSeatUnavailableError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailServiceUnavailableError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailSessionExpiredError(KorailAuthError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, code: str | None, message: str | None, *, raw: object = ...) -> None: ...

class KorailSoldOutError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailTransportError(KorailApiError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailAccountLockedError(KorailAuthError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, code: str | None, message: str | None, *, raw: object = ...) -> None: ...

class KorailAlreadyProcessedError(KorailAppError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str

class KorailAuthContinuationRequired(KorailAuthError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
    def __init__(self, redirect_url: str, *, raw: object = ...) -> None: ...

class KorailNoDirectTrainError(KorailNoResultsError):
    raw: object
    parser_raw: object
    code: str | None
    message: str | None
    display_message: str
    redirect_url: str
