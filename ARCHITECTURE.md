# Source layout

The distribution exposes a single public namespace, `korail_api`. Its modules separate the API, protocol, transport, services and models.

```text
korail-api_v2/
├── src/
│   └── korail_api/
│       ├── api/             # Public client, facade, type attachment
│       ├── configuration/   # Device and environment configuration
│       ├── models/          # Value objects and exception hierarchy
│       ├── services/
│       │   ├── authentication.py
│       │   ├── search.py
│       │   ├── reservations.py
│       │   ├── payments.py
│       │   ├── validation.py
│       │   └── operations.py # Operation orchestration and remaining read rules
│       ├── protocol/        # Request compilation, decoding, adapters, data loading
│       ├── transport/       # HTTP, curl adaptation, admission, cleanup
│       ├── security/        # Password transformation and token serialization
│       ├── messages/        # Locale and display text handling
│       └── resources/
│           ├── contracts/   # Interface and wire contract data
│           └── messages/    # Vendor messages and provenance
├── tests/
│   ├── fixtures/            # Synthetic wire and mutation cases
│   └── *.py                 # Offline behavior and typing checks
├── tools/
│   ├── packaging/           # Isolated wheel and source-archive verification
│   ├── catalog/             # Vendor resource importer; explicit input only
│   ├── validation/          # Captured synthetic decoder comparisons
│   ├── performance/         # Equivalent benchmarks and profiling
│   └── reports/             # Comparison evidence and recorded samples
├── docs/                    # Current documentation site
└── THIRD_PARTY_NOTICES.md    # Bundled data and runtime dependency notices
```

The wheel contains the runtime namespace and release documentation. The source archive also contains the standalone tests, artifact checker and catalog importer. Captured decoder outcomes, validators, performance tools and reports are development-only.

## Where to change behavior

- Authentication and session transitions: `services/authentication.py`.
- Search validation and continuation values: `services/search.py`; client pagination is in `api/client.py`.
- Passenger, journey, designated-seat and limousine reservation rules: `services/reservations.py`.
- Card and settlement validation: `services/payments.py`.
- Remaining account/product query rules and operation orchestration: `services/operations.py`.
- Wire field mappings: `resources/contracts/requests.json`; their compilation and fresh per-call forms: `protocol/requests.py`.
- Response field conversion and raw error context: `protocol/codec.py`.
- HTTP status, cookies, form encoding and protocol rejection: `transport/http.py`.
- Already-decompressed curl responses and proxy handling: `transport/curl.py`.
- Queue admission, budgets and completion: `transport/admission.py`.
- Public constructor fields and signatures: `resources/contracts/public-interface.json`; model construction in `models/records.py`, concrete method annotations in `api/annotations.py`, and declarations in colocated `.pyi` files.

`services/operations.py` and the schema-driven model/decoder engines remain shared components. This reorganization establishes their ownership; it does not claim that every operation has already been converted into a separately authored explicit handler.

## Cache boundaries

Field interpretation plans, immutable date-validation results and resolved endpoint URL objects are cached. Every request receives a fresh form dictionary; client configuration, session values, current timestamps and query arguments are read on each call. Search responses, availability, queue passes and transaction outcomes are never cached by these optimizations. The form-plan cache is bounded to 512 entries the date-validation cache to 1,024 entries, and the per-client endpoint cache to 256 entries. Endpoint resolution is invalidated when the base URL changes and bypassed for client-level query defaults. Cookies, tokens and query/body values remain current on every request.

The offline contract suite remains the compatibility boundary when moving responsibilities into smaller handlers. Run it after changing a request rule, raw-response conversion or gate policy.
