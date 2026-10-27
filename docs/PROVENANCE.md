# Material provenance

## Implementation and protocol data

The code lives in `src/korail_api/`. Its architecture separates schema-directed requests and decoding, generated value objects, session state, queue admission, HTTP transport and token serialization.

Protocol contracts describe public names, signatures, constructor defaults, wire fields, endpoint paths and serialization order. Synthetic input/output fixtures exercise those contracts. Decoder observations under `tools/validation/observations/` are development-only test data, excluded from release artifacts.

## Vendor message data

The vendor error catalog was imported from `assets/error_json.json` in a locally available application artifact identified as version `7.0.10`. Its resource SHA-256 is `7b7998f2582217aba20e58a722b3640a6ef3a2751d9816aaf2f78cfc97c74d00`. The importer records 12,430 codes and 19,381 translations. The version label comes from the local artifact context; the artifact's delivery origin was not independently authenticated. The APK and extracted raw vendor files are not distributed. The catalog text remains third-party material; independent extraction does not make its text maintainer-owned or supply a redistribution license.

`tools/catalog/import_messages.py` can regenerate the catalog from a separately supplied local artifact. It reads a ZIP resource and never executes application code. Secrets and application binaries are not bundled.

## Dependencies and technical references

Runtime dependencies are installed separately and retain their own licenses. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) records the direct dependencies, vendor-data rights and protocol references. The maintainer licenses only material they have authority to license.

Selected search/session components of pykorail, korail2 and SRT were inspected at pinned revisions. The source references are recorded in `tools/reports/related-projects.md`; no implementation from those projects is bundled or required as a runtime dependency.

The ordinary schedule endpoint's `201` compatibility marker and protocol version `250722001` were informed by the documented observations in [devgyurak/pykorail](https://github.com/devgyurak/pykorail) at revision `5e485fd56a2482e741fde14d87dea8f381352f43` and verified independently with an anonymous read-only request. The marker is not a native, device-bound or cryptographic signature; its acceptance can change. This observation was used for the ordinary schedule endpoint only, and no pykorail source code is bundled. The referenced project has its own noncommercial license.
