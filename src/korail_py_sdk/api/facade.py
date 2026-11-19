"""Convenience resources that keep every transaction an explicit caller action."""

from dataclasses import replace
from datetime import datetime
from zoneinfo import ZoneInfo

from korail_py_sdk.api.client import KorailClient
from korail_py_sdk.models import errors as E
from korail_py_sdk.models.records import (
    KorailPassengerCounts,
    KorailReservationJobType,
    KorailReserveOption,
    KorailSeatClass,
    TicketReservationDetailRequest,
    TrainSearchQuery,
)

KST = ZoneInfo("Asia/Seoul")


class StationResource:
    def __init__(self, client):
        self.client = client
        self._stations = None
        self._index = {}

    def all(self, *, refresh=False):
        if self._stations is None or refresh:
            rows = self.client.get_station_data().stations
            index = {}
            for station in rows:
                index[station.code] = station
                index[station.name] = station
            self._stations, self._index = tuple(rows), index
        return self._stations

    def find(self, reference):
        self.all()
        return self._index.get(reference)

    def names(self):
        return {s.name for s in self.all()}

    def ensure_exists(self, *references):
        for reference in references:
            if self.find(reference) is None:
                raise ValueError(f"역을 찾을 수 없습니다: {reference}")


class TrainResource:
    def __init__(self, client, stations, *, validate_stations=True):
        self.client, self.stations, self.validate_stations = client, stations, validate_stations

    def search(
        self,
        departure,
        arrival,
        *,
        depart_after=None,
        passengers=None,
        train_group_code="109",
        include_srt=False,
        include_nearby_stations=False,
        peak_season=False,
        continuation=None,
        include_no_seats=True,
        include_waiting_list=False,
    ):
        if type(include_no_seats) is not bool or type(include_waiting_list) is not bool:
            raise TypeError("Search filters must be bool")
        now = datetime.now(KST)
        moment = depart_after or now
        moment = moment.replace(tzinfo=KST) if moment.tzinfo is None else moment.astimezone(KST)
        if moment.date() < now.date():
            raise ValueError("지난 출발 날짜는 조회할 수 없습니다")
        if self.validate_stations:
            self.stations.ensure_exists(departure, arrival)
        p = passengers or KorailPassengerCounts()
        query = TrainSearchQuery(
            departure,
            arrival,
            moment.strftime("%Y%m%d"),
            moment.strftime("%H%M%S"),
            passengers=p.adult,
            train_group_code=train_group_code,
            include_srt=include_srt,
            child_passengers=p.child,
            senior_passengers=p.senior,
            high_disability_passengers=p.severe_disability,
            low_disability_passengers=p.mild_disability,
            teenager_passengers=p.teenager,
            infant_passengers=p.infant,
            guide_dog_passengers=p.guide_dog,
            include_nearby_stations=include_nearby_stations,
        )
        result = self.client.search_trains(query, continuation=continuation, peak_season=peak_season)
        if include_no_seats:
            return result
        trains = [t for t in result.trains if t.has_seat() or (include_waiting_list and t.has_waiting_list())]
        return replace(result, trains=trains, unfiltered_trains=result.trains)


class ReservationResource:
    def __init__(self, client):
        self.client = client

    def all(self):
        return self.client.get_reservation_history()

    def create(
        self,
        train,
        *,
        passengers=None,
        seat_class=None,
        job_type=KorailReservationJobType.IMMEDIATE,
        option=None,
    ):
        if seat_class is not None and option is not None:
            raise ValueError("Choose a cabin or a cabin preference")
        if option is not None:
            if job_type != KorailReservationJobType.IMMEDIATE:
                raise ValueError("Cabin preferences require an immediate reservation")
            if not isinstance(option, KorailReserveOption):
                raise TypeError("Unknown cabin preference")
            ordered = [KorailSeatClass.GENERAL, KorailSeatClass.SPECIAL]
            if option in {KorailReserveOption.SPECIAL_ONLY, KorailReserveOption.SPECIAL_FIRST}:
                ordered.reverse()
            if option in {KorailReserveOption.GENERAL_ONLY, KorailReserveOption.SPECIAL_ONLY}:
                ordered = ordered[:1]
            seat_class = None
            for cabin in ordered:
                if train.has_general_seat() if cabin == KorailSeatClass.GENERAL else train.has_special_seat():
                    seat_class = cabin
                    break
            if seat_class is None:
                raise E.KorailProtocolError("Requested cabin has no available seat")
        return self.client.reserve(
            train, passengers=passengers, seat_class=seat_class or KorailSeatClass.GENERAL, job_type=job_type
        )

    def detail(self, hold):
        return self.client.get_ticket_reservation_detail(
            TicketReservationDetailRequest(hold if isinstance(hold, str) else hold.pnr_no)
        )

    def find(self, pnr_no):
        return self.client.get_reservation_hold(pnr_no)

    def cancel(self, hold):
        return self.client.cancel_unpaid_hold(hold)

    def pay(self, hold, card):
        return self.client.pay_with_card(hold, card)


class TicketResource:
    def __init__(self, client):
        self.client = client

    def all(self, *, page_no=1):
        return self.client.get_ticket_list(page_no)

    def refund_fee(self, ticket):
        return self.client.get_refund_commission(ticket)

    def refund(self, ticket, *, commission):
        return self.client.refund(ticket, commission=commission)


class Korail:
    def __init__(self, config=None, *, transport=None, validate_stations=True):
        self.client = KorailClient(config, transport=transport)
        self.stations = StationResource(self.client)
        self.trains = TrainResource(self.client, self.stations, validate_stations=validate_stations)
        self.reservations = ReservationResource(self.client)
        self.tickets = TicketResource(self.client)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.client._close(exc[1] if len(exc) > 1 else None)

    @classmethod
    def logged_in(cls, member_no, password, config=None, *, transport=None, validate_stations=True):
        result = cls(config, transport=transport, validate_stations=validate_stations)
        try:
            result.login(member_no, password)
        except BaseException as error:
            result.client._close(error)
            raise
        return result

    def close(self):
        self.client.close()

    def login(self, member_no, password):
        return self.client.login(member_no, password)

    def logout(self):
        self.client.logout()
