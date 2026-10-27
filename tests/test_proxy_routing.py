"""Proxy routing is decided per destination without leaking credentials."""

import httpx

from korail_api import KorailConfig
from korail_api.transport.curl import build_transport


def test_environment_proxy_bypass_and_explicit_proxy_precedence(monkeypatch):
    for name in (
        "HTTP_PROXY",
        "http_proxy",
        "HTTPS_PROXY",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ALL_PROXY", "socks5h://proxy.example.invalid:1055")
    monkeypatch.setenv("NO_PROXY", ".example.invalid")
    sessions = []

    class Session:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.requests = []
            sessions.append(self)

        def request(self, **kwargs):
            self.requests.append(kwargs)
            return httpx.Response(200, content=b"ok")

        def close(self):
            pass

    monkeypatch.setattr("curl_cffi.requests.Session", Session)
    automatic = build_transport(KorailConfig(), None)
    explicit = build_transport(KorailConfig(proxy="socks5h://explicit.example.invalid:1055"), None)
    try:
        automatic.handle_request(httpx.Request("POST", "https://api.example.invalid/read"))
        automatic.handle_request(httpx.Request("POST", "https://smart.letskorail.com/read"))
        explicit.handle_request(httpx.Request("POST", "https://api.example.invalid/read"))
        assert "proxy" not in sessions[0].requests[0]
        assert sessions[0].requests[1]["proxy"] == "socks5h://proxy.example.invalid:1055"
        assert sessions[1].options["proxies"]["https"] == "socks5h://explicit.example.invalid:1055"
        assert "proxy" not in sessions[1].requests[0]
    finally:
        automatic.close()
        explicit.close()
