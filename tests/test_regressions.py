"""Failure guarantees of the independent engines, without legacy private hooks."""

import dataclasses
import json
import pickle
from pathlib import Path

import httpx
import pytest

import korail_api as api
import korail_api.protocol.codec as codec
from korail_api.api.client import KorailClient
from korail_api.models.records import REGISTRY, restore
from korail_api.protocol.schema import load
from korail_api.transport.http import KorailHttpClient

CASES = json.loads((Path(__file__).parent / "fixtures/synthetic-cases.json").read_text())
TRANSACTIONS = [
    "reserve",
    "reserve_transfer",
    "reserve_merge",
    "reserve_with_discount_card",
    "cancel_product_reservation",
    "pay_with_card",
    "refund",
    "verify_station_ticket_refund",
    "execute_station_ticket_refund",
    "add_to_cart",
    "register_discount_card",
    "recalculate_price",
    "register_self_checkin",
    "cancel_self_checkin",
    "retrieve_delivered_ticket",
]


@pytest.mark.parametrize("operation", TRANSACTIONS)
@pytest.mark.parametrize("unexpected", [False, True])
def test_decoder_failure_preserves_committed_response_and_sends_once(monkeypatch, unexpected, operation):
    raw = {"strResult": "SUCC", "h_pnr_no": "SYNTHETIC-COMMITTED-PNR", "nested": {"synthetic": True}}
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json=raw)

    def broken(name, payload):
        if name != CASES[operation]["reference"]["return_type"]:
            return original(name, payload)
        if unexpected:
            raise ValueError("synthetic decoder failure")
        error = api.KorailProtocolError("synthetic invalid nested value")
        error.raw = payload["nested"]
        raise error

    original = codec._decode
    monkeypatch.setattr(codec, "_decode", broken)
    config = api.KorailConfig(netfunnel_enabled=False)
    with KorailClient(config, transport=httpx.MockTransport(handle)) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION", customer_no="SYNTHETIC-CUSTOMER")
        with pytest.raises(api.KorailProtocolError) as caught:
            getattr(client, operation)(**restore(CASES[operation]["arguments"]))
    assert len(seen) == 1
    assert caught.value.raw == raw
    if not unexpected:
        assert caught.value.parser_raw == raw["nested"]


@pytest.mark.parametrize("code", ["-8204", "-8202"])
def test_business_rejection_and_access_rejection_stay_distinct(code):
    route = "/classes/com.korail.mobile.certification.TicketReservation"
    # Observed numeric access status and a commonOut business error use different shapes.
    raw = (
        {"strResult": "FAIL", "h_msg_cd": code, "h_msg_txt": "synthetic"}
        if code == "-8204"
        else {"code": -8202}
    )
    kind = api.KorailAppError if code == "-8204" else api.KorailDynaPathError
    http = KorailHttpClient(
        api.KorailConfig(), transport=httpx.MockTransport(lambda r: httpx.Response(200, json=raw))
    )
    try:
        with pytest.raises(kind) as caught:
            http.exchange(route)
    finally:
        http.close()
    assert caught.value.raw == raw


def test_exception_pickle_and_sensitive_model_representation():
    error = api.KorailProtocolError("synthetic")
    error.raw = {"pnr": "SYNTHETIC-PNR"}
    error.parser_raw = {"row": True}
    restored = pickle.loads(pickle.dumps(error))
    assert (restored.raw, restored.parser_raw) == (error.raw, error.parser_raw)
    card = api.CardPayment("SYNTHETIC-PAN", "SYNTHETIC-PASSWORD", "9912", "SYNTHETIC-BIRTHDAY")
    assert "SYNTHETIC" not in repr(card)


def test_model_and_method_surface_matches_packaged_contract():
    for name in load("public-interface")["exports"]:
        assert getattr(api, name) is not None
    for name, model in REGISTRY.items():
        if dataclasses.is_dataclass(model):
            assert len(dataclasses.fields(model)) == len(load("public-interface")["models"][name]["fields"])
    assert len(load("public-interface")["client"]) == 86


def test_message_catalog_records_vendor_origin():
    provenance = load("message-provenance")
    assert provenance["app_version"] == "7.0.10"
    assert provenance["code_count"] == len(load("messages")) == 12430
    assert len(provenance["sha256"]) == 64
    assert "not maintainer-authored" in provenance["origin"]


def test_successive_searches_do_not_reuse_previous_request_values():
    from urllib.parse import parse_qs

    observed = []
    response = next(
        row["response"]
        for row in CASES["search_trains"]["reference"]["exchanges"]
        if row["host"] == "api.example.invalid"
    )

    def handle(request):
        observed.append(parse_qs(request.content.decode()))
        return httpx.Response(200, json=response)

    first = api.TrainSearchQuery("SYNTHETIC-A", "SYNTHETIC-B", "20991230", "090000")
    second = dataclasses.replace(
        first, departure_station_code="SYNTHETIC-C", departure_time="100000", passengers=2
    )
    with api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False), transport=httpx.MockTransport(handle)
    ) as client:
        client.search_trains(first)
        client.search_trains(second)
        client.search_trains(first)
    assert observed[0] == observed[2]
    assert observed[1]["txtGoStart"] == ["SYNTHETIC-C"]
    assert observed[1]["txtGoHour"] == ["100000"]
    assert observed[1]["txtPsgFlg_1"] == ["2"]
    assert observed[0]["txtPsgFlg_1"] == ["1"]


@pytest.mark.parametrize(
    ("options", "special", "version", "token"),
    [
        ({}, False, "250722001", "201"),
        ({"version": "250601003"}, False, "250601003", "201"),
        ({"version": "CUSTOM"}, False, "CUSTOM", "201"),
        ({"disable_dynapath": True}, False, "250601003", None),
        ({"dynapath": api.DynapathConfig(allowlist_paths=())}, False, "250601003", None),
        ({}, True, "250601003", "diagnostic"),
        (
            {"dynapath": api.DynapathConfig(enabled=True, token_provider=lambda _: "CUSTOM-TOKEN")},
            False,
            "250601003",
            "CUSTOM-TOKEN",
        ),
    ],
)
def test_schedule_compatibility_preserves_explicit_configuration(options, special, version, token):
    from urllib.parse import parse_qs

    seen = []
    response = next(
        row["response"]
        for row in CASES["search_trains"]["reference"]["exchanges"]
        if row["host"] == "api.example.invalid"
    )

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json=response)

    with api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False, **options), transport=httpx.MockTransport(handle)
    ) as client:
        client.search_trains(
            api.TrainSearchQuery("서울", "부산", "20991230", "090000"), use_special_schedule=special
        )
    assert parse_qs(seen[0].content.decode())["Version"] == [version]
    actual = seen[0].headers.get("x-dynapath-m-token")
    if token == "diagnostic":
        assert actual.startswith("2!")
    else:
        assert actual == token


def test_schedule_default_version_survives_dataclass_replace():
    original = api.KorailConfig()
    clone = dataclasses.replace(original, netfunnel_enabled=False)
    assert type(original.version) is type(clone.version)
    explicit = dataclasses.replace(original, version="250601003")
    assert type(explicit.version) is str


@pytest.mark.parametrize("code", [-8005, "-8005", -8202, "-8202"])
def test_dynapath_rejection_preserves_code_and_does_not_retry(code):
    seen = []

    def reject(request):
        seen.append(request)
        return httpx.Response(403, json={"code": code})

    with api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False), transport=httpx.MockTransport(reject)
    ) as client:
        with pytest.raises(api.KorailDynaPathError) as caught:
            client.search_trains(api.TrainSearchQuery("서울", "부산", "20991230", "090000"))
    assert len(seen) == 1
    assert caught.value.code == str(code)
    assert caught.value.status_code == 403
    assert caught.value.raw == {"code": code}
