# Installation and usage

Use Python 3.11 or newer. From a checkout of the current source:

```sh
python -m venv .venv
.venv/bin/python -m pip install '.[socks]'
```

Install from source; this package is not available on PyPI. Import the public API from `korail_api`:

```python
from korail_api import KorailClient, TrainSearchQuery

with KorailClient() as client:
    response = client.search_trains(TrainSearchQuery("서울", "부산", "20991230", "090000"))
    for train in response.trains:
        print(train.train_no, train.departure_time)
```

Replace the example date with a valid travel date. Executing this example sends a real schedule request; automated tests do not execute it. Always close clients or use a context manager to release their transports.

The default ordinary schedule request uses an observed compatibility marker, `201`, and protocol version `250722001`. The marker is not a native or device-bound signature; the server may stop accepting it. A rejection raises `KorailDynaPathError` without retrying or trying other tokens. For an authenticated or future protocol, applications can supply a token provider through `DynapathConfig`; explicitly supplied `KorailConfig.version` values are sent unchanged. The compatibility marker and automatic version selection apply only when DynaPath is enabled and the ordinary schedule endpoint is in the configured allowlist. Special schedules and other operations are not covered by the anonymous live check.

For the default OkHttp transport, proxy environment variables are evaluated per request and `NO_PROXY` exclusions are honored. An explicit `KorailConfig(proxy=...)` takes precedence over both proxy environment variables and `NO_PROXY`; a failed explicit proxy is not silently bypassed.

## External request signer

`PreparedRequestSigner` is an optional adapter for a separately supplied signer. It is not a DynaPath implementation and does not register a device. It receives the final HTTP method, URL and SHA-256 digest of the exact body bytes, after URL and body encoding. The signer returns the token header value. `SigningRequest` hides the URL and digest in its representation; the signer must also avoid logging them or its token. The old `token_provider` interface remains supported.

```python
from korail_api import DynapathConfig, KorailConfig
from korail_api.security.signing import PreparedRequestSigner, SigningRegistrationRequired


def sign_request(request):
    # Replace this with an independently provisioned signer; never log request data.
    raise SigningRegistrationRequired()


config = KorailConfig(
    version="250722001",
    dynapath=DynapathConfig(enabled=True, token_provider=PreparedRequestSigner(sign_request)),
)
```

The adapter sends no protected request when signing fails. Errors have codes `SIGNER_REGISTRATION_REQUIRED`, `SIGNER_TIMEOUT`, `SIGNER_UNAVAILABLE`, `SIGNER_FAILED`, or `SIGNER_INVALID_TOKEN`. The signer is responsible for its own timeout, device-registration state, and synchronization of any challenge or counter across callers. No automatic enrollment, state persistence, token fallback or transaction replay is performed. Request event hooks and client authentication are rejected for signed requests because they could modify a request after signing; custom transports must not modify the signed URL or body. This interface does not establish that any signer or registration will be accepted by KORAIL.

For local development:

```sh
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
```

Tests use mock transports. A transaction response that cannot be decoded retains whole-response context in `error.raw` and nested context in `error.parser_raw` when available. Do not automatically retry a reservation or payment after an ambiguous outcome. Handle a business rejection separately from a malformed response or expired session.

The root `CONTRIBUTING.md` documents offline validation, isolated artifact checks and documentation builds. The [validation record](VALIDATION.md) lists observed results and limitations.

## Maintenance cooldown

Maintenance and rate-limit responses block requests locally for 30 minutes, 1 hour, 2 hours, then 4 hours, plus up to 10% jitter. A longer server `Retry-After` is respected. Two consecutive transport failures also trigger cooldown; authentication and application-version errors alone do not.

After the deadline, the application must explicitly request `client.get_service_status()`. One successful status probe reopens service. Ordinary calls remain blocked until then, and the library never starts background polling. Schedule the probe only while work is pending; do not automatically repeat an ambiguous reservation or payment.

For a single-process application, use the default in-memory policy. No database setup is needed; clients in that process share cooldowns and recovery-probe exclusion. Restarting the process clears this state, so the next call may contact the server again.

```python
from korail_api import KorailApiError, KorailClient

with KorailClient() as client:
    try:
        status = client.get_service_status()
    except KorailApiError as error:
        if error.next_probe_at is None:
            raise
        next_check_at = error.next_probe_at  # UTC Unix timestamp for your scheduler.
```

SQLite is optional for applications needing restart persistence or multiple processes. Import `MaintenancePolicy` from `korail_api.maintenance`, create it with a shared local `state_path`, and pass it as `KorailClient(maintenance=policy)`. The parent directory must already exist. It stores no credentials or response bodies. Configure `probe_lease` above your maximum status-request duration if you increase timeouts beyond the default 5-minute lease.

Server failures expose `status_code`, `retry_after` and `next_probe_at` where available. Invalid result envelopes are rejected; maintenance protection also applies to `raise_on_fail=False`. Queue errors cannot bypass admission. The default queue wait budget is 300 seconds; explicit `netfunnel_wait_limit=None` still permits unlimited normal queue waiting. An already-running request and token cleanup may finish after the budget.
