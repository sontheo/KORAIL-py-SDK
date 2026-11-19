"""Schema-directed decoding with explicit treatment of missing and invalid values."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from collections.abc import Mapping
from functools import lru_cache

from korail_py_sdk.models.errors import KorailProtocolError
from korail_py_sdk.protocol.schema import load

MISSING = object()


def path_value(raw, path):
    keys = iter(path or ())
    for key in keys:
        if key == "*":
            if not isinstance(raw, (list, tuple)):
                return MISSING
            tail = tuple(keys)
            result = []
            for row in raw:
                child = path_value(row, tail)
                if isinstance(child, list):
                    result.extend(child)
                elif child is not MISSING:
                    result.append(child)
            return result
        if type(raw) is dict:
            raw = raw.get(key, MISSING)
        elif isinstance(raw, Mapping) and key in raw:
            raw = raw[key]
        else:
            return MISSING
    return raw


def scalar(value, kind="str", *, required=False):
    valid = type(value) in (str, int, float) if kind == "float" else type(value) in (str, int)
    if not valid:
        if required:
            raise KorailProtocolError("Response contains an invalid required scalar")
        return None
    if kind == "str":
        return str(value)
    if kind == "int" and required and isinstance(value, str) and re.fullmatch(r"-?[0-9]+", value) is None:
        raise KorailProtocolError("Response contains an invalid integer")
    try:
        return {"int": int, "float": float}[kind](value)
    except (ValueError, OverflowError) as error:
        if required:
            raise KorailProtocolError("Response contains an invalid number") from error
        return None


EXPLICIT = {
    "BaseKorailResponse": {"h_msg_cd": ["h_msg_cd"], "h_msg_txt": ["h_msg_txt"], "str_result": ["strResult"]},
    "StationDataResponse": {"stations": ["stns", "stn"]},
    "SeatCar": {"attributes": ["seatAttInfos"]},
    "LimousineSeatInventoryResponse": {"windows": ["windowList"]},
    "PassAvailabilityResponse": {"ticket_issue_dates": ["ticket_info", "*", "h_ise_dt2"]},
    "KorailStation": {"code": ["stn_cd"], "name": ["stn_nm"]},
    "TrainSummary": {
        "general_reservation_code": ["h_gen_rsv_cd"],
        "special_reservation_code": ["h_spe_rsv_cd"],
        "general_reservation_flag": ["h_gen_rsv_flg"],
        "special_reservation_flag": ["h_spe_rsv_flg"],
        "wait_reservation_flag": ["h_wait_rsv_flg"],
        "standing_reservation_code": ["h_stnd_rsv_cd"],
        "arrival_date": ["h_arv_dt"],
        "merge_seat_application_flag": ["h_mg_seat_apl_flg"],
    },
    "TrainSearchMetadata": {
        "next_page_flag": ["h_next_pg_flg"],
        "next_query_station_no": ["h_qry_st_no_next"],
        "next_train_no": ["h_trn_no_next"],
        "next_preceding_train_no": ["h_prcd_trn_no_next"],
        "next_connecting_train_no": ["h_ectb_trn_no_next"],
        "result_count": ["h_rslt_cnt"],
    },
    "ReservationHoldResponse": {
        "pnr_no": ["h_pnr_no"],
        "journey_count": ["h_jrny_cnt"],
        "window_no": ["h_wct_no"],
        "received_amount": ["h_tot_rcvd_amt"],
        "journeys": ["jrny_infos", "jrny_info"],
    },
}


def _enforce(name, raw):
    rules = load("validation-rules")
    for kind in ("required", "not_null"):
        for path in rules[kind].get(name, ()):
            if len(path) > 1 and path_value(raw, path[:-1]) in (MISSING, None):
                continue
            result = path_value(raw, path)
            if (kind == "required" and result is MISSING) or (kind == "not_null" and result is None):
                error = KorailProtocolError(f"Response {name} has a missing or null required field")
                error.raw = raw
                raise error


@lru_cache(maxsize=None)
def _plan(name):
    from korail_py_sdk.models.records import CONTRACT, REGISTRY

    spec = CONTRACT["models"][name]
    mapping = dict(load("responses").get(name, {}))
    if any(f["name"] == "str_result" for f in spec["fields"]):
        mapping.update(EXPLICIT["BaseKorailResponse"])
    mapping.update(EXPLICIT.get(name, {}))
    plans = []
    for f in spec["fields"]:
        annotation = f["type"]
        nested = next((token for token in re.findall(r"[A-Za-z_]\w*", annotation) if token in REGISTRY), None)
        plans.append((f, mapping.get(f["name"]), annotation, nested))
    return REGISTRY[name], plans


def decode(name, raw):
    try:
        return _decode(name, raw)
    except KorailProtocolError as error:
        if error.raw is None:
            error.raw = raw
        raise
    except (TypeError, ValueError, OverflowError) as cause:
        error = KorailProtocolError(f"Invalid response value in {name}")
        error.raw = raw
        raise error from cause


def _decode(name, raw):
    if name == "BaseKorailResponse":
        from korail_py_sdk.protocol.envelope import decode_envelope

        return decode_envelope(raw)
    if not isinstance(raw, Mapping):
        error = KorailProtocolError("Expected a response object")
        error.raw = raw
        raise error
    for key in ("strResult", "h_msg_cd", "h_msg_txt"):
        val = raw.get(key)
        if val is not None:
            try:
                if type(val) not in (str, int):
                    raise ValueError
                str(val)
            except ValueError:
                error = KorailProtocolError(
                    "Response envelope contains an invalid or unsupported numeric value"
                )
                error.raw = raw
                raise error from None
    if name in {"TrainSearchResult", "TransferSearchResult"}:
        return decode_search(name, raw)
    _enforce(name, raw)
    if name in {"ReservationHoldResponse", "ReservationJourney"}:
        for key in ("jrny_infos", "seat_infos"):
            if key in raw and raw[key] is not None and not isinstance(raw[key], Mapping):
                raise KorailProtocolError("Reservation response contains an invalid row container")
        if name == "ReservationHoldResponse" and "h_pnr_no" in raw and raw["h_pnr_no"] is not None:
            scalar(raw["h_pnr_no"], required=True)
    if name == "RefundTicketResponse":
        settlements = raw.get("stlList", MISSING)
        if settlements is MISSING or (settlements is not None and not isinstance(settlements, list)):
            raise KorailProtocolError("Refund response requires a nullable settlement list")
        for row in settlements or ():
            try:
                if not isinstance(row, Mapping):
                    raise KorailProtocolError("Settlement row must be an object")
                scalar(row.get("stl_mns_cd"), required=True)
            except KorailProtocolError as error:
                error.raw = row
                raise
    if name == "DeliveredTicketRetrievalResponse":
        if isinstance(raw.get("prsList"), list) and any(
            not isinstance(row, Mapping) or "prsFlg" not in row for row in raw["prsList"]
        ):
            raise KorailProtocolError("Ticket retrieval row is missing its result")
    if name in {"TrainSummary", "TrainSearchMetadata"}:
        return _decode_flat(name, raw)
    if (
        name in {"LimousineScheduleResponse", "LimousineSeatInventoryResponse"}
        and raw.get("strResult") != "SUCC"
    ):
        raise KorailProtocolError("Limousine response requires a successful envelope")
    if name == "StationInfoResponse":
        for key in ("count", "map_version"):
            scalar(raw.get(key), required=True)
    if name == "StationDataResponse":
        station_container = raw.get("stns")
        if not isinstance(station_container, Mapping) or not isinstance(station_container.get("stn"), list):
            raise KorailProtocolError("Station data requires a station list")
    if name == "UuidResponse" and not (
        type(raw.get("mutMrkVrfCd")) in (str, int) and str(raw["mutMrkVrfCd"]).strip()
    ):
        raise KorailProtocolError("UUID response is missing its verification code")
    cls, plans = _plan(name)
    rules = load("response-rules")
    defaults = rules["missing_defaults"].get(name, {})
    lenient = rules["lenient_collections"].get(name, ())
    skip_rows = rules.get("skip_non_object_rows", {}).get(name, ())
    kwargs = {}
    for f, path, annotation, nested in plans:
        key = f["name"]
        if key == "raw":
            kwargs[key] = raw
            continue
        item = path_value(raw, path) if path is not None else MISSING
        if name == "PassMenuData" and key == "station_selection" and item is MISSING:
            item = raw.get("h_select_station", raw.get("h_seiect_station", MISSING))
        if item is MISSING:
            if name == "TicketReceipt" and key == "passenger_counts":
                kwargs[key] = tuple(
                    scalar(raw.get(f"h_psg_type{i}_cnt"), "int", required=True) for i in (1, 2, 3)
                )
                continue
            if key in defaults:
                kwargs[key] = defaults[key]
                continue
            if "default" not in f and "factory" not in f:
                if "None" in annotation:
                    kwargs[key] = None
                    continue
                if annotation.startswith(("tuple[", "list[")):
                    kwargs[key] = () if annotation.startswith("tuple[") else []
                    continue
                raise KorailProtocolError(f"Response is missing required {name}.{key}")
            continue
        if annotation.startswith(("tuple[", "list[")):
            if item is None:
                item = []
            if not isinstance(item, (tuple, list)):
                if key in lenient or (name == "LimousineSeatInventoryResponse" and key == "windows"):
                    item = []
                else:
                    raise KorailProtocolError(f"Response {name}.{key} must contain rows")
            if nested and key in skip_rows:
                item = [row for row in item if isinstance(row, Mapping)]
            if name == "LimousineSeatInventoryResponse" and key == "windows":
                valid = []
                for row in item:
                    if not isinstance(row, Mapping):
                        continue
                    if all(
                        k not in row
                        or ((ratio := scalar(row[k], "float")) is not None and math.isfinite(ratio))
                        for k in ("st_loc_rt", "cls_loc_rt")
                    ):
                        valid.append(row)
                item = valid
            rows = [
                decode(nested, row)
                if nested
                else row
                if "Mapping" in annotation or "object" in annotation
                else scalar(row, required="None" not in annotation)
                for row in item
            ]
            kwargs[key] = tuple(rows) if annotation.startswith("tuple[") else rows
        elif nested:
            kwargs[key] = None if item is None else decode(nested, item)
        elif "Mapping" in annotation or "dict[" in annotation:
            kwargs[key] = item
        elif "bool" in annotation:
            kwargs[key] = item if type(item) is bool else None
        else:
            if name == "SeatCar" and key in {"car_no", "remaining_seat_count"}:
                scalar(item, "int", required=True)
            if name == "SeatWindow":
                scalar(item, "float", required=True)
            if (
                name == "ReservationHoldResponse"
                and key == "journey_count"
                and item is not None
                and type(item) not in (str, int)
            ):
                raise KorailProtocolError("Reservation journey count has an invalid type")
            kind = (
                "int"
                if annotation.startswith(("int", "<class 'int'"))
                else "float"
                if annotation.startswith("float")
                else "str"
            )
            kwargs[key] = scalar(item, kind, required="None" not in annotation)
    if name == "AppDataResponse" and not isinstance(raw.get("notice"), Mapping):
        kwargs["notice"] = None
    if name == "CommuterInfoResponse":
        kwargs["available_passenger_count_from"] = scalar(raw.get("avlPrnbFrom", 0), "int")
    if name == "RefundTicketResponse":
        kwargs["settlement_list_is_null"] = "stlList" in raw and raw["stlList"] is None
    if name == "ReservationHoldResponse":

        def money(value):
            if type(value) is int:
                return value if value >= 0 else None
            if isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
                return int(value)
            return None

        declared = money(raw.get("h_tot_rcvd_amt"))
        total = 0
        invalid = False
        for journey in kwargs.get("journeys", ()):
            container = journey.raw.get("seat_infos")
            seats = container.get("seat_info") if isinstance(container, Mapping) else None
            if not isinstance(seats, list):
                continue
            for seat in seats:
                parsed = money(seat.get("h_rcvd_amt")) if isinstance(seat, Mapping) else None
                if parsed is None:
                    invalid = True
                else:
                    total += parsed
        if not invalid and total > 0 and declared is not None and declared != total:
            raise KorailProtocolError("Reservation settlement total does not match seat amounts")
        amount = None if invalid else total or declared
        try:
            kwargs["received_amount"] = str(amount) if amount is not None else None
        except ValueError as error:
            raise KorailProtocolError("Reservation contains an unsupported numeric value") from error
    try:
        return cls(**kwargs)
    except (TypeError, ValueError) as error:
        raised = KorailProtocolError(f"Cannot decode {name}")
        raised.raw = raw
        raise raised from error


@lru_cache(maxsize=3)
def _flat_plan(name):
    cls, fields = _plan(name)
    return cls, tuple((field["name"], path[0]) for field, path, _, _ in fields if path and len(path) == 1)


def _decode_flat(name, raw):
    # Train rows have a flat, optional scalar schema. Skipping absent fields
    # preserves constructor defaults and avoids the general collection decoder.
    cls, fields = _flat_plan(name)
    values = {"raw": raw}
    if name == "TrainSummary":
        values["train_no"] = ""
    for field, wire in fields:
        item = raw.get(wire, MISSING)
        if item is not MISSING:
            converted = scalar(item)
            values[field] = converted if field != "train_no" or converted is not None else ""
    return cls(**values)


def decode_search(name, raw):
    from korail_py_sdk.models.records import REGISTRY

    rows = path_value(raw, ["trn_infos", "trn_info"])
    if rows is MISSING:
        rows = []
    if not isinstance(rows, list):
        raise KorailProtocolError("Train response rows must be a list")
    trains = [decode("TrainSummary", row) for row in rows]
    for row in rows:
        number = row.get("h_trn_no")
        if number and type(number) not in (str, int):
            raise KorailProtocolError("Train number has an invalid type")
    common = {
        "trains": trains,
        "response": decode("BaseKorailResponse", raw),
        "raw": raw,
        "metadata": decode("TrainSearchMetadata", raw),
    }
    if name == "TransferSearchResult":
        groups = defaultdict(list)
        for train in trains:
            groups[train.train_sequence].append(train)
        common["itineraries"] = [
            REGISTRY["TransferItinerary"](*legs) for legs in groups.values() if len(legs) == 2
        ]
    else:
        common["unfiltered_trains"] = trains
    return REGISTRY[name](**common)
