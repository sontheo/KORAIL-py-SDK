"""Single-attempt HTTP exchange and response-envelope validation."""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from urllib.parse import urlencode

import httpx

from korail_api.maintenance import SERVICE_STATUS_PATH, default_policy, http_error_details
from korail_api.models import errors as E
from korail_api.protocol.envelope import decode_envelope
from korail_api.protocol.schema import load
from korail_api.transport.curl import build_transport


def parse_base_response(
    raw, *, raise_on_fail=True, require_envelope=True, require_result=None, common_out=None
):
    if require_result is not None:
        require_envelope = require_result
    response = decode_envelope(raw)
    if "strResult" in raw and response.str_result not in {"SUCC", "FAIL"}:
        error = E.KorailProtocolError("Invalid strResult in response envelope")
        error.raw = raw
        raise error
    failed = response.str_result == "FAIL" or (require_envelope and "strResult" not in raw)
    common_failed = response.str_result == "FAIL" or "strResult" not in raw
    if (
        common_failed
        and (common_out if common_out is not None else require_envelope)
        and response.h_msg_cd == "P058"
    ):
        raise E.KorailSessionExpiredError(response.h_msg_cd, response.h_msg_txt, raw=raw)
    if failed and raise_on_fail:
        raise E.classify_app_error(response.h_msg_cd, response.h_msg_txt, raw=raw)
    return response


class KorailHttpClient:
    def __init__(self, config=None, *, transport=None, maintenance=None):
        from korail_api.models.records import KorailConfig

        self.config = config or KorailConfig()
        self.maintenance = maintenance if maintenance is not None else default_policy()
        chosen = build_transport(self.config, transport)
        options = {
            "base_url": self.config.base_url,
            "timeout": self.config.timeout,
            "follow_redirects": False,
            "transport": chosen,
        }
        if self.config.proxy is not None:
            options["trust_env"] = False
            if chosen is None:
                options["proxy"] = self.config.proxy
        self.client = httpx.Client(**options)
        self._client = self.client
        self.client.headers.clear()
        self.cookies = self.client.cookies
        self._closed = False
        self._endpoint_urls = {}
        self._dynapath_generator = None
        if self.config.dynapath.token_settings is not None:
            from korail_api.security.legacy import DynapathTokenGenerator

            self._dynapath_generator = DynapathTokenGenerator(
                self.config.dynapath.token_settings,
                timestamp_ms_provider=self.config.dynapath.timestamp_ms_provider,
                random_text_provider=self.config.dynapath.random_text_provider,
            )

    def close(self):
        if not self._closed:
            self._closed = True
            self.client.close()

    def common_fields(self):
        c = self.config
        fields = {"Device": c.device, "Version": c.version}
        if c.app_version is not None:
            fields["AppVersion"] = c.app_version
        fields["Key"] = c.key
        if c.lang is not None:
            fields["lang"] = c.lang
        return fields

    def _headers(self, route, include_dynapath, method="POST", *, version=None, request=None):
        c = self.config
        headers = {"User-Agent": c.user_agent, "Accept-Encoding": "gzip", "Connection": "Keep-Alive"}
        paths = c.dynapath.allowlist_paths
        if route in paths or include_dynapath:
            if c.disable_dynapath and route.endswith("login.Login"):
                raise E.KorailDynaPathRequiredError("Login needs a configured protocol token")
            provider = c.dynapath.token_provider or self._dynapath_generator
            if c.dynapath.enabled and provider is not None:
                from korail_api.security.signing import PreparedRequestSigner, SigningRequest

                if isinstance(provider, PreparedRequestSigner):
                    if request is None:
                        raise E.KorailProtocolError("Request must be prepared before signing")
                    if self.client.event_hooks.get("request") or self.client.auth is not None:
                        raise E.KorailProtocolError(
                            "Request hooks and client authentication cannot modify signed requests"
                        )
                    signed = SigningRequest(
                        request.method, request.url.path, str(request.url), sha256(request.content).digest()
                    )
                    headers[c.dynapath.header_name] = provider.sign(signed)
                    if self.client.event_hooks.get("request") or self.client.auth is not None:
                        raise E.KorailProtocolError(
                            "Request hooks and client authentication cannot modify signed requests"
                        )
                    return headers
                from korail_api.models.records import DynapathRequestContext

                context = DynapathRequestContext(
                    method=method,
                    path=route,
                    url=c.base_url.rstrip("/") + route,
                    device=c.device,
                    version=c.version if version is None else version,
                    key=c.key,
                    user_agent=c.user_agent,
                    device_name=c.dynapath.device_name,
                    os_version=c.dynapath.os_version,
                )
                try:
                    token = provider(context)
                except Exception as error:
                    raise E.KorailProtocolError("Protocol token provider failed") from error
                if token is not None:
                    headers[c.dynapath.header_name] = token
        return headers

    def exchange(
        self,
        route,
        fields=None,
        *,
        method="POST",
        include_common=True,
        include_dynapath=False,
        require_envelope=True,
        raise_on_fail=True,
        omit_empty_fields=True,
        query=None,
        content_type="application/x-www-form-urlencoded",
    ):
        if self._closed:
            raise E.KorailProtocolError("Client is closed")
        if route == SERVICE_STATUS_PATH:
            # Only an explicitly successful status response can recover service.
            require_envelope = raise_on_fail = True
        result = None
        try:
            with self.maintenance.request(self.config.base_url, probe=route == SERVICE_STATUS_PATH):
                result = self._exchange(
                    route,
                    fields,
                    method=method,
                    include_common=include_common,
                    include_dynapath=include_dynapath,
                    require_envelope=require_envelope,
                    raise_on_fail=raise_on_fail,
                    omit_empty_fields=omit_empty_fields,
                    query=query,
                    content_type=content_type,
                )
        except Exception as error:
            if result is not None:
                raised = E.KorailProtocolError(
                    "Maintenance state update failed after a response; verify its outcome before retrying"
                )
                raised.raw = result.raw
                raise raised from error
            raise
        return result

    def _exchange(
        self,
        route,
        fields=None,
        *,
        method="POST",
        include_common=True,
        include_dynapath=False,
        require_envelope=True,
        raise_on_fail=True,
        omit_empty_fields=True,
        query=None,
        content_type="application/x-www-form-urlencoded",
    ):
        if self._closed:
            raise E.KorailProtocolError("Client is closed")
        pairs = list(self.common_fields().items()) if include_common else []
        if fields:
            pairs.extend(fields.items() if isinstance(fields, Mapping) else fields)
        flat = []
        for key, values in pairs:
            for item in values if isinstance(values, (list, tuple)) else [values]:
                if omit_empty_fields and item in (None, ""):
                    continue
                flat.append(
                    (key, "" if item is None else str(item).lower() if isinstance(item, bool) else str(item))
                )
        wire_version = next((value for key, value in reversed(flat) if key == "Version"), None)
        headers = {}
        if content_type is not None:
            headers["Content-Type"] = content_type
        options = {"headers": headers}
        if query:
            options["params"] = query
        if method == "GET":
            options["params"] = flat
        else:
            options["content"] = urlencode(flat).encode("utf-8")
        try:
            request = self.client.build_request(method, self._endpoint_url(method, route), **options)
            request.headers.update(
                self._headers(route, include_dynapath, method, version=wire_version, request=request)
            )
            response = self.client.send(request)
        except (httpx.HTTPError, httpx.InvalidURL) as error:
            raise E.KorailTransportError("HTTP exchange failed; transaction outcome may be unknown") from error
        try:
            raw = response.json()
        except (ValueError, UnicodeError):
            error = E.KorailProtocolError("Response body is not valid JSON")
            error.raw = response.content
            if not response.is_success:
                error = E.KorailTransportError("HTTP server returned an error response")
                error.raw = response.content
            raise http_error_details(error, response, self.maintenance.clock())
        protected = route in load("constants")["DYNAPATH_ALLOWLIST_PATHS"]["items"]
        if protected and isinstance(raw, dict):
            blocked_codes = {"-1203", "-1406", "-2000", "-8005", "-8201", "-8202", "-8203"}
            blocked = next(
                (str(v) for v in raw.values() if type(v) in (int, str) and str(v) in blocked_codes),
                None,
            )
            if blocked:
                error = E.KorailDynaPathError("Server rejected protocol access")
                error.code = blocked
                error.raw = raw
                raise http_error_details(error, response, self.maintenance.clock())
        if not response.is_success:
            error = E.KorailTransportError(f"HTTP server returned status {response.status_code}")
            error.raw = raw
            raise http_error_details(error, response, self.maintenance.clock())
        common = route.startswith("/classes/") and not route.endswith(
            ("common.stationdata", "common.stationinfo")
        )
        try:
            result = parse_base_response(
                raw,
                raise_on_fail=raise_on_fail,
                require_envelope=require_envelope,
                common_out=common or require_envelope,
            )
        except E.KorailApiError as error:
            http_error_details(error, response, self.maintenance.clock())
            raise
        # A maintenance response must stop multi-step operations even when the
        # caller requested an inspectable business-failure envelope.
        if result.str_result == "FAIL":
            error = E.classify_app_error(result.h_msg_cd, result.h_msg_txt, raw=raw)
            if isinstance(error, (E.KorailServiceUnavailableError, E.KorailRateLimitError)):
                raise http_error_details(error, response, self.maintenance.clock())
        return result

    def _endpoint_url(self, method, route):
        # Resolve static endpoints once through httpx's public URL semantics.
        # Request headers, cookies, tokens and query arguments remain per-call.
        if self.client.params:
            return route
        base = self.client.base_url
        cached = self._endpoint_urls.get(route)
        if cached is not None and cached[0] is base:
            return cached[1]
        url = self.client.build_request(method, route).url
        if len(self._endpoint_urls) >= 256:
            del self._endpoint_urls[next(iter(self._endpoint_urls))]
        self._endpoint_urls[route] = (base, url)
        return url

    def post_form(self, route, form=None, **kwargs):
        return self.exchange(route, form, **kwargs)

    def post_mutation_form(self, route, form=None, **kwargs):
        return self.exchange(route, form, **kwargs)

    def get(self, route, params=None, **kwargs):
        return self.exchange(route, params, method="GET", **kwargs)
