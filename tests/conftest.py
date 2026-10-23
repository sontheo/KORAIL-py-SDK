"""The independent suite cannot contact KORAIL or any other network service."""

import socket

import httpx
import pytest
from curl_cffi.requests import Session


@pytest.fixture(autouse=True)
def isolate_maintenance(monkeypatch):
    from korail_api import maintenance

    monkeypatch.setattr(maintenance, "_DEFAULT_POLICY", maintenance.MaintenancePolicy(jitter=lambda _: 0))


@pytest.fixture(autouse=True)
def deny_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Tests require a synthetic transport")

    monkeypatch.setattr(socket, "getaddrinfo", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
    monkeypatch.setattr(socket.socket, "sendto", denied)
    # curl uses native sockets, so Python's socket patch alone cannot block it.
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", denied)
    monkeypatch.setattr(Session, "request", denied)
