from __future__ import annotations

import collections.abc
import typing
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Literal, Mapping, Self, Sequence

import httpx

from korail_py_sdk.api.client import KorailClient
from korail_py_sdk.models.records import *

class StationResource:
    def __init__(self, client: KorailClient) -> None: ...
    def all(self, *, refresh: bool = ...) -> tuple[KorailStation, ...]: ...
    def find(self, reference: str) -> KorailStation | None: ...
    def names(self) -> set[str]: ...
    def ensure_exists(self, *references: str) -> None: ...

class TrainResource:
    def __init__(self, client: KorailClient, stations: StationResource, *, validate_stations: bool) -> None: ...
    def search(
        self,
        departure: str,
        arrival: str,
        *,
        depart_after: datetime | None = ...,
        passengers: KorailPassengerCounts | None = ...,
        train_group_code: str = ...,
        include_srt: bool = ...,
        include_nearby_stations: bool = ...,
        peak_season: bool = ...,
        continuation: TrainSearchContinuation | None = ...,
        include_no_seats: bool = ...,
        include_waiting_list: bool = ...,
    ) -> TrainSearchResult: ...

class ReservationResource:
    def __init__(self, client: KorailClient) -> None: ...
    def create(
        self,
        train: TrainSummary,
        *,
        passengers: KorailPassengerCounts | None = ...,
        seat_class: KorailSeatClass | None = ...,
        job_type: KorailReservationJobType = ...,
        option: KorailReserveOption | None = ...,
    ) -> ReservationHoldResponse: ...
    def find(self, pnr_no: str) -> ReservationHoldResponse: ...
    def detail(self, hold: ReservationHoldResponse | str) -> TicketReservationDetailResponse: ...
    def all(self) -> ReservationHistoryResponse: ...
    def cancel(self, hold: ReservationHoldResponse) -> BaseKorailResponse: ...
    def pay(self, hold: ReservationHoldResponse, card: CardPayment) -> ReservationPaymentResponse: ...

class TicketResource:
    def __init__(self, client: KorailClient) -> None: ...
    def all(self, *, page_no: int = ...) -> TicketListResponse: ...
    def refund_fee(self, ticket: OriginalTicketReference) -> RefundCommissionResponse: ...
    def refund(self, ticket: PaidTicket, *, commission: RefundCommissionResponse) -> RefundTicketResponse: ...

class Korail:
    client: KorailClient
    stations: StationResource
    trains: TrainResource
    reservations: ReservationResource
    tickets: TicketResource
    def __init__(
        self,
        config: KorailConfig | None = ...,
        *,
        transport: httpx.BaseTransport | None = ...,
        validate_stations: bool = ...,
    ) -> None: ...
    @classmethod
    def logged_in(
        cls,
        member_no: str,
        password: str,
        *,
        config: KorailConfig | None = ...,
        transport: httpx.BaseTransport | None = ...,
        validate_stations: bool = ...,
    ) -> Korail: ...
    def __enter__(self) -> Korail: ...
    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None: ...
    def login(self, member_no: str, password: str) -> KorailSession: ...
    def logout(self) -> None: ...
    def close(self) -> None: ...
