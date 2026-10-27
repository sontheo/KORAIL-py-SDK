"""Endpoint reuse must preserve httpx URL semantics and live request state."""

from urllib.parse import parse_qs

import httpx
import pytest

from korail_api import DynapathConfig, KorailConfig
from korail_api.transport.http import KorailHttpClient


@pytest.mark.parametrize("base", ["https://api.example.invalid", "https://api.example.invalid/mobile/"])
@pytest.mark.parametrize(
    "route", ["/search?value=a%2Fb", "search?value=열차", "https://other.example.invalid/search?q=one"]
)
def test_endpoint_reuse_preserves_prefix_query_and_parameter_changes(base, route):
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json={"strResult": "SUCC"})

    http = KorailHttpClient(KorailConfig(base_url=base), transport=httpx.MockTransport(handle))
    try:
        for index, defaults in enumerate(({}, {"global": "ONE"}, {"other": "TWO"}, {}, {})):
            if index == 4:
                http.client.base_url = "https://changed.example.invalid/new-base/"
            http.client.params = defaults
            query = {"current": str(index)}
            expected = http.client.build_request("POST", route, params=query).url
            http.exchange(route, {"body": str(index)}, include_common=False, query=query)
            assert seen[-1].url == expected
            assert parse_qs(seen[-1].content.decode()) == {"body": [str(index)]}
        assert len(seen) == 5
    finally:
        http.close()


def test_repeated_search_updates_tokens_cookies_and_client_headers():
    seen = []
    tokens = []

    def provider(context):
        token = "SYNTHETIC-TOKEN-" + str(len(tokens) + 1)
        tokens.append(token)
        return token

    def handle(request):
        seen.append(request)
        return httpx.Response(
            200,
            json={"strResult": "SUCC"},
            headers={"Set-Cookie": f"JSESSIONID=SYNTHETIC-SESSION-{len(seen)}; Path=/"},
        )

    config = KorailConfig(
        base_url="https://api.example.invalid", dynapath=DynapathConfig(enabled=True, token_provider=provider)
    )
    http = KorailHttpClient(config, transport=httpx.MockTransport(handle))
    try:
        for index in range(3):
            http.client.headers["X-Synthetic-Trace"] = str(index)
            http.exchange("/classes/com.korail.mobile.seatMovie.ScheduleView", {"query": str(index)})
        assert len(seen) == len(tokens) == 3
        assert [r.headers[config.dynapath.header_name] for r in seen] == tokens
        assert [r.headers["X-Synthetic-Trace"] for r in seen] == ["0", "1", "2"]
        assert [r.headers.get("cookie", "") for r in seen] == [
            "",
            "JSESSIONID=SYNTHETIC-SESSION-1",
            "JSESSIONID=SYNTHETIC-SESSION-2",
        ]
    finally:
        http.close()


def test_token_provider_receives_actual_wire_version():
    observed = []

    def provider(context):
        observed.append(context.version)
        return "synthetic"

    config = KorailConfig(dynapath=DynapathConfig(enabled=True, token_provider=provider))
    http = KorailHttpClient(
        config, transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"strResult": "SUCC"}))
    )
    try:
        http.exchange(
            "/classes/com.korail.mobile.seatMovie.ScheduleView",
            {"Version": "wire-version"},
            include_common=False,
        )
        assert observed == ["wire-version"]
    finally:
        http.close()
