# Related SDK architecture references

This review inspected the synchronous search/session components listed below at fixed commits. It was an architectural comparison; these libraries were not installed, executed against railway services, vendored, or used as a dependency. No third-party implementation was transplanted. This is not a repository-wide review or a cross-library latency ranking.

| Project and revision | Reviewed components | Relevant observation |
| --- | --- | --- |
| [pykorail — 759afa802f81](https://github.com/devgyurak/pykorail/tree/759afa802f8108b4af5df6d51d18fa9c97ff0f1c) | [synchronous trains](https://github.com/devgyurak/pykorail/blob/759afa802f8108b4af5df6d51d18fa9c97ff0f1c/src/pykorail/_sync/resources/trains.py), [session](https://github.com/devgyurak/pykorail/blob/759afa802f8108b4af5df6d51d18fa9c97ff0f1c/src/pykorail/_sync/session.py), transport interface | Search/page handling leads to typed train conversion. The synchronous session forwards calls to its existing session object. |
| [korail2 — 5a6593f3093e](https://github.com/carpedm20/korail2/tree/5a6593f3093ee15564d217443bd46e40e8217c17) | [search and client](https://github.com/carpedm20/korail2/blob/5a6593f3093ee15564d217443bd46e40e8217c17/korail2/korail2.py) | Search uses a retained session, decodes JSON, checks the result, constructs train objects and filters them in a direct path. Its legacy protocol and model contract differ from this package. |
| [SRT — 3c0c29bd3b74](https://github.com/ryanking13/SRT/tree/3c0c29bd3b747db05f4a14cce77bbfb408fb4318) | [session construction and search](https://github.com/ryanking13/SRT/blob/3c0c29bd3b747db05f4a14cce77bbfb408fb4318/SRT/srt.py) | A retained requests session is used for search, followed by response and train conversion. NetFunnel and recursive search/continuation behavior are part of its separate service contract. |

The useful common design is a retained transport/session and a short search-to-model path. Session reuse was already present in our implementation; the current design uses one retained transport for each client. Different protocol, protection, pagination and response contracts make an SDK-to-SDK network timing comparison inappropriate here.

## Cache behavior

The endpoint cache stores resolved URL objects, not requests or responses. Its 256-entry bound prevents arbitrary route strings from accumulating indefinitely. Resolution uses httpx's public `build_request` behavior once on a cold endpoint. Headers, cookies, tokens, body fields and query arguments are still rebuilt for each exchange. If client-level query defaults are set, the optimization falls back to normal URL resolution. Changing `client.base_url` invalidates that endpoint's cached resolution.

Tests exercise relative and absolute paths, encoded query values, base prefixes and base changes, global query-default changes, successive cookies, per-request tokens and client-header updates. Transport invocation counts remain exactly one per exchange.

## Reproduction

Reviewed project revisions and source links are recorded in `related-projects.json`.

```sh
PYTHONPATH=src .venv/bin/python tools/performance/profile_search.py
```

This command profiles the current implementation with synthetic responses and no live traffic.
