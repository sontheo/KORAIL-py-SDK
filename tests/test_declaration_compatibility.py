"""Recorded token vectors and independently intercepted reservation requests."""

import dataclasses
import json
from hashlib import sha256
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

import korail_api as api
from korail_api.models.records import restore
from korail_api.protocol.forms import build
from korail_api.security import declaration
from korail_api.security.declaration import DeclarationTokenProvider, encode_declaration
from korail_api.security.signing import PreparedRequestSigner

DATA = Path(__file__).parent / "fixtures"
VECTORS = json.loads((DATA / "declaration-vectors.json").read_text())["vectors"]
_REFERENCE = json.loads((DATA / "reservation-compatibility.json").read_text())
RESERVATIONS = [
    {**case, "arguments": {**_REFERENCE["base_arguments"], **case["arguments"]}} for case in _REFERENCE["cases"]
]
CASES = json.loads((DATA / "synthetic-cases.json").read_text())
RESPONSE = CASES["reserve"]["reference"]["exchanges"][1]["response"]


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: f"native-nonce-{v['nonce']}")
def test_recorded_native_declaration_vectors(vector):
    token = encode_declaration(vector["plaintext"].encode(), vector["nonce"])
    assert sha256(token.encode()).hexdigest() == vector["token_sha256"]


def test_declaration_identity_facts_timestamp_and_nonce(monkeypatch):
    observed = []

    def encode(payload, nonce):
        observed.append((payload, nonce))
        return "synthetic-token"

    monkeypatch.setattr(declaration, "encode_declaration", encode)
    nonces = iter([5, 6])
    provider = DeclarationTokenProvider(
        device_id="0123456789abcdef",
        model="MODEL",
        release="14",
        manufacturer="MFR",
        board="BD",
        sdk_int=34,
        timestamp_ms_provider=lambda: 1700000000000,
        nonce_provider=lambda: next(nonces),
    )
    assert provider() == provider() == "synthetic-token"
    payload = observed[0][0].decode()
    assert payload == observed[1][0].decode()
    assert "&iid=MDEyMzQ1Njc4OWFiY2RlZg&" in payload
    assert "&ts=1700000000000&" in payload
    assert "&os=MTQ&dm=TU9ERUw&" in payload
    assert "&mf=TUZS&bd=QkQ&sl=34&sb=0&" in payload
    assert [nonce for _, nonce in observed] == [5, 6]
    assert provider.device_id not in repr(provider)


def test_default_identity_survives_config_replace_and_profile_updates():
    config = api.KorailConfig()
    provider = config.dynapath.token_provider
    assert config.dynapath_mode == "v2-declaration"
    assert isinstance(provider, DeclarationTokenProvider)
    clone = dataclasses.replace(config, timeout=7)
    assert clone.dynapath.token_provider is provider
    assert api.KorailConfig().dynapath.token_provider.device_id != provider.device_id
    profile = api.KorailDeviceProfile("0123456789abcdef", "SM-TEST", "14", "TEST", android_sdk_int=34)
    updated = api.build_config_from_profile(profile, base=config)
    assert updated.dynapath.token_provider.device_id == profile.device_id
    assert updated.dynapath.token_provider.model == profile.model
    assert updated.dynapath.token_provider.sdk_int == 34
    assert dataclasses.replace(config, dynapath_mode="v2-diagnostic").dynapath.token_provider is not provider
    assert dataclasses.replace(config, dynapath_mode="legacy").dynapath.token_settings is not None
    other = dataclasses.replace(profile, model="OTHER-MODEL")
    assert api.build_config_from_profile(other, base=config).dynapath.token_provider.manufacturer == ""


@pytest.mark.parametrize("case", RESERVATIONS, ids=lambda case: case["label"])
def test_default_reservation_matches_independent_pykorail_wire_observations(case):
    seen = []

    def handle(request):
        seen.append(request)
        assert request.method == "GET"
        assert request.url.path.endswith(".TicketReservation")
        assert not request.content
        assert parse_qs(request.url.query.decode(), keep_blank_values=True) == {
            key: [value] for key, value in case["expected_query"].items()
        }
        assert request.headers["x-dynapath-m-token"].startswith("201")
        return httpx.Response(200, json=RESPONSE)

    config = api.KorailConfig(netfunnel_enabled=False, key="SYNTHETIC-APP-KEY")
    arguments = restore(case["arguments"])
    with api.KorailClient(config, transport=httpx.MockTransport(handle)) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION", customer_no="SYNTHETIC-CUSTOMER")
        result = client.reserve(**arguments)
    assert result.pnr_no == "SYNTHETIC-PNR"
    assert len(seen) == 1
    assert build("reserve", config, arguments) == case["expected_query"]


@pytest.mark.parametrize("version", ["250601003", "CUSTOM"])
def test_reservation_does_not_override_explicit_protocol_version(version):
    seen = []

    def handle(request):
        seen.append(request)
        assert parse_qs(request.url.query.decode())["Version"] == [version]
        return httpx.Response(200, json=RESPONSE)

    with api.KorailClient(
        api.KorailConfig(version=version, netfunnel_enabled=False), transport=httpx.MockTransport(handle)
    ) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION")
        client.reserve(**restore(RESERVATIONS[0]["arguments"]))
    assert len(seen) == 1


@pytest.mark.parametrize("prepared", [False, True])
def test_custom_reservation_signers_keep_post_and_final_request_identity(prepared):
    signed, seen = [], []

    def sign(request):
        signed.append(request)
        return "synthetic-token"

    provider = PreparedRequestSigner(sign) if prepared else sign
    config = api.KorailConfig(
        netfunnel_enabled=False, dynapath=api.DynapathConfig(enabled=True, token_provider=provider)
    )

    def handle(request):
        seen.append(request)
        assert request.method == "POST"
        assert parse_qs(request.content.decode())["Version"] == ["250601003"]
        if prepared:
            assert signed[0].method == request.method
            assert signed[0].url == str(request.url)
            assert signed[0].body_sha256 == sha256(request.content).digest()
        return httpx.Response(200, json=RESPONSE)

    with api.KorailClient(config, transport=httpx.MockTransport(handle)) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION")
        client.reserve(**restore(RESERVATIONS[0]["arguments"]))
    assert len(seen) == len(signed) == 1


@pytest.mark.parametrize("status", [200, 403])
@pytest.mark.parametrize("code", [-8005, "-8005"])
def test_reservation_rejection_preserves_response_without_post_replay(status, code):
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(status, json={"code": code})

    with api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False), transport=httpx.MockTransport(handle)
    ) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION")
        with pytest.raises(api.KorailDynaPathError) as error:
            client.reserve(**restore(RESERVATIONS[0]["arguments"]))
    assert len(seen) == 1 and seen[0].method == "GET"
    assert error.value.code == "-8005"
    assert error.value.status_code == status
    assert error.value.raw == {"code": code}


def test_declaration_failure_prevents_transmission():
    seen = []

    def unavailable():
        raise RuntimeError("synthetic clock failure")

    provider = DeclarationTokenProvider(timestamp_ms_provider=unavailable)
    config = api.KorailConfig(
        netfunnel_enabled=False, dynapath=api.DynapathConfig(enabled=True, token_provider=provider)
    )
    with api.KorailClient(
        config, transport=httpx.MockTransport(lambda request: seen.append(request))
    ) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION")
        with pytest.raises(api.KorailProtocolError, match="token provider failed"):
            client.reserve(**restore(RESERVATIONS[0]["arguments"]))
    assert not seen


@pytest.mark.parametrize(
    "options",
    [
        {"disable_dynapath": True},
        {"dynapath": api.DynapathConfig(allowlist_paths=frozenset())},
        {"dynapath_mode": "v2-diagnostic"},
        {"dynapath_mode": "legacy"},
    ],
)
def test_explicit_non_declaration_paths_keep_original_reservation(options):
    seen = []

    def handle(request):
        seen.append(request)
        assert request.method == "POST"
        assert parse_qs(request.content.decode())["Version"] == ["250601003"]
        return httpx.Response(200, json=RESPONSE)

    with api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False, **options), transport=httpx.MockTransport(handle)
    ) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION")
        client.reserve(**restore(RESERVATIONS[0]["arguments"]))
    assert len(seen) == 1


def test_ambiguous_reservation_transport_failure_is_never_replayed():
    seen = []

    def handle(request):
        seen.append(request)
        raise httpx.ReadTimeout("synthetic response timeout", request=request)

    with api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False), transport=httpx.MockTransport(handle)
    ) as client:
        client.session.current = api.KorailSession("SYNTHETIC-SESSION")
        with pytest.raises(api.KorailTransportError, match="outcome may be unknown"):
            client.reserve(**restore(RESERVATIONS[0]["arguments"]))
    assert len(seen) == 1 and seen[0].method == "GET"


@pytest.mark.parametrize("nonce", [-1, 2**32, True, "5"])
def test_invalid_nonce_is_rejected_before_token_generation(nonce):
    with pytest.raises(ValueError, match="nonce"):
        encode_declaration(b"!v=2&es=288904575606514493", nonce)
