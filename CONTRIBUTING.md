# Contributing

Use Python 3.11 or newer and a dedicated environment. The project distribution is `korail-api`; the current repository name is `korail-api_v2`.

```sh
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pip check
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/python tools/validation/check_decoder_equivalence.py
```

Tests use synthetic data and block socket connections and native curl requests. Do not add live authentication, reservations, cancellation, payment or refund to automated checks. Keep credentials, account identifiers, passenger details and payment data out of fixtures, logs and issue reports.

## Public API

Maintain the `korail_api` public exports, constructor signatures, enum values, request ordering, raw-response identity and error distinctions. Transaction requests must not be retried automatically. Preserve whole-response and nested parser context on failures while treating that context as sensitive. Extend the standalone tests when changing behavior.

Synthetic outcomes under `tools/validation/observations/` are development-only test data and are excluded from release artifacts.

## Performance

```sh
.venv/bin/python tools/performance/search_matrix.py
.venv/bin/python tools/performance/profile_search.py
```

These tools exercise mock transports. Do not equate offline CPU timing with server latency or transaction acceptance.

## Packaging

Use an empty `dist/` directory for a new build:

```sh
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
.venv/bin/python tools/packaging/check_artifacts.py dist/*.whl --sdist dist/*.tar.gz
```

The checker installs the wheel into a temporary target without index access or dependency downloads, verifies the public namespace with editable startup hooks disabled, and runs the standalone tests from the extracted source archive. Dependencies must already be installed in the invoking environment. Project license/NOTICE files and current legal documentation must remain included; captured observations, reports, validators and performance tools must remain excluded.

Review `LEGAL.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md` and `PROVENANCE.md` before redistributing. Attribution does not establish rights to vendor message text. Do not add third-party code or data without documenting origin and reviewing applicable rights. Building artifacts does not publish a package; this development version is not a PyPI release.

## Documentation

```sh
.venv/bin/python -m pip install -r docs/requirements.txt
.venv/bin/python -m mkdocs build --strict
```

Keep public prose in English. Station names and protocol/vendor text retain the spelling required by their data contracts. See `ARCHITECTURE.md` for responsibility boundaries. GitHub issue and pull request templates describe the information needed to review a change without disclosing sensitive data.
