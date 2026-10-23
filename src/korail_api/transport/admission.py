"""Queue admission as an explicit acquire / poll / release state machine."""

from __future__ import annotations

import re
import time
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from urllib.parse import urlencode

import httpx

from korail_api.maintenance import default_policy, http_error_details
from korail_api.models import errors as E
from korail_api.protocol.schema import load
from korail_api.transport.curl import build_transport


@dataclass(frozen=True)
class KorailNetFunnelGate:
    name: str
    action: str
    success_only: bool


@dataclass(frozen=True)
class KorailNetFunnelToken:
    code: str
    key: str = field(default="", repr=False)
    params: dict = field(default_factory=dict, repr=False)
    node: str = ""
    raw: str = field(default="", repr=False)

    @property
    def wait_seconds(self):
        return max(1, min(30, _int32(self.params.get("ttl"))))

    @property
    def wait_count(self):
        return _int32(self.params.get("nwait"))


KORAIL_NETFUNNEL_GATES = {name: KorailNetFunnelGate(**row) for name, row in load("gates").items()}


def korail_netfunnel_node_url(host, port):
    if (
        port == "443"
        and isinstance(host, str)
        and re.fullmatch(r"(?:nf|rnf[1-9][0-9]?)\.letskorail\.com", host)
    ):
        return "https://" + host
    return ""


def _int32(value, fallback=0):
    try:
        if not isinstance(value, str) or not value:
            return fallback
        sign = -1 if value.startswith("-") else 1
        digits = value[1:] if value[:1] in {"+", "-"} else value
        if not digits or any(ord(char) > 65535 for char in digits):
            return fallback
        normalized = "".join(str(unicodedata.decimal(char)) for char in digits).lstrip("0") or "0"
        if len(normalized) > 10:
            return fallback
        parsed = sign * int(normalized)
        return parsed if -(1 << 31) <= parsed < 1 << 31 else fallback
    except (TypeError, ValueError):
        return fallback


def parse_queue(text):
    match = re.search(r"(?:^|['\"])(?:[0-9]+:)?([+-]?\d+):([^'\";]*)", text.strip())
    if match is None:
        raise E.KorailNetFunnelError("QUEUE_FORMAT", "Invalid queue response", raw=text)
    code = _int32(match.group(1), None)
    if code is None:
        raise E.KorailNetFunnelError("QUEUE_FORMAT", "Invalid queue response code", raw=text)
    fields = {}
    for pair in match.group(2).split("&"):
        key, found, val = pair.partition("=")
        if found:
            fields[key] = val
    return code, fields


def parse_netfunnel_body(text):
    code, fields = parse_queue(text)
    return KorailNetFunnelToken(
        str(code),
        fields.get("key", ""),
        fields,
        korail_netfunnel_node_url(fields.get("ip"), fields.get("port")),
        text,
    )


class Admission:
    def __init__(
        self,
        config=None,
        *,
        transport=None,
        sleeper=time.sleep,
        clock=time.monotonic,
        maintenance=None,
    ):
        if config is None:
            from korail_api.models.records import KorailConfig

            config = KorailConfig()
        self.config = config
        self.maintenance = maintenance if maintenance is not None else default_policy()
        self._sleep, self._clock = sleeper, clock
        chosen = build_transport(config, transport)
        options = dict(
            base_url=config.netfunnel_url,
            timeout=config.netfunnel_timeout,
            transport=chosen,
            follow_redirects=False,
        )
        if config.proxy is not None:
            options["trust_env"] = False
            if chosen is None:
                options["proxy"] = config.proxy
        self.client = httpx.Client(**options)
        self._client = self.client
        self.client.headers.clear()
        self._closed = False

    def close(self):
        if not self._closed:
            self._closed = True
            self.client.close()

    def _post(self, url):
        try:
            response = self.client.post(
                url,
                content=b"",
                headers={
                    "User-Agent": self.config.netfunnel_user_agent,
                    "Accept-Encoding": "gzip",
                    "Connection": "Keep-Alive",
                    "Accept-Charset": "UTF-8",
                    "Context_Type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            response.raise_for_status()
            return response.text
        except (httpx.HTTPError, httpx.InvalidURL) as error:
            raised = E.KorailNetFunnelError(None, "Queue exchange failed")
            if isinstance(error, httpx.HTTPStatusError):
                http_error_details(raised, error.response, self.maintenance.clock())
            raise raised from error

    def _request(self, params, base=None):
        url = (base or self.config.netfunnel_url).rstrip("/") + "/ts.wseq?" + urlencode(params)
        return parse_netfunnel_body(self._post(url))

    def _complete(self, token):
        if token is None or not token.key:
            return
        url = (
            (token.node or self.config.netfunnel_url).rstrip("/")
            + "/ts.wseq?"
            + urlencode({"opcode": "5004", "key": token.key})
        )
        try:
            self._post(url)
        except Exception:
            pass

    def get_gate(self, name):
        gate = KORAIL_NETFUNNEL_GATES[name]
        return replace(gate, action=(self.config.netfunnel_actions or {}).get(name, gate.action))

    gate = get_gate

    def run(self, gate, send):
        gate = self.get_gate(gate) if isinstance(gate, str) else gate
        with self.enter(gate.action, success_only=gate.success_only):
            return send()

    @contextmanager
    def enter(self, action, *, success_only=True):
        if self._closed:
            raise E.KorailProtocolError("Queue client is closed")
        self.maintenance.check(self.config.base_url)
        if not self.config.netfunnel_enabled:
            yield
            return
        started = self._clock()
        token = None
        failures = 0
        params = {"opcode": "5101", "sid": "service_1", "aid": action}

        def in_budget(extra=0):
            limit = self.config.netfunnel_wait_limit
            return limit is None or self._clock() - started + extra <= limit

        try:
            while True:
                self.maintenance.check(self.config.base_url)
                limit = self.config.netfunnel_wait_limit
                if limit is not None and self._clock() - started > limit:
                    raise E.KorailNetFunnelError(None, "Queue wait budget exhausted")
                try:
                    next_token = self._request(params, token.node if token else None)
                except E.KorailNetFunnelError as error:
                    failures += 1
                    blocked = self.maintenance.failure(self.config.base_url, error)
                    retry_exhausts_budget = limit is not None and (
                        self._clock() - started + self.config.netfunnel_timeout >= limit
                    )
                    if blocked or failures >= 2 or retry_exhausts_budget:
                        raise
                    self._sleep(self.config.netfunnel_timeout)
                    continue
                token = next_token
                if not in_budget():
                    raise E.KorailNetFunnelError("Queue wait budget exhausted")
                if token.code in {"301", "302"}:
                    raise E.KorailQueueRejectedError(token.code, "Queue rejected admission")
                if token.code not in {"201", "202"}:
                    if token.code != "200" and success_only:
                        raise E.KorailNetFunnelError(token.code, "Queue did not grant admission")
                    break
                if not token.key:
                    raise E.KorailNetFunnelError("Queue wait response has no key")
                if not in_budget(token.wait_seconds):
                    raise E.KorailNetFunnelError("Queue wait budget exhausted")
                self._sleep(token.wait_seconds)
                params = {"opcode": "5002", "key": token.key}
            if not in_budget():
                raise E.KorailNetFunnelError("Queue wait budget exhausted")
            yield
        finally:
            self._complete(token)


KorailNetFunnelClient = Admission
