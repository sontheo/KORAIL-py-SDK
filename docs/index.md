# korail-py-SDK

A synchronous, unofficial Python client for KORAIL. The repository root contains the current implementation and builds the `korail-py-SDK` distribution, version `0.1.0`. The PyPI release is being prepared and is not yet published.

The `korail_py_sdk` namespace exposes the client, models and exceptions. The offline contract includes 239 root exports and 86 public client methods, covering authentication, train search, reservations, payments, refunds, account reads and product operations.

Start with [installation and usage](getting-started.md), then see the [source layout](ARCHITECTURE.md) and [validation guide](VALIDATION.md).

The current implementation preserves transaction failure context, avoids automatic transaction retries and distinguishes business rejection, invalid responses and session errors. Automated checks use synthetic data and block network access; offline validation does not establish live-service acceptance.

Read the [legal notice](LEGAL.md), [third-party notices](THIRD_PARTY_NOTICES.md) and [provenance](PROVENANCE.md) for authorship, vendor-data rights and licensing boundaries. This project is not affiliated with or endorsed by KORAIL.
