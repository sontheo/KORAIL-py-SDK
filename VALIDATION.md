# Validation record

## Maintenance corrections (2026-10-23)

Maintenance protection defaults to shared in-memory state, without database setup. Single recovery probes, long backoff intervals, server retry metadata, optional restart persistence, queue budgets, strict result envelopes and transaction response preservation are covered by the standalone synthetic suite. No live requests were made. In this checkout, 271 standalone tests, all 1,915 recorded decoder comparisons, strict mypy, Ruff lint/format and the strict documentation build passed locally on 2026-10-23. The standalone suite includes a separate-process probe exclusion test and retained response context after bookkeeping failures.

## Checks for this repository

The current implementation is the root package, version `0.1.0`. Local publication checks use Python 3.12.3 on Linux ARM64. The CI matrix is configured for Python 3.11–3.14 with current dependencies and Python 3.11 with declared runtime/build lower bounds. Remote outcomes must be read from the actual workflow results.

| Check | Local result |
| --- | --- |
| Standalone contract and failure suite | 271 tests passed |
| Captured synthetic decoder outcomes | All 1,915 equivalent |
| Public namespace inventory | All 239 exports available in `korail_api` |
| Client method inventory | All 86 public methods preserved |
| Static consumer | Strict mypy passed |
| Style | Ruff lint and format passed |
| Documentation | Strict MkDocs build passed |
| Packaging | Wheel and source archive built; metadata and isolated checks passed |

All test requests use synthetic responses. Socket guards and native curl guards block network traffic. No live login, reservation, cancellation, payment or refund validates this development version. Offline behavior does not establish live-service acceptance or current network latency.

## Performance checks

The mock-search benchmarks and profiler exercise the current implementation with synthetic responses and a retained httpx transport. Each search reaches the mock transport once. Endpoint URL objects and immutable decode plans may be cached; response bodies, seat availability and transaction outcomes are never cached.

These measurements describe local CPU/mock-HTTP work and do not establish live-service latency or transaction acceptance.

## Reproduce current checks

```sh
python -m pip install -e '.[dev]'
python -m pytest
ruff check .
ruff format --check .
mypy
python tools/validation/check_decoder_equivalence.py
python tools/performance/search_matrix.py
python -m build
python -m twine check dist/*
python tools/packaging/check_artifacts.py dist/*.whl --sdist dist/*.tar.gz
```

The artifact checker installs the wheel into a temporary target with pip using `--no-index --no-deps`, then runs Python with `-I -S`. Only the installed artifact and dependency site-packages are supplied; editable startup hooks are disabled. It verifies module origins, the public namespace, version metadata, serialization, message access and a synthetic search. It rejects reference code, captured observations and development comparison tools in the archives, then runs the 271 standalone tests from the extracted source archive.

This is an engineering validation record. It does not establish vendor-data redistribution rights or permission to access external services.
