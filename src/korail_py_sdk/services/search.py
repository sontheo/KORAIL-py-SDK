"""Search validation and continuation fields."""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache

from korail_py_sdk.models import errors as E


@lru_cache(maxsize=1024)
def _departure(date, clock):
    try:
        datetime.strptime(date + clock, "%Y%m%d%H%M%S")
    except (ValueError, TypeError) as error:
        raise E.KorailProtocolError("Invalid search departure date or time") from error


def _search(arguments, form):
    query = arguments["query"]
    if not isinstance(query.departure_date, str) or not isinstance(query.departure_time, str):
        raise E.KorailProtocolError("Invalid search departure date or time")
    _departure(query.departure_date, query.departure_time)
    counts = [
        query.passengers,
        query.child_passengers,
        query.senior_passengers,
        query.high_disability_passengers,
        query.low_disability_passengers,
        query.teenager_passengers,
        query.infant_passengers,
        query.guide_dog_passengers,
    ]
    if any(type(n) is not int or n < 0 for n in counts) or sum(counts) < 1:
        raise E.KorailProtocolError("Search requires a positive passenger count")
    form["txtPsgFlg_1"] = query.passengers + query.teenager_passengers + query.guide_dog_passengers
    form["txtPsgFlg_2"] = query.child_passengers + query.infant_passengers
    cursor = arguments.get("continuation")
    if cursor is not None:
        form.update(
            qryStNo=cursor.query_station_no,
            qryStTrnNo=cursor.query_train_no,
            qryStTrnNo2=cursor.query_train_no2,
        )
    if query.connection_station_codes:
        form["chtnCnt"] = len(query.connection_station_codes)
        for index, code in enumerate(query.connection_station_codes, 1):
            form[f"chtnRsStnCd{index}"] = code
    if query.connection_train_group_code:
        form["trnGpCnt"] = "1"
        form["trnGpCd1"] = query.connection_train_group_code
