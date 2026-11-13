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

The default `dynapath_mode="v2-declaration"` generates software declaration tokens with fresh timestamps/nonces and one synthetic identity per configuration. It does not enroll a device or implement hardware attestation. Configuration copies retain that identity; applications needing continuity across restarts should explicitly restore a private device profile with `build_config_from_profile` or `build_config_from_env`. No identity or credentials are loaded from disk automatically.

Ordinary schedule requests and ordinary single-train reservations select protocol version `250722001` when the version was omitted. An explicitly supplied `KorailConfig.version` is preserved. With the declaration provider, an immediate reservation without designated seats uses the observed GET/query profile, retaining empty second-journey/card fields and the passenger block ordering. Other reservation types, designated seats, externally supplied signers and disabled/non-allowlisted paths retain their existing request formats. Selection occurs before transmission: a rejection never triggers a POST/GET fallback or a second transaction.

Prepared reservation URLs contain journey details; avoid logging URLs, token headers, cookies or complete responses. For diagnostics, retain only the operation, method, endpoint path, protocol version, HTTP status and error code.

Explicit `dynapath_mode="v2-diagnostic"` retains the earlier diagnostic profile (including the ordinary-schedule `201` marker); `"legacy"` retains the older serializer. These modes do not establish that a live reservation is accepted. External token providers remain supported through `DynapathConfig`. Rejections raise `KorailDynaPathError` without retrying or cycling tokens, including HTTP 200 responses containing `code=-8005`.

Applications explicitly setting `KORAIL_DYNAPATH_MODE=v2-diagnostic` must select `v2-declaration` after installing the updated package to use the new profile. A package default does not override an explicit application setting; updating this checkout does not redeploy an existing service.

The declaration provider's default board is unspecified and StrongBox is false. Applications can configure accurate additional facts using `korail_api.security.declaration.DeclarationTokenProvider` (`device_id`, `model`, `release`, `manufacturer`, `board`, `sdk_int`, `strongbox`) as their token provider. These inputs are declarations, not proof of hardware or registration. The codec is checked against two recorded emulator vectors and the ordinary-reservation query against 17 independently intercepted synthetic pykorail requests. This checkout has not sent a live transaction to validate the new implementation; server acceptance can change.

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

The repository’s `.github/CONTRIBUTING.md` documents offline validation, isolated artifact checks and documentation builds. The [validation guide](VALIDATION.md) lists observed results and limitations.

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
