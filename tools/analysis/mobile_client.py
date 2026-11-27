#!/usr/bin/env python3
"""Mobile ScheduleView client with a fresh device identity and dynamic rt history."""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import string
import time
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from korail_py_sdk.models.records import REGISTRY
from korail_py_sdk.security.declaration import DeclarationTokenProvider, encode_declaration
from korail_py_sdk.security.legacy import generate_dynapath_token

BASE = "https://smart.letskorail.com"
SCHEDULE_PATH = "/classes/com.korail.mobile.seatMovie.ScheduleView"
TOKEN_HEADER = "x-dynapath-m-token"
USER_AGENT = "korailtalk"
APP_VERSION = "7.0.10"
WIRE_VERSION = "250722001"
SDK_VERSION = "v1.0.3"
DEVICE_MODEL = "SM-S911N"
OS_RELEASE = "15"
AS_VALUE = "[38ff229cb34c7dda8e28220a2d750cce]"
BOARD = "kalama"
SDK_INT = 35
STRONGBOX = True
API_KEY = "korail1234567890"
SID_KEY = b"2485dd54d9deaa36"


@dataclass(frozen=True)
class SearchLeg:
    departure: str = "서울"
    arrival: str = "부산"
    run_date: str = ""
    run_time: str = "090000"
    train_group: str = "100"


def generate_sid(timestamp_ms: int) -> str:
    padder = padding.PKCS7(128).padder()
    plaintext = ("AD" + str(timestamp_ms)).encode("utf-8")
    padded = padder.update(plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(SID_KEY), modes.CBC(SID_KEY)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode("ascii") + "\n"


class DynaPathBlocked(RuntimeError):
    def __init__(self, http: int, code: str | None, request_id: str | None, message: str | None):
        self.http = http
        self.code = code
        self.request_id = request_id
        self.message = message
        super().__init__(f"HTTP {http} code={code} id={request_id} message={message}")


class BusinessFailure(RuntimeError):
    def __init__(self, http: int, h_msg_cd: str | None, h_msg_txt: str | None, raw: dict[str, Any]):
        self.http = http
        self.h_msg_cd = h_msg_cd
        self.h_msg_txt = h_msg_txt
        self.raw = raw
        super().__init__(f"HTTP {http} {h_msg_cd}: {h_msg_txt}")


class MobileScheduleClient:
    def __init__(
        self,
        device_id: str | None = None,
        *,
        app_start_ts: int | None = None,
        token_mode: str = "v2",
        token_format: str = "full",
        base_url: str = BASE,
        netfunnel: bool = False,
        sid: bool = False,
        proxy: str | None = None,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if token_mode not in {"v1", "v2"}:
            raise ValueError("token_mode must be v1 or v2")
        self.token_mode = token_mode
        self.token_format = token_format
        self.base_url = base_url.rstrip("/")
        self.netfunnel = netfunnel
        self.sid = sid
        self.proxy = proxy
        self.device_id = device_id or secrets.token_hex(16 if token_mode == "v1" else 8)
        now = int(time.time() * 1000)
        self.app_start_ts = app_start_ts or now
        self._last_request_ms = self.app_start_ts
        self._intervals: deque[int] = deque(maxlen=5)
        self._declaration = (
            DeclarationTokenProvider(
                device_id=self.device_id,
                model=DEVICE_MODEL,
                release=OS_RELEASE,
                manufacturer="samsung",
                board=BOARD,
                sdk_int=SDK_INT,
                strongbox=STRONGBOX,
            )
            if token_mode == "v2"
            else None
        )
        self._client = httpx.Client(timeout=timeout, transport=transport, proxy=proxy)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "MobileScheduleClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _token(self, now_ms: int) -> str:
        if self._declaration is not None:
            if self.token_format == "captured-data":
                return self._captured_data_token(now_ms)
            return self._declaration()
        interval = max(0, now_ms - self._last_request_ms)
        self._intervals.append(interval)
        self._last_request_ms = now_ms
        settings = REGISTRY["DynapathTokenSettings"](
            device_id=self.device_id,
            as_value=AS_VALUE,
            app_start_ts=str(self.app_start_ts),
            os_version=OS_RELEASE,
            device_model=DEVICE_MODEL,
            sdk_version=SDK_VERSION,
        )
        nonce = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(4))
        return generate_dynapath_token(
            settings,
            timestamp_ms=now_ms,
            random_text=nonce,
            recent_intervals=tuple(self._intervals),
        )

    def _captured_data_token(self, now_ms: int) -> str:
        def b64(value: str) -> str:
            return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")

        payload = "&".join(
            [
                "!v=2",
                "es=893617653734745139",
                f"ts={now_ms}",
                "st=Android",
                "sv=2.0.1",
                "ai=korailplus",
                f"os={b64(OS_RELEASE)}",
                f"dm={b64(DEVICE_MODEL)}",
                f"iid={b64(self.device_id)}",
            ]
        ).encode("ascii")
        return encode_declaration(payload, secrets.randbits(32))

    def _form(self, leg: SearchLeg, timestamp_ms: int) -> dict[str, str]:
        form = {
            "Device": "AD",
            "Version": WIRE_VERSION,
            "AppVersion": APP_VERSION,
            "Key": API_KEY,
            "txtMenuId": "11",
            "radJobId": "1",
            "selGoTrain": "05",
            "txtTrnGpCd": leg.train_group,
            "txtGoStart": leg.departure,
            "txtGoEnd": leg.arrival,
            "qryDvCd": "1",
            "txtGoAbrdDt": leg.run_date,
            "txtGoHour": leg.run_time,
            "txtPsgFlg_1": "1",
            "txtPsgFlg_2": "0",
            "txtPsgFlg_3": "0",
            "txtPsgFlg_4": "0",
            "txtPsgFlg_5": "0",
            "txtSeatAttCd_2": "000",
            "txtSeatAttCd_3": "000",
            "txtSeatAttCd_4": "015",
            "ebizCrossCheck": "N",
            "srtCheckYn": "N",
            "rtYn": "N",
            "adjStnScdlOfrFlg": "N",
        }
        if self.sid:
            form["Sid"] = generate_sid(timestamp_ms)
        return form

    def _send(self, leg: SearchLeg) -> httpx.Response:
        now_ms = int(time.time() * 1000)
        token = self._token(now_ms)
        return self._client.post(
            self.base_url + SCHEDULE_PATH,
            data=self._form(leg, now_ms),
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                TOKEN_HEADER: token,
            },
        )

    def search(self, leg: SearchLeg) -> dict[str, Any]:
        if self.netfunnel:
            from korail_py_sdk.models.records import KorailConfig
            from korail_py_sdk.transport.admission import Admission

            admission = Admission(
                KorailConfig(netfunnel_enabled=True, base_url=self.base_url, proxy=self.proxy)
            )
            try:
                with admission.enter("act_8", success_only=False):
                    response = self._send(leg)
            finally:
                admission.close()
        else:
            response = self._send(leg)
        try:
            body = response.json()
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}
        code = body.get("code") or body.get("dynaPathResultCode")
        request_id = body.get("id") or body.get("requestId")
        message = body.get("message") or body.get("errMsg")
        if code in {-2000, -4001, -8202, -8003} or str(code) in {"-2000", "-4001", "-8202", "-8003"}:
            raise DynaPathBlocked(response.status_code, str(code), request_id, message)
        if body.get("strResult") == "FAIL":
            raise BusinessFailure(response.status_code, body.get("h_msg_cd"), body.get("h_msg_txt"), body)
        return {
            "http": response.status_code,
            "code": code,
            "request_id": request_id,
            "strResult": body.get("strResult"),
            "h_msg_cd": body.get("h_msg_cd"),
            "h_msg_txt": body.get("h_msg_txt"),
            "train_count": len((body.get("trn_infos") or {}).get("trn_info") or []),
            "device_id": self.device_id,
            "token_mode": self.token_mode,
            "token_format": self.token_format,
            "host": self.base_url,
            "intervals": list(self._intervals),
        }


def default_leg() -> SearchLeg:
    tomorrow = date.today() + timedelta(days=1)
    return SearchLeg(run_date=tomorrow.strftime("%Y%m%d"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--device-id", default="")
    parser.add_argument("--token-mode", choices=["v1", "v2"], default="v2")
    parser.add_argument("--host", choices=["smart", "www"], default="smart")
    parser.add_argument("--token-format", choices=["full", "captured-data"], default="full")
    parser.add_argument("--netfunnel", action="store_true")
    parser.add_argument("--sid", action="store_true")
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--departure", default="서울")
    parser.add_argument("--arrival", default="부산")
    parser.add_argument("--run-date", default="")
    parser.add_argument("--run-time", default="090000")
    parser.add_argument("--jsonl", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    leg = default_leg()
    leg = SearchLeg(
        departure=args.departure,
        arrival=args.arrival,
        run_date=args.run_date or leg.run_date,
        run_time=args.run_time,
        train_group=leg.train_group,
    )
    base_url = "https://smart.letskorail.com" if args.host == "smart" else "https://www.korail.com"
    client = MobileScheduleClient(
        args.device_id or None,
        token_mode=args.token_mode,
        token_format=args.token_format,
        base_url=base_url,
        netfunnel=args.netfunnel,
        sid=args.sid,
        proxy=args.proxy,
    )
    rows: list[dict[str, Any]] = []
    for index in range(args.repeat):
        started = datetime.now(timezone.utc).isoformat()
        if args.dry_run:
            now_ms = int(time.time() * 1000)
            token = client._token(now_ms)
            rows.append({"index": index, "started_at": started, "token_len": len(token), "device_id": client.device_id, "dry_run": True})
        else:
            try:
                row = client.search(leg)
                row.update({"index": index, "started_at": started, "outcome": "SUCC"})
            except DynaPathBlocked as e:
                row = {"index": index, "started_at": started, "outcome": "BLOCKED", "http": e.http, "code": e.code, "request_id": e.request_id, "message": e.message}
            except BusinessFailure as e:
                row = {"index": index, "started_at": started, "outcome": "FAIL", "http": e.http, "h_msg_cd": e.h_msg_cd, "h_msg_txt": e.h_msg_txt}
            rows.append(row)
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
        if index + 1 < args.repeat:
            time.sleep(args.interval)
    if args.jsonl:
        with open(args.jsonl, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    client.close()


if __name__ == "__main__":
    os.umask(0o077)
    main()
