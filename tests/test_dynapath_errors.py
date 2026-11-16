"""Synthetic access rejections: classify before HTTP/business handling, never replay."""

import pickle

import httpx
import pytest

import korail_api as api
from korail_api.transport.http import KorailHttpClient

SCHEDULE = "/classes/com.korail.mobile.seatMovie.ScheduleView"
RESERVATION = "/classes/com.korail.mobile.certification.TicketReservation"


@pytest.mark.parametrize("status", [200, 403])
@pytest.mark.parametrize("route", [SCHEDULE, RESERVATION, "/synthetic/unlisted"])
@pytest.mark.parametrize("code", [-8004, "-8004", -8202, "-8202"])
@pytest.mark.parametrize("macro", [False, True])
def test_explicit_rejection_preserves_details_and_sends_once(status, route, code, macro):
    raw = {"dynaPathResultCode": code, "requestId": "SYNTHETIC-REQUEST-ID"}
    if macro:
        raw["h_msg_cd"] = "macro_err1"
    seen = []

    def reject(request):
        seen.append(request)
        return httpx.Response(status, json=raw)

    http = KorailHttpClient(api.KorailConfig(), transport=httpx.MockTransport(reject))
    try:
        with pytest.raises(api.KorailDynaPathError) as caught:
            http.exchange(route, raise_on_fail=False, require_envelope=False)
    finally:
        http.close()
    error = caught.value
    assert len(seen) == 1
    assert error.code == str(code)
    assert error.dynapath_code == str(code)
    assert error.h_msg_cd == ("macro_err1" if macro else None)
    assert error.request_id == "SYNTHETIC-REQUEST-ID"
    assert error.status_code == status
    assert error.raw == raw
    assert "SYNTHETIC-REQUEST-ID" not in str(error)
    assert "SYNTHETIC-REQUEST-ID" not in error.display_message
    restored = pickle.loads(pickle.dumps(error))
    assert restored.__dict__ == error.__dict__
    if str(code) == "-8202":
        assert "network access policy" in error.display_message
    else:
        assert "exact cause is unconfirmed" in error.display_message


@pytest.mark.parametrize("status", [200, 403])
@pytest.mark.parametrize(
    "extra, expected",
    [
        ({}, "macro_err1"),
        ({"dynaPathResultCode": "-9999"}, "-9999"),
        ({"dynaPathResultCode": {}}, "macro_err1"),
        ({"dynaPathResultCode": 0}, "macro_err1"),
        ({"dynaPathResultCode": ""}, "macro_err1"),
        ({"code": "-8202"}, "-8202"),
    ],
)
def test_macro_marker_remains_a_rejection_without_a_known_numeric_code(status, extra, expected):
    raw = {"h_msg_cd": "macro_err1", **extra}
    http = KorailHttpClient(
        api.KorailConfig(), transport=httpx.MockTransport(lambda r: httpx.Response(status, json=raw))
    )
    try:
        with pytest.raises(api.KorailDynaPathError) as caught:
            http.exchange(SCHEDULE)
    finally:
        http.close()
    assert caught.value.code == expected
    assert caught.value.request_id is None


def test_explicit_code_takes_priority_over_legacy_code():
    raw = {"dynaPathResultCode": "-8004", "code": "-8202"}
    http = KorailHttpClient(
        api.KorailConfig(), transport=httpx.MockTransport(lambda r: httpx.Response(200, json=raw))
    )
    try:
        with pytest.raises(api.KorailDynaPathError) as caught:
            http.exchange(SCHEDULE)
    finally:
        http.close()
    assert caught.value.code == "-8004"


@pytest.mark.parametrize(
    "extra",
    [
        {"unrelated": "-8004"},
        {"dynaPathResultCode": 0},
        {"dynaPathResultCode": False},
        {"dynaPathResultCode": []},
    ],
)
def test_success_is_not_misclassified_from_unrelated_or_invalid_values(extra):
    raw = {"strResult": "SUCC", **extra}
    http = KorailHttpClient(
        api.KorailConfig(), transport=httpx.MockTransport(lambda r: httpx.Response(200, json=raw))
    )
    try:
        assert http.exchange(SCHEDULE).raw == raw
    finally:
        http.close()
