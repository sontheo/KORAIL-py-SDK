# Validation record

## Maintenance corrections (2026-10-23)

Maintenance protection defaults to shared in-memory state, without database setup. Single recovery probes, long backoff intervals, server retry metadata, optional restart persistence, queue budgets, strict result envelopes and transaction response preservation are covered by the standalone synthetic suite. No live requests were made. In this checkout, 271 standalone tests, all 1,915 recorded decoder comparisons, strict mypy, Ruff lint/format and the strict documentation build passed locally on 2026-10-23. The standalone suite includes a separate-process probe exclusion test and retained response context after bookkeeping failures.

## Checks for this repository

The current implementation is the root package, version `0.1.0.dev0`. Local publication checks use Python 3.12.3 on Linux ARM64. The CI matrix is configured for Python 3.11–3.14 with current dependencies and Python 3.11 with declared runtime/build lower bounds. Remote outcomes must be read from the actual workflow results.

| Check | Local result |
| --- | --- |
| Standalone contract and failure suite | 271 tests passed |
| Captured synthetic decoder outcomes | All 1,915 equivalent |
| Public namespace inventory | All 239 exports available in both namespaces |
| Client method inventory | All 86 public methods preserved |
| Static consumer | Strict mypy passed |
| Style | Ruff lint and format passed |
| Documentation | Strict MkDocs build passed |
| Packaging | Wheel and source archive built; metadata and isolated checks passed |

All test requests use synthetic responses. Socket guards and native curl guards block network traffic. No live login, reservation, cancellation, payment or refund validates this development version. Offline behavior does not establish live-service acceptance or current network latency.

## Historical compatibility evidence

Before this repository was created, the previous development checkout ran 2,504 original tests and 36 subtests against the original runtime. Against the new implementation, 2,459 behavioral tests and 36 subtests passed, with 37 selected cases excluded. The original runtime, tests and history are maintained separately; these tests are not included here and their count is not this repository's CI suite size.

The exclusions and replacement coverage were:

- Thirty failure-injection cases patched private globals in the previous parser. Thirty standalone cases cover the same fifteen transaction operations, each with structured and unexpected decoder failures, whole-response preservation, nested context and one transmission.
- Three cases depended on the previous method AST or unsupported private parser/builder helpers. Public method inventory, wire contracts and nested failure tests cover the corresponding behavior.
- Three cases asserted the previous catalog resource version, builder or private cache. Standalone provenance checks cover the newly extracted catalog resource.
- One mypy case hard-coded the previous source path. The strict public typing consumer replaces it.

A test-only adapter in that development checkout pinned the previous private payment-clock fixture to September 2026. No clock adapter is required by this repository's runtime. The previous 148 tracked files were preserved byte-for-byte in the separate development checkout; they were not imported into the new repository history.

## Performance evidence

A historical investigation compared selected source components from pykorail, korail2 and SRT, then profiled the same public mock-search workload before and after optimization. Repeated httpx URL reconstruction and a second generic envelope conversion were identified and reduced. No response, seat availability or transaction outcome cache was introduced.

Three fresh processes per implementation ran in alternating order, with five warmed samples per response size per process:

| Returned trains | Previous local implementation | Current implementation | Elapsed reduction |
| --- | ---: | ---: | ---: |
| 1 | 328.955 µs | 302.313 µs | 8.10% |
| 10 | 628.011 µs | 509.567 µs | 18.86% |
| 50 | 1,875.887 µs | 1,381.437 µs | 26.36% |

Each search reached the mock transport exactly once. Cold endpoints perform their first URL resolution once; these results are not cold-start measurements. A profile of 2,000 warmed searches recorded 4,000 calls to httpx's URL parser before optimization and zero in the measured post-fix window; cookie-related standard-library URL processing still occurs.

The complete samples, selected-source revisions and profile evidence are under `tools/reports/`. Publication normalized host-specific path labels without changing timing samples. This repository includes single-runtime profiling tools; the previous runtime required for the historical two-implementation benchmark is maintained separately. No cross-SDK live-speed ranking is claimed.

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

The artifact checker installs the wheel into a temporary target with pip using `--no-index --no-deps`, then runs Python with `-I -S`. Only the installed artifact and dependency site-packages are supplied; editable startup hooks are disabled. It verifies module origins, namespace identity, version metadata, serialization, message access and a synthetic search. It rejects reference code, captured observations and development comparison tools in the archives, then runs the 220 standalone tests from the extracted source archive.

This is an engineering validation record. It does not certify a strict clean-room development process, extinguishment of attribution duties, vendor-data redistribution rights or permission to access external services.
