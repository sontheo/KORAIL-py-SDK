"""Reservation passenger, seat and journey rules."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum

from korail_py_sdk.models import errors as E
from korail_py_sdk.models.records import REGISTRY, KorailPassengerCounts, KorailReservationJobType
from korail_py_sdk.services.validation import _value, number, text


def _reservation(name, arguments, form):
    passengers = arguments.get("passengers") or KorailPassengerCounts()
    if not isinstance(passengers, KorailPassengerCounts):
        raise E.KorailProtocolError("Passengers must be a passenger-count value object")
    if passengers.teenager:
        raise E.KorailProtocolError("Unsupported teenager reservation discount P11")
    if passengers.infant and not (
        passengers.adult + passengers.senior + passengers.severe_disability + passengers.mild_disability
    ):
        raise E.KorailProtocolError("Infants require an accompanying adult passenger")
    if passengers.guide_dog > passengers.severe_disability + passengers.mild_disability:
        raise E.KorailProtocolError("Guide-dog count exceeds disabled passenger count")
    for key in list(form):
        if re.fullmatch(r"txt(?:CompaCnt|PsgTpCd|DiscKndCd)\d+", key):
            del form[key]
    categories = [
        ("adult", "1", "000"),
        ("child", "3", "000"),
        ("infant", "3", "321"),
        ("senior", "1", "131"),
        ("severe_disability", "1", "111"),
        ("mild_disability", "1", "112"),
        ("guide_dog", "1", "173"),
    ]
    rows = [
        (getattr(passengers, field), kind, discount)
        for field, kind, discount in categories
        if getattr(passengers, field)
    ]
    if name == "reserve_with_discount_card":
        if passengers.total != 1:
            raise E.KorailProtocolError("Discount-card reservation requires one passenger")
        rows = [(1, "1", "153")]
    for i, (count, kind, discount) in enumerate(rows, 1):
        form.update({f"txtCompaCnt{i}": count, f"txtPsgTpCd{i}": kind, f"txtDiscKndCd{i}": discount})
    form["txtTotPsgCnt"] = passengers.total
    legs = arguments.get("legs") or [
        arguments.get("train") or arguments.get("standing_hold_train") or arguments.get("schedule")
    ]
    for index, train in enumerate(legs, 1):
        if train is not None:
            if not hasattr(train, "train_no"):
                raise E.KorailProtocolError("Reservation requires a train or schedule value object")
            form[f"txtTrnNo{index}"] = text(train.train_no, "Train number").zfill(5)
    job = arguments.get("job_type", KorailReservationJobType.IMMEDIATE)
    form["txtJobId"] = _value(job)
    if "seat_class" in arguments:
        form["txtPsrmClCd1"] = _value(arguments["seat_class"])
    if arguments.get("seat_attribute_code") is not None:
        if re.fullmatch(r"[0-9]{3}", arguments["seat_attribute_code"]) is None:
            raise E.KorailProtocolError("Seat attribute must have three digits")
        form["txtSeatAttCd4"] = arguments["seat_attribute_code"]
    if name == "reserve_transfer":
        legs = arguments["legs"]
        if len(legs) != 2:
            raise E.KorailProtocolError("A transfer reservation requires exactly two legs")
        if legs[0].arrival_station_code != legs[1].departure_station_code:
            raise E.KorailProtocolError("Transfer legs must be different trains in boarding order")
        if legs[0].train_no == legs[1].train_no or (
            (legs[0].arrival_date or legs[0].departure_date or "", legs[0].arrival_time or "")
            > (legs[1].departure_date or "", legs[1].departure_time or "")
        ):
            raise E.KorailProtocolError("Transfer legs must be different trains in boarding order")
        form["txtDptTm1"] = legs[0].departure_time
        cabins = arguments["seat_classes"]
        cabins = [cabins] * 2 if isinstance(cabins, (str, Enum)) else list(cabins)
        if len(cabins) != 2:
            raise E.KorailProtocolError("A cabin is required for each transfer leg")
        for index, cabin in enumerate(cabins, 1):
            form[f"txtPsrmClCd{index}"] = _value(cabin)
            if _value(job) == "1101" and not (
                legs[index - 1].has_general_seat()
                if _value(cabin) == "1"
                else legs[index - 1].has_special_seat()
            ):
                raise E.KorailProtocolError("Transfer cabin has no available seat")
        if arguments.get("seat_attribute_codes") is not None:
            attributes = arguments["seat_attribute_codes"]
            if len(attributes) != 2:
                raise E.KorailProtocolError("A seat attribute is required for each transfer leg")
            for key, value in zip(("txtSeatAttCd4", "txtSeatAttCd4_1"), attributes):
                if value is not None:
                    if re.fullmatch(r"[0-9]{3}", value) is None:
                        raise E.KorailProtocolError("Seat attribute must have three digits")
                    form[key] = value
    seats = arguments.get("seats")
    if seats:
        groups = seats if name == "reserve_transfer" else [seats]
        for leg, group in enumerate(groups):
            if len(group) != passengers.total:
                raise E.KorailProtocolError("Seat count must match passenger count")
            suffix = str(leg) if leg else ""
            form[f"txtSrcarCnt{suffix}"] = len(group)
            for index, seat in enumerate(group, 1):
                tail = f"{leg}_{index}" if leg else str(index)
                form[f"txtSrcarNo{tail}"] = seat.car_no
                form[f"txtSeatNo{tail}"] = text(seat.seat_no, "Seat number")
    elif _value(job) == "1103":
        raise E.KorailProtocolError("Designated-seat reservation needs explicit seats")
    if name == "reserve":
        cabin = _value(arguments["seat_class"])
        train = arguments["train"]
        if _value(job) == "1102" and cabin != "1":
            raise E.KorailProtocolError("Standby reservations require a general cabin")
        if _value(job) == "1101" and not (
            train.has_general_seat() if cabin == "1" else train.has_special_seat()
        ):
            raise E.KorailProtocolError("No available general seat or requested special seat")
    if name == "reserve_merge" and arguments["merge_rows"]:
        if any(
            row.run_date and row.run_date != arguments["standing_hold_train"].run_date
            for row in arguments["merge_rows"]
        ):
            raise E.KorailProtocolError("Merge row run_date differs from the held train")
        cabin_attr = (
            "special_reservation_code" if _value(arguments["seat_class"]) == "2" else "general_reservation_code"
        )
        form["txtStndFlg"] = (
            "Y"
            if any(
                getattr(row, cabin_attr) == "13" and row.standing_reservation_code == "11"
                for row in arguments["merge_rows"]
            )
            else "N"
        )
    if name == "reserve_limousine":
        schedule = arguments["schedule"]
        if not isinstance(schedule, REGISTRY["LimousineSchedule"]):
            raise E.KorailProtocolError("Limousine reservation requires a schedule value object")
        if any(
            getattr(passengers, key)
            for key in ("teenager", "infant", "senior", "severe_disability", "mild_disability", "guide_dog")
        ):
            raise E.KorailProtocolError("Limousine reservations support adult and child passengers")
        for key in (
            "train_no",
            "train_class_code",
            "service_code",
            "departure_station_code",
            "arrival_station_code",
            "departure_run_order",
            "arrival_run_order",
        ):
            value = text(getattr(schedule, key), key)
            if re.fullmatch(r"[0-9]+", value) is None:
                raise E.KorailProtocolError("Limousine schedule contains a nonnumeric identifier")
        for key in ("run_date", "departure_date"):
            value = text(getattr(schedule, key), key)
            if re.fullmatch(r"[0-9]{8}", value) is None:
                raise E.KorailProtocolError("Limousine schedule contains an invalid date")
            try:
                datetime.strptime(value, "%Y%m%d")
            except ValueError as error:
                raise E.KorailProtocolError("Limousine schedule contains an invalid date") from error
        if re.fullmatch(r"[0-9]{6}", schedule.departure_time or "") is None:
            raise E.KorailProtocolError("Limousine schedule contains an invalid departure time")
        if number(schedule.general_remaining_seat_count, "Remaining seats") < passengers.total:
            raise E.KorailProtocolError("Limousine schedule does not have enough remaining seats")
        selected = arguments["seat_nos"]
        if not isinstance(selected, (tuple, list)) or len(selected) != passengers.total:
            raise E.KorailProtocolError("Limousine seat count must match passenger count")
        selected = [text(seat, "Seat number") for seat in selected]
        if len(set(selected)) != len(selected):
            raise E.KorailProtocolError("Limousine seats must be distinct")
        form["txtSrcarCnt"] = len(selected)
        for index, seat_no in enumerate(selected, 1):
            form[f"txtSrcarNo{index}"] = "0001"
            form[f"txtSeatNo{index}"] = text(seat_no, "Seat number")
