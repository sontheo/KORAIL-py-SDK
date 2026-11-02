# Changelog

## Unreleased

- Default to software declaration tokens with fresh request timestamps/nonces and a configuration-scoped synthetic identity; retain explicit diagnostic/legacy modes and external signers.
- Align ordinary immediate reservations without designated seats with the observed GET/query profile, default wire version, blank fields and passenger ordering. Preserve explicit versions and other reservation formats.
- Verify the codec against recorded emulator output digests and complete ordinary-reservation queries against independently intercepted synthetic reference requests. No live transaction was executed, and no transaction retry or protocol fallback was added.

## 0.1.0 — 2026-10-23

- Reject invalid result envelopes and prevent queue error retries from exceeding the admission budget.
- Add shared in-memory maintenance cooldowns, server retry metadata, single recovery probes and optional SQLite persistence.
- Stop queue error bypass and final-failure sleeps; bound queue admission to 300 seconds by default (explicit `None` remains unlimited).

- Publish the current implementation in the new `korail-api_v2` repository, with a new Git history.
- Expose 239 public exports, 86 client methods and typed model/request contracts.
- Separate protocol, transport, service, configuration, model, message and security responsibilities.
- Retain tested failure context, queue behavior, error distinctions and transaction protections.
- Reuse resolved endpoint URLs and simplify common-envelope decoding; see [`docs/VALIDATION.md`](docs/VALIDATION.md) for offline checks and limits.
- Include standalone tests, typed public declarations, isolated artifact verification and CI.
- Keep runtime annotation installation compatible with Python 3.14's unified union types.
- Add English documentation, original banner artwork and explicit legal/provenance notices.

GitHub release `v0.1.0` includes the wheel and source archive. The package has not been uploaded to PyPI. Offline validation and live-service validation are distinct; this release has no live authentication or transaction acceptance claim.
