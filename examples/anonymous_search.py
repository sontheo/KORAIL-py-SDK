"""Bounded anonymous schedule probe. Never logs headers, bodies, or queue keys."""

import argparse
import json
import logging
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from korail_py_sdk import KorailClient, KorailConfig, TrainSearchQuery
from korail_py_sdk.transport.curl import OkHttpTransport, env_proxy_url


class ReadOnlyTransport(httpx.BaseTransport):
    def __init__(self, inner):
        self.inner = inner
        self.searches = 0
        self.queue = 0
        self.started = time.monotonic()

    def handle_request(self, request):
        url = request.url
        if request.method != "POST" or url.scheme != "https" or url.port not in (None, 443):
            raise ValueError("only HTTPS POST reads allowed")
        if time.monotonic() - self.started > 90:
            raise ValueError("probe time budget exceeded")
        if url.host == "smart.letskorail.com" and url.path in (
            "/classes/com.korail.mobile.seatMovie.ScheduleView",
            "/classes/com.korail.mobile.seatMovie.ScheduleViewSpecial",
        ):
            self.searches += 1
            if self.searches > 6:
                raise ValueError("search budget exceeded")
        elif (
            url.host == "nf.letskorail.com"
            or re.fullmatch(r"rnf(?:[1-9]|[1-9][0-9])\.letskorail\.com", url.host or "")
        ) and url.path == "/ts.wseq":
            self.queue += 1
            if self.queue > 24 or url.params.get("opcode") not in ("5101", "5002", "5004") or request.read():
                raise ValueError("only bounded queue enter, poll, complete allowed")
        else:
            raise ValueError("only schedule and queue endpoints allowed")
        return self.inner.handle_request(request)

    def close(self):
        self.inner.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--proxy", default=None)
    args = parser.parse_args()
    logging.getLogger("korail_py_sdk.transport.admission").setLevel(logging.CRITICAL)
    guard = ReadOnlyTransport(OkHttpTransport(proxy=args.proxy or env_proxy_url()))
    client = KorailClient(
        KorailConfig(timeout=12, netfunnel_timeout=3, netfunnel_wait_limit=15), transport=guard
    )
    report = {"accounts_used": False, "success": False}
    try:
        tomorrow = (datetime.now(ZoneInfo("Asia/Seoul")) + timedelta(days=1)).strftime("%Y%m%d")
        trains = client.search_trains_all(
            TrainSearchQuery("서울", "부산", tomorrow, "060000"), max_time="100000", max_pages=6
        )
        clocks = [t.departure_time for t in trains]
        unique = len({(t.train_no, t.departure_date, t.departure_time) for t in trains}) == len(trains)
        report.update(
            count=len(trains),
            search_requests=guard.searches,
            queue_requests=guard.queue,
            unique=unique,
            ordered=clocks == sorted(clocks),
        )
        report["success"] = bool(
            len(trains) > 10
            and guard.searches > 1
            and unique
            and clocks == sorted(clocks)
            and max(clocks) >= "100000"
        )
    except Exception as error:
        report["error_type"] = type(error).__name__
    finally:
        client.close()
    print(json.dumps(report))
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
