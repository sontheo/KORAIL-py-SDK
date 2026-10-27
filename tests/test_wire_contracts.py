"""Public operations compared with protocol facts observed outside this implementation."""

import inspect
import json
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

import korail_api as api
from korail_api.models.records import restore

CASES = json.loads((Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic-cases.json").read_text())


@pytest.mark.parametrize("operation", sorted(CASES))
def test_request_and_result_contract(operation):
    case = CASES[operation]
    exchanges = case["reference"]["exchanges"]
    observed = []

    def handle(request):
        expected = exchanges[len(observed)]
        observed.append(request)
        assert request.method == expected["method"]
        assert request.url.path == expected["path"]
        assert request.url.host == expected["host"]
        for actual, wanted in [
            (parse_qs(request.url.query.decode(), keep_blank_values=True), expected["query"]),
            (parse_qs(request.content.decode(), keep_blank_values=True), expected["form"]),
        ]:
            assert actual.keys() == wanted.keys()
            for field, values in wanted.items():
                if (
                    operation
                    in {"search_trains", "search_transfer_trains", "search_trains_with_transfer_fallback"}
                    and request.url.path.endswith(".ScheduleView")
                    and field == "Version"
                ):
                    values = ["250722001"]
                if values == ["<DYNAMIC>"]:
                    assert len(actual[field]) == 1 and actual[field][0].isdigit()
                else:
                    assert actual[field] == values, field
        raw = expected["response"]
        if isinstance(raw, str):
            return httpx.Response(200, text=raw)
        return httpx.Response(200, json=raw, headers={"Set-Cookie": "JSESSIONID=SYNTHETIC-SESSION; Path=/"})

    config = api.KorailConfig(
        base_url="https://api.example.invalid",
        netfunnel_url="https://queue.example.invalid",
        key="SYNTHETIC-APP-KEY",
    )
    with api.KorailClient(config, transport=httpx.MockTransport(handle)) as client:
        if operation != "login":
            client.session.current = api.KorailSession(
                "SYNTHETIC-SESSION", "SYNTHETIC-MEMBER", {}, "SYNTHETIC-MEMBER-CARD", "SYNTHETIC-CUSTOMER"
            )
            client.http.cookies.set("JSESSIONID", "SYNTHETIC-SESSION")
        result = getattr(client, operation)(**restore(case["arguments"]))
        assert type(result).__name__ == case["reference"]["return_type"]
        assert len(observed) == len(exchanges)
        if hasattr(result, "raw") and exchanges:
            assert (
                result.raw == [row for row in exchanges if row["host"] == "api.example.invalid"][-1]["response"]
            )


def test_full_import_and_method_surface():
    assert all(hasattr(api, name) for name in api.__all__)
    methods = {
        name
        for name, function in inspect.getmembers(api.KorailClient, inspect.isfunction)
        if not name.startswith("_")
    }
    assert methods == set(CASES) | {"search_trains_all"}
