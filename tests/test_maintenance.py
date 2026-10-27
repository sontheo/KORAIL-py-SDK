"""Real request counts and durable probe exclusion under synthetic failures."""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from threading import Event

import httpx
import pytest

from korail_api import KorailClient, KorailConfig
from korail_api.maintenance import SERVICE_STATUS_PATH, MaintenanceDeferredError, MaintenancePolicy
from korail_api.models import errors as E
from korail_api.transport.admission import Admission
from korail_api.transport.http import KorailHttpClient, parse_base_response

BASE = "https://maintenance.example.invalid"
OK = {"strResult": "SUCC"}


@pytest.fixture
def clock():
    return [1_800_000_000.0]


def policy(clock, **kwargs):
    return MaintenancePolicy(clock=lambda: clock[0], jitter=lambda _: 0, **kwargs)


def http(clock, handle, **kwargs):
    return KorailHttpClient(
        KorailConfig(base_url=BASE, netfunnel_enabled=False),
        transport=httpx.MockTransport(handle),
        maintenance=policy(clock, **kwargs),
    )


@pytest.mark.parametrize("value", [None, "", "UNKNOWN", 1, True, [], {}])
def test_invalid_result_is_not_an_accepted_envelope(value):
    raw = {"strResult": value, "h_msg_cd": "S003"}
    with pytest.raises(E.KorailProtocolError) as caught:
        parse_base_response(raw)
    assert caught.value.raw is raw


@pytest.mark.parametrize("status", [429, 503])
@pytest.mark.parametrize("json_body", [False, True])
def test_retry_after_stops_all_followup_calls(clock, status, json_body):
    requests = []

    def handle(request):
        requests.append(request)
        kwargs = {"json": OK} if json_body else {"text": "maintenance"}
        return httpx.Response(status, headers={"Retry-After": "20000"}, **kwargs)

    client = http(clock, handle)
    try:
        with pytest.raises(E.KorailTransportError) as caught:
            client.post_form("/transaction")
        error = caught.value
        assert error.status_code == status
        assert error.retry_after == 20000
        assert error.next_probe_at == clock[0] + 20000
        for path in ["/transaction", SERVICE_STATUS_PATH] * 10:
            with pytest.raises(MaintenanceDeferredError):
                client.post_form(path)
        assert len(requests) == 1
    finally:
        client.close()


@pytest.mark.parametrize("header", ["invalid", "-1", "1.5", "9" * 400])
def test_invalid_retry_after_uses_policy_default(clock, header):
    client = http(clock, lambda _: httpx.Response(503, headers={"Retry-After": header}))
    try:
        with pytest.raises(E.KorailTransportError) as caught:
            client.get("/read")
        assert caught.value.retry_after is None
        assert caught.value.next_probe_at == clock[0] + 1800
    finally:
        client.close()


def test_http_date_and_business_maintenance_are_preserved(clock):
    retry = format_datetime(datetime.fromtimestamp(clock[0] + 5000, timezone.utc), usegmt=True)
    client = http(
        clock,
        lambda _: httpx.Response(
            200, json={"strResult": "FAIL", "h_msg_cd": "S003"}, headers={"Retry-After": retry}
        ),
    )
    try:
        with pytest.raises(E.KorailServiceUnavailableError) as caught:
            client.post_form("/read", raise_on_fail=False)
        assert caught.value.status_code == 200
        assert caught.value.retry_after == 5000
        assert caught.value.next_probe_at == clock[0] + 5000
    finally:
        client.close()


def test_backoff_only_probes_when_caller_requests_and_then_recovers(clock):
    requests = []
    healthy = [False]

    def handle(request):
        requests.append(request.url.path)
        return httpx.Response(200, json=OK) if healthy[0] else httpx.Response(503)

    client = http(clock, handle)
    try:
        for i, delay in enumerate([1800, 3600, 7200, 14400, 14400]):
            with pytest.raises(E.KorailTransportError) as caught:
                client.get("/read" if i == 0 else SERVICE_STATUS_PATH)
            deadline = caught.value.next_probe_at
            assert deadline == clock[0] + delay
            assert len(requests) == i + 1
            clock[0] = deadline - 1
            with pytest.raises(MaintenanceDeferredError):
                client.get(SERVICE_STATUS_PATH)
            clock[0] = deadline
            with pytest.raises(MaintenanceDeferredError):
                client.post_mutation_form("/transaction")
        healthy[0] = True
        client.get(SERVICE_STATUS_PATH)
        client.post_mutation_form("/transaction")
        assert requests[-2:] == [SERVICE_STATUS_PATH, "/transaction"]
    finally:
        client.close()


@pytest.mark.parametrize("code", ["S000", "S001", "S002", "S003", "SEMGTK", "BT019", "BT023"])
def test_known_unavailability_blocks_without_retry(clock, code):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(200, json={"strResult": "FAIL", "h_msg_cd": code})

    client = http(clock, handle)
    try:
        with pytest.raises(E.KorailApiError):
            client.get("/read")
        with pytest.raises(MaintenanceDeferredError):
            client.get("/read")
        assert len(calls) == 1
    finally:
        client.close()


@pytest.mark.parametrize("code", ["P058", "-8204", "WRC000390", "SUPDATE"])
def test_account_and_version_errors_do_not_open_maintenance(clock, code):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(200, json={"strResult": "FAIL", "h_msg_cd": code})

    client = http(clock, handle)
    try:
        for _ in range(3):
            with pytest.raises(E.KorailApiError) as caught:
                client.get("/read")
            assert not isinstance(caught.value, MaintenanceDeferredError)
        assert len(calls) == 3
    finally:
        client.close()


def test_transport_failure_threshold_and_single_attempt_transactions(clock):
    calls = []

    def handle(request):
        calls.append(request)
        raise httpx.ReadTimeout("synthetic", request=request)

    client = http(clock, handle)
    try:
        for i in range(2):
            with pytest.raises(E.KorailTransportError):
                client.post_mutation_form("/transaction")
            assert len(calls) == i + 1
        with pytest.raises(MaintenanceDeferredError):
            client.post_mutation_form("/transaction")
        assert len(calls) == 2
    finally:
        client.close()


def test_success_resets_consecutive_failure_counter(clock):
    replies = [502, 200, 502, 200]
    client = http(clock, lambda _: httpx.Response(replies.pop(0), json=OK))
    try:
        for _ in range(2):
            with pytest.raises(E.KorailTransportError):
                client.get("/read")
            client.get("/read")
    finally:
        client.close()


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_http_client_errors_do_not_become_outages(clock, status):
    client = http(clock, lambda _: httpx.Response(status, json=OK))
    try:
        for _ in range(3):
            with pytest.raises(E.KorailTransportError):
                client.get("/read")
    finally:
        client.close()


@pytest.mark.parametrize("persistent", [False, True])
def test_only_one_recovery_probe_and_restart_keeps_deadline(clock, tmp_path, persistent):
    kwargs = {"state_path": tmp_path / "maintenance.sqlite3"} if persistent else {}
    first = policy(clock, **kwargs)
    error = E.KorailServiceUnavailableError("S003", "synthetic")
    deadline = first.failure(BASE, error)
    second = policy(clock, **kwargs) if persistent else first
    with pytest.raises(MaintenanceDeferredError) as caught:
        second.check(BASE)
    assert caught.value.next_probe_at == deadline
    # A separate service origin remains usable.
    second.check("https://unrelated.example.invalid")
    clock[0] = deadline
    started, release = Event(), Event()
    seen = []

    def handle(request):
        seen.append(request)
        started.set()
        assert release.wait(5)
        return httpx.Response(200, json=OK)

    config = KorailConfig(base_url=BASE, netfunnel_enabled=False)
    a = KorailHttpClient(config, transport=httpx.MockTransport(handle), maintenance=first)
    b = KorailHttpClient(config, transport=httpx.MockTransport(handle), maintenance=second)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(a.get, SERVICE_STATUS_PATH)
            try:
                assert started.wait(5)
                for _ in range(3):
                    with pytest.raises(MaintenanceDeferredError):
                        b.get(SERVICE_STATUS_PATH)
                assert len(seen) == 1
            finally:
                release.set()
            pending.result(timeout=5)
        second.check(BASE)
    finally:
        release.set()
        a.close()
        b.close()


def test_expired_probe_cannot_clear_a_newer_outage(clock, tmp_path):
    a = policy(clock, state_path=tmp_path / "state.sqlite3", probe_lease=10)
    b = policy(clock, state_path=tmp_path / "state.sqlite3", probe_lease=10)
    clock[0] = a.failure(BASE, E.KorailServiceUnavailableError("S003", "synthetic"))
    with a.request(BASE, probe=True):
        clock[0] += 11
        with pytest.raises(E.KorailProtocolError):
            with b.request(BASE, probe=True):
                raise E.KorailProtocolError("synthetic malformed recovery")
    with pytest.raises(MaintenanceDeferredError):
        a.check(BASE)


def test_login_and_queue_are_blocked_before_any_request(clock):
    p = policy(clock)
    p.failure(BASE, E.KorailServiceUnavailableError("S003", "synthetic"))
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json=OK)

    with KorailClient(KorailConfig(base_url=BASE), transport=httpx.MockTransport(handle), maintenance=p) as c:
        with pytest.raises(MaintenanceDeferredError):
            c.login("1234567890", "SYNTHETIC-PASSWORD")
        with pytest.raises(MaintenanceDeferredError):
            c.netfunnel.run("inquiry", lambda: seen.append("API"))
        with pytest.raises(MaintenanceDeferredError):
            c.get_station_data()
    assert seen == []


def test_queue_never_retries_after_budget_or_bypasses_errors(clock):
    for limit, expected in [(1, 1), (5, 1), (20, 2)]:
        now = [0]
        seen, sleeps, sent = [], [], []

        def fail(request):
            seen.append(now[0])
            raise httpx.ConnectError("synthetic", request=request)

        def sleep(seconds):
            sleeps.append(seconds)
            now[0] += seconds

        q = Admission(
            KorailConfig(base_url=BASE, netfunnel_wait_limit=limit, netfunnel_timeout=5),
            transport=httpx.MockTransport(fail),
            sleeper=sleep,
            clock=lambda: now[0],
            maintenance=policy(clock),
        )
        try:
            with pytest.raises(E.KorailNetFunnelError):
                q.run("inquiry", lambda: sent.append(True))
            assert len(seen) == expected
            assert all(at < limit for at in seen)
            assert len(sleeps) == expected - 1
            assert sent == []
        finally:
            q.close()


def test_queue_503_does_not_retry_and_retains_retry_after(clock):
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(503, headers={"Retry-After": "5000"})

    q = Admission(KorailConfig(base_url=BASE), transport=httpx.MockTransport(handle), maintenance=policy(clock))
    try:
        with pytest.raises(E.KorailNetFunnelError) as caught:
            q.run("inquiry", lambda: pytest.fail("API must not be sent"))
        assert caught.value.status_code == 503
        assert caught.value.retry_after == 5000
        assert len(seen) == 1
    finally:
        q.close()


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 503])
def test_queue_http_rejection_is_not_retried(clock, status):
    seen, slept = [], []

    def handle(request):
        seen.append(request)
        return httpx.Response(status, headers={"Retry-After": "5000"})

    q = Admission(
        KorailConfig(base_url=BASE),
        transport=httpx.MockTransport(handle),
        maintenance=policy(clock),
        sleeper=slept.append,
    )
    try:
        with pytest.raises(E.KorailNetFunnelError) as caught:
            q.run("inquiry", lambda: pytest.fail("API must not be sent"))
        assert caught.value.status_code == status
        assert len(seen) == 1
        assert not slept
        if status in {429, 503}:
            assert caught.value.retry_after == 5000
            assert caught.value.next_probe_at == clock[0] + 5000
    finally:
        q.close()


@pytest.mark.parametrize("fail_first", [False, True])
def test_queue_poll_errors_share_retry_budget_and_release_without_bypass(clock, fail_first):
    replies = iter(["error", "wait", "error"] if fail_first else ["wait", "error", "error"])
    ops, sleeps, sent = [], [], []
    now = [0]

    def handle(request):
        op = request.url.params["opcode"]
        ops.append(op)
        if op == "5004":
            return httpx.Response(200, text="done")
        if next(replies) == "error":
            raise httpx.ConnectError("synthetic", request=request)
        return httpx.Response(200, text="201:key=SYNTHETIC&ttl=1")

    def sleep(seconds):
        sleeps.append(seconds)
        now[0] += seconds

    q = Admission(
        KorailConfig(base_url=BASE),
        transport=httpx.MockTransport(handle),
        sleeper=sleep,
        clock=lambda: now[0],
        maintenance=policy(clock),
    )
    try:
        with pytest.raises(E.KorailNetFunnelError):
            q.run("inquiry", lambda: sent.append(True))
        assert ops == (["5101", "5101", "5002", "5004"] if fail_first else ["5101", "5002", "5002", "5004"])
        assert sleeps == ([3, 1] if fail_first else [1, 3])
        assert sent == []
    finally:
        q.close()


def test_another_process_cannot_take_an_active_persistent_probe(clock, tmp_path):
    path = tmp_path / "maintenance.sqlite3"
    p = policy(clock, state_path=path)
    clock[0] = p.failure(BASE, E.KorailServiceUnavailableError("S003", "synthetic"))
    code = """
import sys
sys.path.insert(0, sys.argv[1])
from korail_api.maintenance import MaintenancePolicy, MaintenanceDeferredError
p = MaintenancePolicy(state_path=sys.argv[2], clock=lambda: float(sys.argv[3]))
try:
    with p.request(sys.argv[4], probe=True):
        raise AssertionError('A second process acquired the same probe')
except MaintenanceDeferredError:
    pass
"""
    with p.request(BASE, probe=True):
        subprocess.run(
            [
                sys.executable,
                "-I",
                "-c",
                code,
                str(Path(__file__).parents[1] / "src"),
                str(path),
                str(clock[0]),
                BASE,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )


def test_invalid_probe_does_not_reopen_service_even_when_flags_disable_validation(clock):
    client = http(clock, lambda _: httpx.Response(200, json={"strResult": "FAIL", "h_msg_cd": "OTHER"}))
    try:
        clock[0] = client.maintenance.failure(BASE, E.KorailServiceUnavailableError("S003", "synthetic"))
        with pytest.raises(E.KorailAppError):
            client.post_form(SERVICE_STATUS_PATH, require_envelope=False, raise_on_fail=False)
        with pytest.raises(MaintenanceDeferredError):
            client.get("/read")
    finally:
        client.close()


def test_default_queue_wait_has_a_finite_bound():
    assert KorailConfig().netfunnel_wait_limit == 300


def test_default_queue_budget_stops_an_endlessly_waiting_queue(clock):
    now = [0]
    polls = []
    released = []

    def handle(request):
        if request.url.params["opcode"] == "5004":
            released.append(True)
            return httpx.Response(200, text="done")
        polls.append(now[0])
        return httpx.Response(200, text="201:key=SYNTHETIC&ttl=30")

    def sleep(seconds):
        now[0] += seconds

    q = Admission(
        KorailConfig(base_url=BASE),
        transport=httpx.MockTransport(handle),
        sleeper=sleep,
        clock=lambda: now[0],
        maintenance=policy(clock),
    )
    try:
        with pytest.raises(E.KorailNetFunnelError):
            q.run("inquiry", lambda: pytest.fail("A waiting queue cannot send the API request"))
        assert polls == list(range(0, 301, 30))
        assert released == [True]
    finally:
        q.close()


@pytest.mark.parametrize("value", [None, "", "UNKNOWN"])
def test_invalid_first_cancellation_stage_never_sends_second_stage(clock, value):
    import json

    from korail_api.models.records import restore

    cases = json.loads((Path(__file__).parent / "fixtures/synthetic-cases.json").read_text())
    case = cases["cancel_unpaid_hold"]
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json={"strResult": value})

    config = KorailConfig(base_url=BASE, netfunnel_enabled=False)
    with KorailClient(config, transport=httpx.MockTransport(handle), maintenance=policy(clock)) as c:
        from korail_api import KorailSession

        c.session.current = KorailSession("SYNTHETIC-SESSION", customer_no="SYNTHETIC-CUSTOMER")
        with pytest.raises(E.KorailProtocolError):
            c.cancel_unpaid_hold(**restore(case["arguments"]))
    assert len(seen) == 1


def test_bookkeeping_failure_preserves_committed_response(clock, monkeypatch):
    import sqlite3

    raw = {"strResult": "SUCC", "h_pnr_no": "SYNTHETIC-COMMITTED"}
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json=raw)

    client = http(clock, handle)

    def broken(*args, **kwargs):
        raise sqlite3.OperationalError("synthetic disk failure")

    monkeypatch.setattr(client.maintenance, "success", broken)
    try:
        with pytest.raises(E.KorailProtocolError) as caught:
            client.post_mutation_form("/transaction")
        assert caught.value.raw == raw
        assert len(seen) == 1
    finally:
        client.close()


def test_bookkeeping_failure_does_not_mask_original_http_failure(clock, monkeypatch):
    import sqlite3

    client = http(clock, lambda _: httpx.Response(503, json={"synthetic": True}))

    def broken(*args, **kwargs):
        raise sqlite3.OperationalError("synthetic disk failure")

    monkeypatch.setattr(client.maintenance, "failure", broken)
    try:
        with pytest.raises(E.KorailTransportError) as caught:
            client.get("/read")
        assert caught.value.status_code == 503
        assert caught.value.raw == {"synthetic": True}
        assert caught.value.__notes__ == ["Maintenance bookkeeping failed (OperationalError)"]
    finally:
        client.close()
