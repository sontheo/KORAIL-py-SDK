"""Card settlement validation and fields."""

from __future__ import annotations

import re
from datetime import datetime

from korail_py_sdk.models import errors as E
from korail_py_sdk.services.validation import number, text


def _payment(arguments, form):
    hold, card = arguments["hold"], arguments["card"]
    if hold.str_result != "SUCC" or not hold.payable:
        raise E.KorailProtocolError("Payment requires a successful hold; standby holds cannot be paid")
    text(hold.pnr_no, "Reservation number")
    text(hold.window_no, "Payment window number")
    if number(hold.received_amount, "Settlement amount") == 0:
        raise E.KorailProtocolError("Cannot card-pay a zero-amount hold")
    form["hidTmpJobSqno1"] = (
        hold.temporary_job_sequence_1 if hold.temporary_job_sequence_1 not in (None, "") else "000000"
    )
    form["hidTmpJobSqno2"] = (
        hold.temporary_job_sequence_2 if hold.temporary_job_sequence_2 not in (None, "") else "000000"
    )
    for label, val, pattern in [
        ("Card number", card.card_number, r"[0-9]{13,16}"),
        ("Card password", card.card_password, r"[0-9]{2}"),
        ("Card expiry", card.card_expire, r"[0-9]{4}"),
        ("Installment", card.installment, r"[0-9]{1,2}"),
        ("Authentication value", card.birthday, r"[0-9]{6}" if card.card_type == "J" else r"[0-9]{10}"),
    ]:
        if not isinstance(val, str) or re.fullmatch(pattern, val) is None:
            raise E.KorailProtocolError(f"Invalid {label.lower()}")
    month = int(card.card_expire[2:])
    if not 1 <= month <= 12:
        raise E.KorailProtocolError("Invalid card expiry month")
    if 200000 + int(card.card_expire) < datetime.now().year * 100 + datetime.now().month:
        raise E.KorailProtocolError("Card has expired")
    form["hidAthnDvCd1"] = card.card_type
    form["hidMnsStlAmt1"] = hold.received_amount
    if hold.journeys:
        form["hidRsvChgNo"] = hold.journeys[0].reservation_change_no or "000"
