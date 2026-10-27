"""The optional signer sees the exact prepared request and fails closed."""

from hashlib import sha256

import httpx
import pytest

from korail_api import DynapathConfig, KorailConfig, KorailProtocolError
from korail_api.security.signing import PreparedRequestSigner, SigningRegistrationRequired
from korail_api.transport.http import KorailHttpClient

ROUTE = "/classes/com.korail.mobile.seatMovie.ScheduleView"


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_signer_receives_final_url_and_body_as_sent(method):
    signed, received = [], []

    def signer(request):
        signed.append(request)
        return "synthetic-token"

    def handler(request):
        received.append(request)
        return httpx.Response(200, json={"strResult": "SUCC"})

    config = KorailConfig(dynapath=DynapathConfig(enabled=True, token_provider=PreparedRequestSigner(signer)))
    client = KorailHttpClient(config, transport=httpx.MockTransport(handler))
    client.client.params = {"default": "기본"}
    try:
        client.exchange(ROUTE, [("item", "서울"), ("item", "부산")], method=method, query={"q": "a/b"})
    finally:
        client.close()
    assert len(received) == len(signed) == 1
    assert signed[0].method == received[0].method
    assert signed[0].url == str(received[0].url)
    assert signed[0].body_sha256 == sha256(received[0].content).digest()
    assert received[0].headers["x-dynapath-m-token"] == "synthetic-token"
    assert signed[0].url not in repr(signed[0])
    assert signed[0].body_sha256.hex() not in repr(signed[0])


@pytest.mark.parametrize(
    ("outcome", "code"),
    [
        (SigningRegistrationRequired("sensitive"), "SIGNER_REGISTRATION_REQUIRED"),
        (TimeoutError("sensitive"), "SIGNER_TIMEOUT"),
        (ConnectionError("sensitive"), "SIGNER_UNAVAILABLE"),
        (ValueError("sensitive"), "SIGNER_FAILED"),
        (None, "SIGNER_INVALID_TOKEN"),
        ("\r\nbad", "SIGNER_INVALID_TOKEN"),
    ],
)
def test_signer_failure_never_sends_or_leaks_exception(outcome, code):
    seen = []

    def signer(_):
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    config = KorailConfig(dynapath=DynapathConfig(enabled=True, token_provider=PreparedRequestSigner(signer)))
    client = KorailHttpClient(config, transport=httpx.MockTransport(lambda request: seen.append(request)))
    try:
        with pytest.raises(KorailProtocolError) as caught:
            client.exchange(ROUTE, {"secret": "synthetic-sensitive"})
        assert caught.value.code == code
        assert "sensitive" not in str(caught.value)
        assert caught.value.__suppress_context__ or caught.value.__context__ is None
        assert seen == []
    finally:
        client.close()


def test_signed_requests_reject_mutating_hooks_before_send():
    received = []
    config = KorailConfig(
        dynapath=DynapathConfig(enabled=True, token_provider=PreparedRequestSigner(lambda _: "token"))
    )
    client = KorailHttpClient(config, transport=httpx.MockTransport(lambda request: received.append(request)))
    client.client.event_hooks["request"].append(lambda request: None)
    try:
        with pytest.raises(KorailProtocolError):
            client.exchange(ROUTE)
        assert received == []
    finally:
        client.close()


def test_registration_transition_requires_caller_action():
    ready = [False]
    signed, sent = [], []

    def signer(request):
        signed.append(request)
        if not ready[0]:
            raise SigningRegistrationRequired()
        return "registered-token"

    def handler(request):
        sent.append(request)
        return httpx.Response(200, json={"strResult": "SUCC"})

    config = KorailConfig(dynapath=DynapathConfig(enabled=True, token_provider=PreparedRequestSigner(signer)))
    client = KorailHttpClient(config, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(KorailProtocolError) as caught:
            client.exchange(ROUTE)
        assert caught.value.code == "SIGNER_REGISTRATION_REQUIRED"
        assert len(signed) == 1 and not sent
        ready[0] = True  # The application, not the SDK, controls registration.
        client.exchange(ROUTE)
        assert len(signed) == 2 and len(sent) == 1
    finally:
        client.close()
