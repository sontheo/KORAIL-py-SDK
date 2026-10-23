from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from pathlib import Path
from typing import TypeVar

import httpx

from korail_api.models import errors as E

SERVICE_STATUS_PATH: str
_Error = TypeVar("_Error", bound=E.KorailApiError)

def origin(url: object) -> str: ...
def http_error_details(error: _Error, response: httpx.Response, now: float) -> _Error: ...

class MaintenanceDeferredError(E.KorailServiceUnavailableError):
    next_probe_at: float
    retry_after: float
    def __init__(self, next_probe_at: float, now: float) -> None: ...

class MaintenancePolicy:
    state_path: str | None
    clock: Callable[[], float]
    def __init__(
        self,
        *,
        state_path: str | Path | None = ...,
        delays: Sequence[float] = ...,
        network_failure_threshold: int = ...,
        probe_lease: float = ...,
        clock: Callable[[], float] = ...,
        jitter: Callable[[float], float] | None = ...,
    ) -> None: ...
    def check(self, url: str) -> None: ...
    def failure(self, url: str, error: BaseException, *, probe: float = ...) -> float | None: ...
    def success(self, url: str, *, probe: float = ...) -> None: ...
    def request(self, url: str, *, probe: bool = ...) -> AbstractContextManager[None]: ...

def default_policy() -> MaintenancePolicy: ...
