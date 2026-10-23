"""httpx transport boundary with one cookie owner and decoded-body adaptation."""

import os
import re
from urllib.parse import urlsplit

import httpx

from korail_api.protocol.schema import load

_fingerprint = load("fingerprint")
OKHTTP4_JA3 = _fingerprint["OKHTTP4_JA3"]
OKHTTP4_AKAMAI = _fingerprint["OKHTTP4_AKAMAI"]
OKHTTP4_EXTRA_FP = _fingerprint["OKHTTP4_EXTRA_FP"]
_HTTPX_VERSION = tuple(int(part) for part in httpx.__version__.split(".")[:2])


def validate_proxy(proxy):
    if proxy is None:
        return
    try:
        if not isinstance(proxy, str) or not proxy or re.search(r"\s", proxy):
            raise ValueError
        parsed = urlsplit(proxy)
        if parsed.scheme not in {"http", "https", "socks5", "socks5h"} or not parsed.hostname:
            raise ValueError
        if parsed.port is not None and not 1 <= parsed.port <= 65535:
            raise ValueError
    except ValueError:
        raise ValueError("Invalid proxy URL") from None


def env_proxy_url():
    for key in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
        if os.environ.get(key):
            return os.environ[key]
    return None


class OkHttpTransport(httpx.BaseTransport):
    def __init__(self, proxy=None):
        from curl_cffi import CurlOpt
        from curl_cffi.requests import Session

        self.proxy = proxy
        options = dict(
            ja3=OKHTTP4_JA3,
            akamai=OKHTTP4_AKAMAI,
            extra_fp=OKHTTP4_EXTRA_FP,
            discard_cookies=True,
            trust_env=False,
            curl_options={CurlOpt.TLS_STATUS_REQUEST: 1},
        )
        if proxy:
            options["proxies"] = {"http": proxy, "https": proxy}
        self._session = Session(**options)
        self._closed = False

    def handle_request(self, request):
        from curl_cffi.requests import exceptions as ce

        timeout = request.extensions.get("timeout", {}).get("read", 60.0)
        try:
            result = self._session.request(
                method=request.method,
                url=str(request.url),
                headers=[(k.decode("latin1"), v.decode("latin1")) for k, v in request.headers.raw],
                content=request.read(),
                timeout=timeout,
                allow_redirects=False,
            )
        except ce.InvalidURL as error:
            raise httpx.InvalidURL("Invalid transport URL") from error
        except ce.CurlError as error:
            kind = httpx.TransportError
            for curl_type, http_type in (
                (ce.ConnectTimeout, httpx.ConnectTimeout),
                (ce.ReadTimeout, httpx.ReadTimeout),
                (ce.ConnectionError, httpx.ConnectError),
            ):
                if isinstance(error, curl_type):
                    kind = http_type
                    break
            raise kind("Transport request failed", request=request) from error
        # curl has already decompressed content; forwarding its encoding headers
        # would make httpx try to decompress the bytes again.
        raw_headers = getattr(result.headers, "raw", None)
        pairs = raw_headers if raw_headers is not None else list(result.headers.items())
        pairs = [
            (k, v)
            for k, v in pairs
            if (k.decode("latin1") if isinstance(k, bytes) else k).lower()
            not in {"content-encoding", "content-length", "transfer-encoding"}
        ]
        return httpx.Response(result.status_code, headers=pairs, content=result.content, request=request)

    def close(self):
        if not self._closed:
            self._closed = True
            self._session.close()

    def __repr__(self):
        return f"{type(self).__name__}(closed={self._closed})"


def build_okhttp_transport(proxy=None):
    return OkHttpTransport(proxy=proxy)


def build_transport(config, transport):
    if transport is not None and config.proxy is not None:
        raise ValueError("An explicit proxy cannot be combined with a custom transport")
    if transport is not None:
        return transport
    if config.transport_profile == "okhttp":
        return OkHttpTransport(config.proxy if config.proxy is not None else env_proxy_url())
    if config.proxy is not None:
        if config.proxy.startswith("https:") and _HTTPX_VERSION < (0, 25):
            raise ValueError("HTTPS proxy requires httpx 0.25 or later")
        if config.proxy.startswith("socks5h:") and _HTTPX_VERSION < (0, 28):
            raise ValueError("socks5h requires httpx 0.28 or later")
        try:
            return httpx.HTTPTransport(proxy=httpx.Proxy(config.proxy))
        except ImportError:
            raise ImportError("Install korail-api[socks] for SOCKS proxy support") from None
        except (ValueError, httpx.InvalidURL):
            raise ValueError("httpx rejected the proxy URL") from None
    return None
