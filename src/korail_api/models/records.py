"""Value objects built from the public constructor contract.

Request serialization and response decoding live in separate engines; these
objects hold data and small, independently implemented convenience operations.
"""

from __future__ import annotations

import copy
import dataclasses as dc
import re
import time
import uuid
from datetime import datetime
from enum import Enum

from korail_api.protocol.schema import load

CONTRACT = load("public-interface")
REGISTRY = {}


class _DefaultProtocolVersion(str):
    """Distinguish the omitted default from an explicitly supplied version."""


def restore(data):
    if isinstance(data, list):
        return [restore(v) for v in data]
    if not isinstance(data, dict):
        return data
    if "enum" in data:
        return REGISTRY[data["enum"]][data["member"]]
    if "model" in data and "fields" in data:
        fields = {k: restore(v) for k, v in data["fields"].items()}
        if data["model"] == "CommuterPassengerRequest":
            return REGISTRY[data["model"]].from_response(**fields)
        return REGISTRY[data["model"]](**fields)
    if "sequence" in data and "items" in data:
        return {"tuple": tuple, "set": set, "frozenset": frozenset}[data["sequence"]](
            restore(v) for v in data["items"]
        )
    if "callable" in data:
        if data["callable"] == "diagnostic_token":
            from korail_api.security.diagnostic import diagnostic_token

            return diagnostic_token
        return None
    return {k: restore(v) for k, v in data.items()}


def _post_init(self):
    from korail_api.models.errors import KorailProtocolError

    name = type(self).__name__
    if name == "KorailConfig":
        from korail_api.transport.curl import validate_proxy

        validate_proxy(self.proxy)
        if self.app_version is not None and (
            not isinstance(self.app_version, str) or not self.app_version.strip()
        ):
            raise ValueError("app_version must be nonempty text or None")
        if self.disable_dynapath and self.dynapath.token_provider is not None:
            from korail_api.security.diagnostic import diagnostic_token

            if self.dynapath.token_provider is not diagnostic_token:
                raise ValueError("Cannot disable an explicitly configured token provider")
        if self.dynapath_mode not in {"legacy", "v2-diagnostic"}:
            raise ValueError("Unsupported dynapath mode")
        if self.transport_profile not in {"httpx", "okhttp"}:
            raise ValueError("Unsupported transport profile")
        token_config = self.dynapath
        from korail_api.security.diagnostic import diagnostic_token

        if self.dynapath_mode == "legacy" and (
            token_config.token_provider is None or token_config.token_provider is diagnostic_token
        ):
            settings = token_config.token_settings or REGISTRY["DynapathTokenSettings"](
                device_id=uuid.uuid4().hex,
                as_value=load("legacy-protocol")["as_value"],
                app_start_ts=str(int(time.time() * 1000)),
                os_version=token_config.os_version,
                device_model=token_config.device_name,
            )
            token_config = dc.replace(token_config, enabled=True, token_provider=None, token_settings=settings)
        if self.disable_dynapath:
            token_config = dc.replace(token_config, enabled=False)
        elif self.dynapath_mode == "v2-diagnostic":
            from korail_api.security.diagnostic import diagnostic_token

            if token_config.token_provider is None:
                token_config = dc.replace(
                    token_config, enabled=True, token_provider=diagnostic_token, token_settings=None
                )
        object.__setattr__(self, "dynapath", token_config)
    if name == "KorailPassengerCounts":
        values = [getattr(self, f.name) for f in dc.fields(self)]
        if any(type(v) is not int or v < 0 for v in values) or not 1 <= sum(values) <= 9:
            raise KorailProtocolError("Passenger counts must be nonnegative integers with a positive total")
    if (
        name == "DynapathConfig"
        and self.enabled
        and self.token_provider is None
        and self.token_settings is None
    ):
        raise ValueError("Enabled token configuration needs a provider or token settings")
    if name == "LimousineSeatInventoryQuery" and (
        type(self.passenger_count) is not int or type(self.is_arrow) is not bool
    ):
        raise KorailProtocolError("Limousine seat query requires an integer count and a boolean direction flag")
    if name == "KorailSeatAssignment" and (type(self.car_no) is not int or self.car_no < 1 or not self.seat_no):
        raise KorailProtocolError("Seat assignment needs a positive car number and a seat number")
    if name == "CardPayment" and self.card_type not in ("J", "S"):
        raise KorailProtocolError("Unknown card type")
    if name == "KorailDeviceProfile":
        if any(
            not isinstance(v, str) or not v or "\n" in v or "\r" in v
            for v in [self.device_id, self.model, self.android_release, self.build_id]
        ):
            raise ValueError("Device profile fields must be nonempty single-line text")
    if (
        name == "SelfSeatChangeInfoRequest"
        and self.room_class_code is not None
        and (not isinstance(self.room_class_code, str) or not self.room_class_code.strip())
    ):
        raise KorailProtocolError("room_class_code must not be empty and must be text or None")


def _display(self):
    from korail_api.messages.catalog import resolve_error_message

    return resolve_error_message(self.h_msg_cd, self.h_msg_txt)


def _base_from_raw(cls, raw):
    from korail_api.protocol.codec import decode

    return decode(cls.__name__, raw)


def _duration(self):
    values = (self.departure_date, self.departure_time, self.arrival_date, self.arrival_time)
    if any(
        not isinstance(v, str) or re.fullmatch(r"[0-9]{8}" if i % 2 == 0 else r"[0-9]{6}", v) is None
        for i, v in enumerate(values)
    ):
        return None
    try:
        start = datetime.strptime((self.departure_date or "20000101") + self.departure_time, "%Y%m%d%H%M%S")
        end = datetime.strptime(
            (self.arrival_date or self.departure_date or "20000101") + self.arrival_time, "%Y%m%d%H%M%S"
        )
    except ValueError:
        return None
    minutes = int((end - start).total_seconds() // 60)
    return minutes if minutes >= 0 else None


def _next_page(self):
    metadata = self.metadata
    rows = getattr(self, "unfiltered_trains", None) or self.trains
    if not rows or metadata is None or metadata.next_page_flag != "Y":
        return None
    station = metadata.next_query_station_no
    train = (
        metadata.next_preceding_train_no
        if isinstance(self, REGISTRY["TransferSearchResult"])
        and metadata.next_connecting_train_no
        and metadata.next_preceding_train_no
        else metadata.next_train_no
    )
    return (
        REGISTRY["TrainSearchContinuation"](station, train, metadata.next_connecting_train_no or "")
        if station and train
        else None
    )


def _next_query(self, query):
    rows = self.unfiltered_trains if self.unfiltered_trains is not None else self.trains
    if not rows or not rows[-1].departure_time:
        return None
    last = rows[-1]
    return dc.replace(
        query, departure_date=last.departure_date or query.departure_date, departure_time=last.departure_time
    )


def _seat_from_inventory(cls, inventory, seat):
    from korail_api.models.errors import KorailProtocolError

    car = getattr(inventory, "car_no", None)
    if not car:
        raise KorailProtocolError("Inventory has no car number")
    return cls(int(car), seat.seat_no)


def _build_models():
    for name, members in CONTRACT["enums"].items():
        REGISTRY[name] = Enum(name, members, type=str, module=__name__)
    pending = dict(CONTRACT["models"])
    while pending:
        progress = False
        for name, spec in list(pending.items()):
            if any(base not in REGISTRY for base in spec["bases"]):
                continue
            bases = tuple(REGISTRY[base] for base in spec["bases"])
            inherited = {f.name for base in bases for f in dc.fields(base)}
            fields = []
            for f in spec["fields"]:
                if f["name"] in inherited:
                    continue
                options = {
                    "repr": f["repr"],
                    "init": f["init"],
                    "kw_only": f.get("kw_only", False),
                    "compare": f.get("compare", True),
                }
                if "default" in f:
                    encoded = f["default"]
                    if name == "KorailConfig" and f["name"] == "version":
                        options["default"] = _DefaultProtocolVersion(encoded)
                    elif encoded is None or type(encoded) in (str, int, bool, float):
                        options["default"] = encoded
                    else:
                        options["default_factory"] = lambda encoded=encoded: restore(copy.deepcopy(encoded))
                elif "factory" in f:
                    options["default_factory"] = lambda: REGISTRY["DynapathConfig"]()
                annotation = f["type"]
                if annotation.startswith("<class '"):
                    annotation = annotation[8:-2]
                fields.append((f["name"], annotation, dc.field(**options)))
            cls = dc.make_dataclass(
                name,
                fields,
                bases=bases,
                frozen=spec["frozen"],
                namespace={
                    "__module__": __name__,
                    **(
                        {"__post_init__": _post_init}
                        if name
                        in {
                            "KorailConfig",
                            "DynapathConfig",
                            "KorailPassengerCounts",
                            "LimousineSeatInventoryQuery",
                            "KorailSeatAssignment",
                            "CardPayment",
                            "KorailDeviceProfile",
                            "SelfSeatChangeInfoRequest",
                        }
                        else {}
                    ),
                },
            )
            REGISTRY[name] = cls
            del pending[name]
            progress = True
        if not progress:
            raise RuntimeError("Invalid public constructor dependency graph")
    globals().update(REGISTRY)


_build_models()


BaseKorailResponse.display_message = property(_display)
BaseKorailResponse.from_raw = classmethod(_base_from_raw)
TrainSummary.from_raw = classmethod(_base_from_raw)
KorailPassengerCounts.total = property(lambda self: sum(getattr(self, f.name) for f in dc.fields(self)))
TrainSummary.has_general_seat = lambda self: self.general_reservation_code == "11"
TrainSummary.has_special_seat = lambda self: self.special_reservation_code == "11"
TrainSummary.has_seat = lambda self: self.has_general_seat() or self.has_special_seat()
TrainSummary.has_waiting_list = lambda self: self.wait_reservation_flag == " 9"
TrainSummary.duration_minutes = property(_duration)


def _duration_text(self):
    minutes = self.duration_minutes
    if minutes is None:
        return None
    hours, remainder = divmod(minutes, 60)
    return (
        f"{hours}시간 {remainder}분" if hours and remainder else f"{hours}시간" if hours else f"{remainder}분"
    )


def _summary(self):
    def stamp(day, clock):
        return f"{day[:4]}-{day[4:6]}-{day[6:]} {clock[:2]}:{clock[2:4]}" if day and clock else "?"

    timing = stamp(self.departure_date, self.departure_time) + "~" + stamp(self.arrival_date, self.arrival_time)
    line = f"[{self.train_class_name or '열차'} {self.train_no}] {timing} {self.departure_station_name or '?'}~{self.arrival_station_name or '?'}"
    return line + (f" ({self.duration_text})" if self.duration_text is not None else "")


TrainSummary.duration_text = property(_duration_text)
TrainSummary.summary = _summary
TrainSearchResult.next_page = _next_page
TransferSearchResult.next_page = _next_page
TrainSearchResult.next_query_from_last_departure = _next_query
KorailSeatAssignment.from_inventory = classmethod(_seat_from_inventory)
ReservationHistoryResponse.trains = property(lambda self: self.items)
PaidTicket.from_refund_detail = classmethod(
    lambda cls, detail, train_no="": cls(
        detail.pnr_no,
        detail.sale_date,
        detail.original_window_no,
        detail.original_sale_sequence,
        detail.original_return_password,
        train_no,
    )
)
CartItem.usage_window = property(
    lambda self: (self.usage_start_date, self.usage_start_time, self.usage_close_time)
)
TransferItinerary.legs = property(lambda self: (self.first, self.second))
TransferItinerary.transfer_station_code = property(lambda self: self.first.arrival_station_code)
TransferItinerary.transfer_station_name = property(lambda self: self.first.arrival_station_name)
MaasServiceDetailQuery.current = classmethod(lambda cls: cls())
MaasServiceDetailQuery.history = classmethod(lambda cls, start_date, end_date: cls(start_date, end_date))


def _station_selection(self):
    required = [self.active == "Y", self.menu_type != "N", self.app_data not in (None, "", "N")]
    service = self.additional_service_code
    return all(required) and isinstance(service, str) and bool(service.strip())


def _card_schedule(
    cls,
    card_kind_management_no,
    *,
    departure_station_name,
    arrival_station_name,
    departure_date,
    usable_trip_count="",
    usage_period_days=None,
    page_no=None,
):
    return cls(
        card_kind_management_no,
        departure_station_name,
        arrival_station_name,
        departure_date,
        card_kind_code="MMM",
        usable_trip_count=usable_trip_count,
        usage_period_days=usage_period_days,
        page_no=page_no,
    )


def _commuter_passengers(cls, pass_data, source, passenger_counts):
    from korail_api.models.errors import KorailProtocolError

    if not isinstance(passenger_counts, tuple) or len(passenger_counts) != len(source.passenger_options):
        raise KorailProtocolError("Passenger counts must match the commuter passenger options")
    if any(type(v) is not int or v < 0 for v in passenger_counts) or not 1 <= sum(passenger_counts) <= 9:
        raise KorailProtocolError("Commuter passenger counts are invalid")
    result = object.__new__(cls)
    for field, value in (("pass_data", pass_data), ("source", source), ("passenger_counts", passenger_counts)):
        object.__setattr__(result, field, value)
    return result


def _commuter_constructor(self):
    raise TypeError("CommuterPassengerRequest must be created with from_response()")


def _refund_execution(cls, verification, *, customer_phone, customer_name):
    from korail_api.models.errors import KorailProtocolError

    if verification.str_result != "SUCC" or len(verification.original_tickets) != 1:
        raise KorailProtocolError("Station refund requires one successfully verified ticket")
    ticket = verification.original_tickets[0]
    fields = {
        field: getattr(ticket, field)
        for field in (
            "pnr_no",
            "original_sale_date",
            "original_sale_window_no",
            "original_sale_sequence",
            "original_return_password",
            "refund_division_code",
            "refund_reason_code",
            "ticket_kind_code",
        )
    }
    return cls(
        **fields,
        customer_phone=customer_phone,
        customer_name=customer_name,
        refund_amount=verification.refund_amount,
        refund_fee=verification.refund_fee,
    )


def _recalculation_for_hold(cls, hold, requested_discount_codes):
    from korail_api.models.errors import KorailProtocolError
    from korail_api.protocol.codec import scalar

    if hold.str_result != "SUCC":
        raise KorailProtocolError("Price recalculation requires a successful hold")
    if not isinstance(requested_discount_codes, (list, tuple)):
        raise KorailProtocolError("Requested discounts must be a sequence")
    seats = hold.journeys[0].raw.get("seat_infos", {}).get("seat_info") if hold.journeys else None
    if not isinstance(seats, list) or not seats:
        raise KorailProtocolError("Price recalculation requires first-journey seat rows")
    if len(seats) != len(requested_discount_codes):
        raise KorailProtocolError("Price recalculation needs one requested code per seat")
    rows = []
    for seat, discount in zip(seats, requested_discount_codes):
        try:
            converted = {
                key: scalar(seat.get(key))
                for key in ("h_psg_tp_cd", "h_psrm_cl_cd", "h_dcnt_knd_cd1", "dcnt_reld_no")
            }
            values = []
            for key in ("h_psg_tp_cd", "h_psrm_cl_cd", "h_dcnt_knd_cd1"):
                item = converted[key]
                if item is None:
                    raise KorailProtocolError(f"Price recalculation seat field {key} must be a scalar")
                values.append(item)
            rows.append(PriceRecalculationRow(*values, discount, converted["dcnt_reld_no"] or ""))
        except (KorailProtocolError, ValueError) as cause:
            error = KorailProtocolError(
                str(cause)
                if isinstance(cause, KorailProtocolError)
                else "Invalid first-journey seat value for price recalculation"
            )
            error.raw, error.parser_raw = hold.raw, seat
            raise error from cause
    return cls(hold.pnr_no, tuple(rows))


MaasMenuItem.uses_station_selection = property(_station_selection)
DiscountCardScheduleRequest.for_card = classmethod(_card_schedule)
CommuterPassengerRequest.from_response = classmethod(_commuter_passengers)
CommuterPassengerRequest.__init__ = _commuter_constructor
StationRefundExecutionRequest.from_verification = classmethod(_refund_execution)
PriceRecalculationRequest.for_hold = classmethod(_recalculation_for_hold)

# Names used by postponed public annotations must remain available to
# typing.get_type_hints, including module-qualified collection annotations.
import collections as collections
import typing as typing
from collections.abc import Callable as Callable
from collections.abc import Mapping as Mapping
from collections.abc import Sequence as Sequence
from typing import Any as Any
from typing import Literal as Literal

KorailSelfSeatChangeRoomClassCode = str
KorailLoginInputFlag = Literal["2", "4", "5"]
KorailRoomClassCode = Literal["1", "2"] | REGISTRY["KorailSeatClass"]
KorailMileageLedger = Literal["1", "2"]
KorailMileageMovement = Literal["0", "1", "2"]
CommuterInfoRequest = (
    REGISTRY["CommuterInitialRequest"]
    | REGISTRY["CommuterPassengerRequest"]
    | REGISTRY["CommuterTicketInquiryRequest"]
)
DynapathTokenProvider = Callable[[REGISTRY["DynapathRequestContext"]], str | None]

TimestampMsProvider = Callable[[], int]
RandomTextProvider = Callable[[], str]
