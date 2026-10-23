"""Shared maintenance cooldowns; callers schedule probes, never transactions.

The default policy is shared within this process. Pass a policy with state_path
to share deadlines and probe leases across processes and restarts.
"""

from __future__ import annotations

import math
import os
import random
import sqlite3
import threading
import time
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from korail_api.models import errors as E

SERVICE_STATUS_PATH = "/file/CACHE/MobileService.cache"


def origin(url):
    parsed = urlsplit(str(url))
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return f"{parsed.scheme.lower()}://{(parsed.hostname or '').lower()}:{port}"


def http_error_details(error, response, now):
    """Keep useful HTTP metadata without retaining headers, cookies or requests."""
    error.status_code = response.status_code
    error.retry_after = None
    value = response.headers.get("Retry-After", "").strip()
    try:
        if value.isascii() and value.isdigit():
            seconds = float(value)
        else:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            seconds = max(0.0, date.timestamp() - now)
        if math.isfinite(seconds):
            error.retry_after = seconds
    except (ValueError, TypeError, OverflowError):
        pass
    return error


class MaintenanceDeferredError(E.KorailServiceUnavailableError):
    """No request was sent. next_probe_at is a UTC Unix timestamp."""

    def __init__(self, next_probe_at, now):
        super().__init__("CLIENT_MAINTENANCE_WAIT", "Service cooldown; only a due status probe is allowed")
        self.next_probe_at = next_probe_at
        self.retry_after = max(0.0, next_probe_at - now)


@dataclass
class _State:
    failures: int = 0
    step: int = 0
    next_probe_at: float = 0.0
    lease_until: float = 0.0


class MaintenancePolicy:
    def __init__(
        self,
        *,
        state_path: str | Path | None = None,
        delays=(1800, 3600, 7200, 14400),
        network_failure_threshold=2,
        probe_lease=300,
        clock=time.time,
        jitter=None,
    ):
        if not delays or any(not math.isfinite(d) or d <= 0 for d in delays):
            raise ValueError("Cooldown delays must be positive finite seconds")
        if type(network_failure_threshold) is not int or network_failure_threshold < 1:
            raise ValueError("Network failure threshold must be a positive integer")
        if not math.isfinite(probe_lease) or probe_lease <= 0:
            raise ValueError("Probe lease must be positive finite seconds")
        self.delays = tuple(delays)
        self.network_failure_threshold = network_failure_threshold
        self.probe_lease = probe_lease
        self.clock = clock
        self.jitter = jitter or (lambda delay: random.uniform(0, delay * 0.1))
        self._states = {}
        self._lock = threading.RLock()
        self.state_path = str(state_path) if state_path is not None else None
        if self.state_path is not None:
            # The parent directory is chosen and created by the application.
            fd = os.open(self.state_path, os.O_CREAT | os.O_RDWR, 0o600)
            os.close(fd)
            with closing(sqlite3.connect(self.state_path)) as db, db:
                db.execute(
                    "CREATE TABLE IF NOT EXISTS maintenance ("
                    "scope TEXT PRIMARY KEY, failures INTEGER, step INTEGER, "
                    "next_probe_at REAL, lease_until REAL)"
                )

    @contextmanager
    def _state(self, scope):
        with self._lock:
            if self.state_path is None:
                yield self._states.setdefault(scope, _State())
                return
            with closing(sqlite3.connect(self.state_path, timeout=10)) as db, db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT failures, step, next_probe_at, lease_until FROM maintenance WHERE scope=?",
                    (scope,),
                ).fetchone()
                state = _State(*row) if row else _State()
                yield state
                db.execute(
                    "INSERT OR REPLACE INTO maintenance VALUES (?, ?, ?, ?, ?)",
                    (scope, state.failures, state.step, state.next_probe_at, state.lease_until),
                )

    def check(self, url):
        """Reject ordinary calls throughout cooldown, even when a probe is due."""
        now = self.clock()
        with self._state(origin(url)) as state:
            deadline = max(state.next_probe_at, state.lease_until)
        if deadline:
            raise MaintenanceDeferredError(deadline, now)

    def _acquire(self, url, probe):
        now = self.clock()
        denied = None
        claimed = 0.0
        with self._state(origin(url)) as state:
            deadline = max(state.next_probe_at, state.lease_until)
            if deadline:
                if not probe or now < deadline:
                    denied = deadline
                else:
                    state.lease_until = now + self.probe_lease
                    claimed = state.lease_until
        if denied is not None:
            raise MaintenanceDeferredError(denied, now)
        return claimed

    def failure(self, url, error, *, probe=0.0):
        """Record only explicit unavailability or repeated transport failures."""
        unavailable = isinstance(error, (E.KorailServiceUnavailableError, E.KorailRateLimitError))
        status = getattr(error, "status_code", None)
        unavailable = unavailable or status in {429, 503}
        transient = isinstance(error, (E.KorailTransportError, E.KorailNetFunnelError)) and (
            (status is not None and status >= 500)
            or (status is None and isinstance(error.__cause__, httpx.TransportError))
        )
        if isinstance(error, E.KorailQueueRejectedError):
            transient = False
        # Access/authentication rejections and malformed JSON do not prove an outage.
        if isinstance(error, MaintenanceDeferredError):
            return error.next_probe_at
        if not (probe or unavailable or transient):
            self.success(url)
            return None
        now = self.clock()
        with self._state(origin(url)) as state:
            if probe and state.lease_until != probe:
                return state.next_probe_at or None
            if state.next_probe_at and not probe:
                return state.next_probe_at
            state.failures += 1
            if probe or unavailable or state.failures >= self.network_failure_threshold:
                delay = self.delays[min(state.step, len(self.delays) - 1)]
                extra = self.jitter(delay)
                if not math.isfinite(extra) or extra < 0:
                    extra = 0
                retry_after = getattr(error, "retry_after", None) or 0
                state.next_probe_at = now + max(delay + extra, retry_after)
                state.step += 1
                state.failures = 0
                state.lease_until = 0
                error.next_probe_at = state.next_probe_at
                return state.next_probe_at
        return None

    def success(self, url, *, probe=0.0):
        with self._state(origin(url)) as state:
            if (probe and state.lease_until == probe) or not state.next_probe_at:
                state.failures = state.step = 0
                state.next_probe_at = state.lease_until = 0

    @contextmanager
    def request(self, url, *, probe=False):
        claimed = self._acquire(url, probe)
        try:
            yield
        except BaseException as error:
            try:
                self.failure(url, error, probe=claimed)
            except Exception as storage_error:
                error.add_note(f"Maintenance bookkeeping failed ({type(storage_error).__name__})")
            raise
        else:
            self.success(url, probe=claimed)


_DEFAULT_POLICY = MaintenancePolicy()


def default_policy():
    return _DEFAULT_POLICY
