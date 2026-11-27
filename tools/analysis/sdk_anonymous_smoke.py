#!/usr/bin/env python3
"""Anonymous SDK smoke: station, schedule, pagination, transfer and fare reads. Never logs in."""

from __future__ import annotations

import argparse
import dataclasses as dc
import json
import time
from datetime import date, timedelta

from korail_py_sdk import KorailClient, KorailConfig, PriceFareLeg, PriceFareQuoteRequest, TrainSearchQuery


def _error(error: BaseException) -> dict:
    result = {
        "ok": False,
        "error_type": type(error).__name__,
        "message": str(error)[:300],
    }
    for name in ("code", "dynapath_code", "h_msg_cd", "status_code", "request_id"):
        value = getattr(error, name, None)
        if value is not None:
            result[name if name != "status_code" else "http"] = value
    return result


def _call(fn) -> tuple[dict, object | None]:
    started = time.monotonic()
    try:
        value = fn()
        return {"ok": True, "elapsed_ms": int((time.monotonic() - started) * 1000)}, value
    except Exception as error:
        result = _error(error)
        result["elapsed_ms"] = int((time.monotonic() - started) * 1000)
        return result, None


def run(
    proxy: str | None,
    netfunnel: bool,
    *,
    include_special: bool = False,
    include_variants: bool = False,
) -> dict:
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y%m%d")
    query = TrainSearchQuery("서울", "부산", tomorrow, "060000")
    config = KorailConfig(
        dynapath_mode="v2-declaration",
        netfunnel_enabled=netfunnel,
        timeout=30,
        netfunnel_timeout=3,
        netfunnel_wait_limit=15,
        proxy=proxy,
    )
    report = {
        "accounts_used": False,
        "netfunnel": netfunnel,
        "proxy": bool(proxy),
        "operations": {},
    }
    client = KorailClient(config)
    trains = None
    station_codes = {}
    try:
        result, data = _call(client.get_station_data)
        if data is not None:
            stations = list(data.stations)
            result["count"] = len(stations)
            station_codes = {station.name: station.code for station in stations}
            report["station_count"] = len(stations)
        report["operations"]["station_data"] = result

        result, data = _call(client.get_station_info)
        if data is not None:
            result.update(count=data.count, map_version=data.map_version)
        report["operations"]["station_info"] = result

        result, data = _call(client.get_train_calendar)
        if data is not None:
            result["count"] = len(data.days)
        report["operations"]["train_calendar"] = result

        result, data = _call(lambda: client.search_trains(query))
        if data is not None:
            trains = list(data.trains)
            result.update(count=len(trains), app_result=data.raw.get("strResult"))
            if trains:
                first = trains[0]
                result["first_train"] = {
                    "train_no": first.train_no,
                    "departure_time": first.departure_time,
                    "arrival_time": first.arrival_time,
                }
        report["operations"]["search_single"] = result

        result, data = _call(
            lambda: client.search_trains_all(query, max_time="120000", max_pages=3)
        )
        if data is not None:
            clocks = [train.departure_time for train in data]
            result.update(
                count=len(data),
                unique=len({(train.train_no, train.departure_date, train.departure_time) for train in data}) == len(data),
                ordered=clocks == sorted(clock for clock in clocks if clock),
            )
        report["operations"]["search_pagination"] = result

        result, data = _call(lambda: client.search_transfer_trains(query))
        if data is not None:
            result.update(
                itinerary_count=len(data.itineraries),
                train_count=len(data.trains),
                app_result=data.raw.get("strResult"),
            )
        report["operations"]["search_transfer"] = result

        if include_variants:
            for label, variant, kwargs in (
                ("search_srt", dc.replace(query, include_srt=True), {}),
                ("search_nearby", dc.replace(query, include_nearby_stations=True), {}),
                ("search_peak", query, {"peak_season": True}),
            ):
                result, data = _call(lambda variant=variant, kwargs=kwargs: client.search_trains(variant, **kwargs))
                if data is not None:
                    result.update(count=len(data.trains), app_result=data.raw.get("strResult"))
                report["operations"][label] = result

        if include_special:
            result, data = _call(
                lambda: client.search_trains(query, use_special_schedule=True)
            )
            result["optional"] = True
            if data is not None:
                result.update(count=len(data.trains), app_result=data.raw.get("strResult"))
            report["operations"]["search_special"] = result

        if trains:
            first = trains[0]
            run_date = first.run_date or first.departure_date or tomorrow
            result, data = _call(lambda: client.get_train_schedule(run_date, first.train_no))
            if data is not None:
                result.update(stop_count=len(data.stops), app_result=data.raw.get("strResult"))
            report["operations"]["train_schedule"] = result

            departure_code = first.departure_station_code or station_codes.get("서울")
            arrival_code = first.arrival_station_code or station_codes.get("부산")
            if departure_code and arrival_code:
                result, data = _call(lambda: client.get_transfer_stations(departure_code, arrival_code))
                if data is not None:
                    result["count"] = len(data.stations)
                report["operations"]["transfer_stations"] = result

                leg = PriceFareLeg(
                    departure_station_code=departure_code,
                    arrival_station_code=arrival_code,
                    run_date=run_date,
                    train_no=first.train_no,
                    requested_seat_attribute_code=first.seat_attribute_code or "000",
                    train_group_code=first.train_group_code or "100",
                    train_class_code=first.train_class_code or "00",
                )
                result, data = _call(
                    lambda: client.get_price_fare_quote(PriceFareQuoteRequest((leg,)))
                )
                if data is not None:
                    result.update(fare_count=len(data.fares), app_result=data.raw.get("strResult"))
                report["operations"]["price_fare"] = result
    finally:
        client.close()
    report["ok"] = all(
        item["ok"] for item in report["operations"].values() if not item.get("optional")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--no-netfunnel", action="store_true")
    parser.add_argument("--include-special", action="store_true")
    parser.add_argument("--include-variants", action="store_true")
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    reports = [
        run(
            args.proxy,
            not args.no_netfunnel,
            include_special=args.include_special,
            include_variants=args.include_variants,
        )
        for _ in range(args.repeat)
    ]
    print(json.dumps(reports if args.repeat > 1 else reports[0], ensure_ascii=False, indent=2))
    return 0 if all(report["ok"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
