"""Operation-specific invariants that cannot be expressed as field mappings."""

from __future__ import annotations

import dataclasses
import re
import time

from korail_api.models import errors as E
from korail_api.models.records import REGISTRY, KorailReservationJobType
from korail_api.services.payments import _payment
from korail_api.services.reservations import _reservation
from korail_api.services.search import _search
from korail_api.services.validation import number, text


def prepare(client, name, arguments, steps, forms):
    if "timestamp_ms" in arguments:
        forms[-1]["timeStamp"] = (
            arguments["timestamp_ms"] if arguments["timestamp_ms"] is not None else int(time.time() * 1000)
        )
    if name == "get_train_schedule":
        train_no = text(arguments["train_no"], "Train number")
        forms[-1]["trnNo"] = train_no.zfill(5)
    if name.startswith("search_"):
        _search(arguments, forms[-1])
        # Only the built-in read-only compatibility profile changes the omitted default.
        from korail_api.models.records import _DefaultProtocolVersion
        from korail_api.security.diagnostic import diagnostic_token

        if (
            name in {"search_trains", "search_transfer_trains"}
            and not arguments.get("use_special_schedule")
            and client.config.dynapath.enabled
            and client.config.dynapath.token_provider is diagnostic_token
            and steps[-1]["path"] in client.config.dynapath.allowlist_paths
            and isinstance(client.config.version, _DefaultProtocolVersion)
        ):
            forms[-1]["Version"] = "250722001"
        forms[-1]["txtGoStart"] = client._resolve_station_reference(arguments["query"].departure_station_code)
        forms[-1]["txtGoEnd"] = client._resolve_station_reference(arguments["query"].arrival_station_code)
        if arguments.get("use_special_schedule"):
            steps = [
                dict(row, path=row["path"].replace("ScheduleView", "ScheduleViewSpecial")) for row in steps
            ]
        return steps, forms
    if name.startswith("reserve"):
        _reservation(name, arguments, forms[-1])
    if name == "pay_with_card":
        _payment(arguments, forms[-1])
    if name in {"get_seat_inventory", "get_seat_cars"}:
        forms[-1]["trnNo" if name == "get_seat_inventory" else "txtTrnNo"] = text(
            arguments["train"].train_no, "Train number"
        ).zfill(5)
        field = "totPsgCnt" if name == "get_seat_inventory" else "txtTotPsgCnt"
        forms[-1][field] = number(arguments["passenger_count"], "Passenger count", minimum=1)
        forms[-1]["psrmClCd" if name == "get_seat_inventory" else "txtPsrmClCd"] = arguments["room_class_code"]
        if arguments.get("seat_attribute_code"):
            if re.fullmatch(r"[0-9]{3}", arguments["seat_attribute_code"]) is None:
                raise E.KorailProtocolError("Seat attribute must have three digits")
            forms[-1]["seatAttCd" if name == "get_seat_inventory" else "txtSeatAttCd"] = arguments[
                "seat_attribute_code"
            ]
    if name == "get_reservation_hold":
        text(arguments["pnr_no"], "Reservation number")
    if name in {"get_pbp_acceptance_specifications", "get_original_ticket_inquiry"}:
        tickets = arguments["tickets"]
        if (
            not isinstance(tickets, (tuple, list))
            or not tickets
            or any(not isinstance(t, REGISTRY["OriginalTicketReference"]) for t in tickets)
        ):
            raise E.KorailProtocolError("Tickets must be a nonempty sequence of original ticket references")
        forms[-1]["tkCnt"] = (
            len(tickets) if arguments.get("ticket_count") is None else arguments["ticket_count"]
        )
        if name == "get_pbp_acceptance_specifications":
            forms[-1]["tkRetNo"] = [
                "-".join((t.sale_window_no, t.sale_date, t.sale_sequence, t.return_password)) for t in tickets
            ]
        else:
            for index, ticket in enumerate(tickets, 1):
                for prefix, attr in (
                    ("ogtkSaleWctNo", "sale_window_no"),
                    ("ogtkSaleDd", "sale_date"),
                    ("ogtkSaleSqno", "sale_sequence"),
                    ("ogtkRetPwd", "return_password"),
                ):
                    forms[-1][f"{prefix}_{index}"] = getattr(ticket, attr)
    if name == "get_reservation_history":
        forms[-1]["timeStamp"] = "0"
    if name == "get_seat_assignment_schedule":
        request = arguments["request"]
        count = number(request.passenger_count, "Passenger count", minimum=1)
        for index in range(1, count + 1):
            forms[-1].update(
                {
                    f"seatAttCd{index}": request.seat_attribute_code,
                    f"psgNum{index}": "1",
                    f"stlbDturDvNm{index}": request.standing_detour_division_name,
                }
            )
    if name == "get_commuter_info":
        request = arguments["request"]
        if isinstance(request, (REGISTRY["CommuterInitialRequest"], REGISTRY["CommuterPassengerRequest"])):
            common = {
                k: v for k, v in forms[-1].items() if k in {"Device", "Version", "AppVersion", "Key", "lang"}
            }
            common.update(jobDvCd="a", cmtrKndCd=request.pass_data.commuter_kind_code, psgCnt="0")
            if isinstance(request, REGISTRY["CommuterPassengerRequest"]):
                counts = request.passenger_counts
                options = request.source.passenger_options
                if (
                    not isinstance(counts, (tuple, list))
                    or len(counts) != len(options)
                    or any(type(n) is not int or n < 0 for n in counts)
                ):
                    raise E.KorailProtocolError("Commuter passenger counts must match its age options")
                common.update(
                    jobDvCd="b",
                    psgCnt=str(sum(counts)),
                    cmtrUtlAgeCd=[
                        option.commuter_usage_age_code for option, n in zip(options, counts) for _ in range(n)
                    ],
                )
            forms[-1] = common
    if name in {
        "get_self_checkin_info",
        "check_self_checkin_seat",
        "register_self_checkin",
        "cancel_self_checkin",
    }:
        detail = arguments["detail"]
        for attr in (
            "original_window_no",
            "original_sale_date",
            "original_sale_sequence",
            "original_return_password",
        ):
            text(getattr(detail, attr), "Original ticket reference")
        if name == "check_self_checkin_seat":
            text(arguments["qr_code"], "Seat QR code")
    if name == "cancel_unpaid_hold":
        hold = arguments["hold"]
        if hold.str_result != "SUCC" or not hold.pnr_no:
            raise E.KorailProtocolError("Cancellation requires a successful reservation hold")
        if not arguments.get("check_first", True):
            steps, forms = steps[-1:], forms[-1:]
        for form in forms:
            if hold.journeys:
                form["txtJrnySqno"] = hold.journeys[0].journey_sequence
                form["hidRsvChgNo"] = hold.journeys[0].reservation_change_no
            form["txtJrnyCnt"] = hold.journey_count
    if name == "confirm_standby_hold":
        hold = arguments["hold"]
        if hold.str_result != "SUCC":
            raise E.KorailProtocolError("Standby options require an existing standby hold")
        if arguments["sms_notify"]:
            forms[-1]["txtSmsSndFlg"] = "Y"
            forms[-1]["txtCpNo"] = text(arguments.get("phone_no"), "SMS phone number")
    if name == "refund":
        commission = arguments["commission"]
        if not isinstance(commission, REGISTRY["RefundCommissionResponse"]):
            raise E.KorailProtocolError("Call get_refund_commission and supply its commission response")
        if commission.str_result != "SUCC":
            error = E.KorailProtocolError("Refund requires a successful commission inquiry")
            error.raw = commission.raw
            raise error
        if arguments["settle_mileage"]:
            try:
                enough = number(commission.usable_mileage, "Available mileage") >= number(
                    commission.refund_fee, "Refund fee"
                )
            except E.KorailProtocolError:
                enough = False
            if not enough:
                raise E.KorailProtocolError("Available mileage is below the fee")
        if arguments.get("pbp_acceptance_target_flag") is not None:
            forms[-1]["pbpAcepTgtFlg"] = arguments["pbp_acceptance_target_flag"]
    if name == "register_discount_card":
        request = arguments["request"]
        forms[-1]["jrnyCnt"] = len(request.sections)
        for index, section in enumerate(request.sections, 1):
            for wire, attr in (
                ("jrnyTpCd", "journey_type_code"),
                ("runDt", "run_date"),
                ("trnNo", "train_no"),
                ("dptRsStnCd", "departure_station_code"),
                ("arvRsStnCd", "arrival_station_code"),
            ):
                forms[-1][f"{wire}_{index}"] = getattr(section, attr)
        for index, person in enumerate(request.additional_users, 1):
            for wire, attr in (("custMgNo", "customer_no"), ("apdCustName", "name"), ("apdCustTeln", "phone")):
                forms[-1][f"{wire}_{index}"] = getattr(person, attr)
        if request.additional_users:
            forms[-1]["apdUsrCnt"] = len(request.additional_users)
    if name == "retrieve_delivered_ticket" and not arguments["ticket"].journeys:
        raise E.KorailProtocolError("Ticket retrieval requires the first journey")
    if name == "register_self_checkin" and not isinstance(arguments["seat"], REGISTRY["SelfCheckInSeat"]):
        raise E.KorailProtocolError("Check-in requires a seat value object")
    if name == "get_common_code":
        code = arguments["code"]
        forms[-1]["code"] = [code] if isinstance(code, str) else list(code)
        forms[-1].update(
            deviceWidth=client.config.device_width,
            deviceHeight=client.config.device_height,
            OSVersion=client.config.android_sdk_int,
        )
    if name == "get_price_fare_quote":
        legs = arguments["request"].legs
        if not 1 <= len(legs) <= 2:
            raise E.KorailProtocolError("Fare quote requires one or two legs")
        forms[-1].update(trnCnt=len(legs), chtnDvCd="2" if len(legs) == 2 else "1")
        columns = {
            "dptRsStnCd": "departure_station_code",
            "arvRsStnCd": "arrival_station_code",
            "runDt": "run_date",
            "trnNo": "train_no",
            "gdNo": "goods_no",
            "rqSeatAttCd": "requested_seat_attribute_code",
            "trnGpCd": "train_group_code",
            "stlbTrnClsfCd": "train_class_code",
        }
        for wire, attr in columns.items():
            values = [getattr(leg, attr) or "" for leg in legs]
            if wire == "trnNo":
                values = [value.zfill(5) for value in values]
            forms[-1][wire] = ",".join(values)
    if name == "get_maas_menu_list":
        if arguments.get("pnr_no"):
            forms[-1].pop("timeStamp", None)
            forms[-1]["pnrNo"] = arguments["pnr_no"]
        tickets = arguments.get("ticket_return_numbers")
        if tickets is not None:
            forms[-1].pop("timeStamp", None)
            forms[-1]["tkRetNo"] = list(tickets)
    if name == "get_ticket_list":
        forms[-1]["h_page_no"] = number(arguments["page_no"], "Page number", minimum=1)
        forms[-1]["txtIndex"] = arguments["mode"]
        if arguments["boarding_date_from"]:
            forms[-1]["h_abrd_dt_from"] = arguments["boarding_date_from"]
        if arguments["boarding_date_to"]:
            forms[-1]["h_abrd_dt_to"] = arguments["boarding_date_to"]
        if client.config.advertising_id:
            forms[-1]["txtDeviceId"] = client.config.advertising_id
        order = "Device Version AppVersion Key lang txtIndex h_abrd_dt_from h_abrd_dt_to txtDeviceId hiduserYn h_page_no".split()
        forms[-1] = {key: forms[-1][key] for key in order if key in forms[-1]}
    if name == "recalculate_price":
        request = arguments["request"]
        if not request.rows:
            raise E.KorailProtocolError("Price recalculation requires passenger rows")
        field_map = {
            "psg_tp_dv_cd": "passenger_type_code",
            "hidDcntKndCd": "requested_discount_code",
            "dcnt_knd_cd1": "discount_kind_code",
            "hidDscpNo": "certificate_no",
            "psrm_cl_cd": "room_class_code",
            "hidFmlyNo": "family_sequence_no",
        }
        forms[-1]["txtPsgGridcnt"] = len(request.rows)
        for wire, field in field_map.items():
            forms[-1][wire] = [getattr(row, field) for row in request.rows]
        if request.non_member_no:
            forms[-1]["hiduserYn"] = "N"
    if name == "get_seat_inventory":
        arrow = forms[-1].pop("isArrow", None)
        if arrow is not None:
            forms[-1]["isArrow"] = arrow
    if name == "get_merge_seats_inquiry":
        order = "Device Version AppVersion Key lang abrdDt runDt trnNo dptRsStnNm arvRsStnNm selRsStnNm psrmClCd seatAttCd totPsgNum".split()
        forms[-1] = {key: forms[-1][key] for key in order if key in forms[-1]}
    if name == "get_refund_commission":
        order = "h_orgtk_ret_sale_dt h_orgtk_wct_no h_orgtk_sale_sqno h_orgtk_ret_pwd h_comp_nm h_comp_cert_no Device Version AppVersion Key lang".split()
        forms[-1] = {key: forms[-1][key] for key in order if key in forms[-1]}
    for form in forms:
        for key, item in form.items():
            if (
                re.fullmatch(r"(?:trnNo|txtTrnNo[0-9]*)", key)
                and isinstance(item, str)
                and item.isascii()
                and item.isdigit()
            ):
                form[key] = item.zfill(5)
    return steps, forms


def finish(client, name, arguments, result):
    if name == "recalculate_price" and arguments.get("add_to_cart"):
        from korail_api.protocol.codec import decode

        try:
            added = client.add_to_cart(REGISTRY["CartAddRequest"](result.pnr_no))
        except E.KorailAppError as error:
            added = decode("CartAddResponse", error.raw)
        result = dataclasses.replace(result, cart_addition=added)
    if name == "get_reservation_hold":
        raw = result.raw
        if result.str_result != "SUCC" or result.pnr_no != arguments["pnr_no"]:
            raise E.KorailProtocolError("Reservation detail does not match the requested reservation")
        text(result.window_no, "Payment window number")
        if "h_payment_flg" in raw and result.payment_flag != "Y":
            raise E.KorailProtocolError("Reservation detail is not payable")
        if number(result.journey_count, "Journey count", minimum=1) != len(result.journeys):
            raise E.KorailProtocolError("Reservation journey count does not match its rows")
        total = 0
        for journey in result.journeys:
            seats = journey.raw.get("seat_infos", {}).get("seat_info")
            if not isinstance(seats, list) or not seats:
                raise E.KorailProtocolError("Each reservation journey must contain seat_infos rows")
            for seat in seats:
                amount = number(seat.get("h_rcvd_amt"), "Seat settlement amount")
                if amount == 0 and not (seat.get("h_seat_no") or "").strip():
                    raise E.KorailProtocolError("An unassigned zero-amount seat cannot be used for payment")
                total += amount
        if "h_tot_rcvd_amt" in raw and number(raw["h_tot_rcvd_amt"], "Total settlement amount") != total:
            raise E.KorailProtocolError("Reservation settlement amount does not match seat amounts")
        number(result.received_amount, "Settlement amount", minimum=1)
        result = dataclasses.replace(result, received_amount=str(total))
    if name.startswith("reserve") and arguments.get("job_type") == KorailReservationJobType.STANDBY:
        result = dataclasses.replace(result, payable=False)
    return result
