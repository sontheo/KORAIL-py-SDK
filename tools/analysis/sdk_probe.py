#!/usr/bin/env python3
"""Inspect the product SDK's actual search request, optionally live.

Mock mode never uses the network. Live mode sends one anonymous search.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from urllib.parse import parse_qs

import httpx

from korail_py_sdk import KorailClient, KorailConfig, TrainSearchQuery
from korail_py_sdk.models.errors import KorailDynaPathError


def request_summary(request: httpx.Request) -> dict:
    form = {}
    try:
        form = {k: v[0] for k, v in parse_qs(request.content.decode("utf-8")).items()}
    except Exception:
        pass
    token = request.headers.get("x-dynapath-m-token", "")
    return {
        "method": request.method,
        "host": request.url.host,
        "path": request.url.path,
        "user_agent": request.headers.get("user-agent"),
        "version": form.get("Version"),
        "app_version": form.get("AppVersion"),
        "device": form.get("Device"),
        "key": form.get("Key"),
        "token_prefix": token[:5],
        "token_length": len(token),
        "sid_present": bool(form.get("Sid")),
        "form_keys": sorted(form),
    }


def mock_probe() -> dict:
    captured: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request_summary(request))
        if request.url.path.endswith("/ScheduleView"):
            return httpx.Response(
                200,
                json={"strResult": "SUCC", "h_msg_cd": "IRG000000", "trn_infos": {"trn_info": []}},
            )
        return httpx.Response(200, json={"strResult": "SUCC", "h_msg_cd": "API.I00000"})

    config = KorailConfig(dynapath_mode="v2-declaration", netfunnel_enabled=False, timeout=10, transport_profile="httpx")
    client = KorailClient(config, transport=httpx.MockTransport(handler))
    client._station_names = {"0001": "서울", "0020": "부산"}
    try:
        client.search_trains(TrainSearchQuery("0001", "0020", "20991231", "090000"))
    finally:
        client.close()
    return {"mode": "mock", "requests": captured}


def live_probe(netfunnel: bool) -> dict:
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y%m%d")
    config = KorailConfig(
        dynapath_mode="v2-declaration",
        netfunnel_enabled=netfunnel,
        timeout=30,
        netfunnel_wait_limit=15,
    )
    client = KorailClient(config)
    result = {
        "mode": "live",
        "host": config.base_url,
        "netfunnel": netfunnel,
        "version_default": config.version,
        "user_agent": config.user_agent,
    }
    try:
        page = client.search_trains(TrainSearchQuery("서울", "부산", tomorrow, "090000"))
        result.update(
            query_success=True,
            app_result=page.raw.get("strResult"),
            train_count=len(page.trains),
        )
    except KorailDynaPathError as error:
        result.update(
            query_success=False,
            error_type=type(error).__name__,
            http=getattr(error, "status_code", None),
            code=getattr(error, "code", None),
            dynapath_code=getattr(error, "dynapath_code", None),
            h_msg_cd=getattr(error, "h_msg_cd", None),
            request_id=getattr(error, "request_id", None),
            message=str(error),
        )
    except Exception as error:
        result.update(query_success=False, error_type=type(error).__name__, message=str(error)[:500])
    finally:
        client.close()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--netfunnel", action="store_true")
    args = parser.parse_args()
    print(json.dumps(live_probe(args.netfunnel) if args.live else mock_probe(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
