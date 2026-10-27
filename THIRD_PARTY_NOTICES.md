# Third-party notices

This record covers bundled third-party data, runtime dependencies and technical references. Attribution is not a blanket redistribution grant. See [the legal notice](https://github.com/sontheo/korail-api_v2/blob/main/docs/LEGAL.md) and [material provenance](https://github.com/sontheo/korail-api_v2/blob/main/docs/PROVENANCE.md) for the distribution boundaries.

## Bundled KORAIL message text

| Field | Recorded value |
| --- | --- |
| Application version label | `7.0.10`, from local artifact context |
| Resource | `assets/error_json.json` |
| SHA-256 of resource | `7b7998f2582217aba20e58a722b3640a6ef3a2751d9816aaf2f78cfc97c74d00` |
| Codes / translations | 12,430 / 19,381 |
| Packaged data | `src/korail_api/resources/messages/messages.json` |
| Packaged provenance | `src/korail_api/resources/messages/message-provenance.json` |
| Rights status | Third-party text; no separate redistribution permission established |

The source artifact's delivery origin was not independently authenticated. The application binary is not distributed. Independent extraction, attribution and recording a hash do not transfer copyright or grant redistribution permission. This project's Apache-2.0 grant does not apply to rights the maintainer does not hold.

## Direct runtime dependencies

These packages are installed separately, not vendored into this project's wheel or source archive. The following entries describe the reviewed direct versions, not all future resolutions or their transitive/native components.

| Dependency | Reviewed version | Declared license | Authoritative license |
| --- | --- | --- | --- |
| httpx | 0.28.1 | BSD-3-Clause | [httpx LICENSE.md](https://github.com/encode/httpx/blob/0.28.1/LICENSE.md) |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | [cryptography LICENSE](https://github.com/pyca/cryptography/blob/50.0.2/LICENSE) |
| curl_cffi | 0.16.3 | MIT | [curl_cffi LICENSE](https://github.com/lexiforest/curl_cffi/blob/v0.16.3/LICENSE) |

Retain their applicable license and notice files when redistributing them. Dependencies can include additional transitive or native components with separate terms. In particular, binary distributions of curl_cffi and cryptography may carry additional notices; inspect the actual distributions you redistribute. Development and documentation tools retain their own licenses.

## Protocol and transport references

The transport profile uses protocol fingerprint parameters. Historical transport references include [bogdanfinn/tls-client](https://github.com/bogdanfinn/tls-client) and the [curl_cffi custom-fingerprint documentation](https://curl-cffi.readthedocs.io/en/latest/impersonate/customize.html). No device identity, registration credential or service authorization is supplied by those parameters.

Selected search/session components from pykorail, korail2 and SRT were inspected for a performance investigation. No implementation from those projects was vendored or installed as a runtime dependency. Their pinned revisions and source links are recorded in `tools/reports/related-projects.md`. Those projects retain their own licenses; consultation is not a license exemption if their code is later incorporated.

KORAIL, KTX and other third-party names and marks remain the property of their respective owners. No endorsement or trademark grant is implied.
