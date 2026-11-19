from __future__ import annotations

import collections.abc
import typing
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Literal, Mapping, Self, Sequence

import httpx

class KorailReservationJobType(str, Enum):
    IMMEDIATE = "1101"
    STANDBY = "1102"
    SEAT_DESIGNATED = "1103"
    MERGE_STANDING = "1202"

class KorailReserveOption(str, Enum):
    GENERAL_FIRST = "GENERAL_FIRST"
    GENERAL_ONLY = "GENERAL_ONLY"
    SPECIAL_FIRST = "SPECIAL_FIRST"
    SPECIAL_ONLY = "SPECIAL_ONLY"

class KorailSeatClass(str, Enum):
    GENERAL = "1"
    SPECIAL = "2"

@dataclass(frozen=True)
class AppVersionInfo(object):
    message: str | None
    new_version: str | None
    store_url: str | None
    def __init__(
        self, message: str | None = ..., new_version: str | None = ..., store_url: str | None = ...
    ) -> None: ...

@dataclass(frozen=True)
class BaseKorailResponse(object):
    h_msg_cd: str | None
    h_msg_txt: str | None
    str_result: str | None
    raw: collections.abc.Mapping[str, object]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...
    @property
    def display_message(self) -> str | None: ...
    @classmethod
    def from_raw(cls, raw: object) -> typing.Self: ...

@dataclass(frozen=True)
class CartAddRequest(object):
    pnr_no: str
    def __init__(self, pnr_no: str) -> None: ...

@dataclass(frozen=True)
class CartAddResponse(BaseKorailResponse):
    discount_additions: tuple[CartDiscountAddition, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        discount_additions: tuple[CartDiscountAddition, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CartDiscountAddition(object):
    passenger_sequence_no: str | None
    duty_reference_recognition_division_code: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        passenger_sequence_no: str | None = ...,
        duty_reference_recognition_division_code: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CartItem(object):
    service_code: str | None
    provider_name: str | None
    product_name: str | None
    item_type: str | None
    departure_date: str | None
    received_amount: str | None
    reservation_received_date: str | None
    ticket_count: str | None
    usage_start_date: str | None
    usage_start_time: str | None
    usage_close_time: str | None
    partner_reservation_no: str | None
    pnr_no: str | None
    lump_sum_target_no: str | None
    customer_no: str | None
    virtual_reservation_no: str | None
    raw: Mapping[str, object]
    item_type_code: str | None
    provider_id: str | None
    item_sequence: str | None
    journey_sequence: str | None
    journey_type_code: str | None
    usage_close_date: str | None
    settlement_limit_time: str | None
    settlement_extension_transaction_no: str | None
    settlement_means_allow_value: str | None
    field_settlement_division: str | None
    supervising_station_code: str | None
    filler: str | None
    def __init__(
        self,
        service_code: str | None = ...,
        provider_name: str | None = ...,
        product_name: str | None = ...,
        item_type: str | None = ...,
        departure_date: str | None = ...,
        received_amount: str | None = ...,
        reservation_received_date: str | None = ...,
        ticket_count: str | None = ...,
        usage_start_date: str | None = ...,
        usage_start_time: str | None = ...,
        usage_close_time: str | None = ...,
        partner_reservation_no: str | None = ...,
        pnr_no: str | None = ...,
        lump_sum_target_no: str | None = ...,
        customer_no: str | None = ...,
        virtual_reservation_no: str | None = ...,
        raw: Mapping[str, object] = ...,
        item_type_code: str | None = ...,
        provider_id: str | None = ...,
        item_sequence: str | None = ...,
        journey_sequence: str | None = ...,
        journey_type_code: str | None = ...,
        usage_close_date: str | None = ...,
        settlement_limit_time: str | None = ...,
        settlement_extension_transaction_no: str | None = ...,
        settlement_means_allow_value: str | None = ...,
        field_settlement_division: str | None = ...,
        supervising_station_code: str | None = ...,
        filler: str | None = ...,
    ) -> None: ...
    @property
    def usage_window(self) -> tuple[str | None, str | None, str | None]: ...

@dataclass(frozen=True)
class CartListResponse(BaseKorailResponse):
    items: tuple[CartItem, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[CartItem, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CommuterKindMenuResponse(BaseKorailResponse):
    after_day: str | None
    agreement: str | None
    information: str | None
    title: str | None
    pass_data: PassMenuData | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        after_day: str | None = ...,
        agreement: str | None = ...,
        information: str | None = ...,
        title: str | None = ...,
        pass_data: PassMenuData | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CommuterInfoResponse(BaseKorailResponse):
    additional_service_goods_flag: str | None
    companion_flag: str | None
    commuter_kind_code: str | None
    commuter_usage_age_code: str | None
    menu_id: str | None
    popup_message: str | None
    promotion_message: str | None
    promotion_url: str | None
    seat_attribute_code: str | None
    available_passenger_count_from: int | None
    available_passenger_count_to: int | None
    passenger_options: tuple[CommuterPassengerOption, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        additional_service_goods_flag: str | None = ...,
        companion_flag: str | None = ...,
        commuter_kind_code: str | None = ...,
        commuter_usage_age_code: str | None = ...,
        menu_id: str | None = ...,
        popup_message: str | None = ...,
        promotion_message: str | None = ...,
        promotion_url: str | None = ...,
        seat_attribute_code: str | None = ...,
        available_passenger_count_from: int | None = ...,
        available_passenger_count_to: int | None = ...,
        passenger_options: tuple[CommuterPassengerOption, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CommuterInitialRequest(object):
    pass_data: PassMenuData
    def __init__(self, pass_data: PassMenuData) -> None: ...

@dataclass(frozen=True)
class CommuterPassengerOption(object):
    commuter_usage_age_code: str | None
    common_code_name: str | None
    customer_age_from: int | None
    customer_age_to: int | None
    passenger_count_from: int | None
    passenger_count_to: int | None
    raw: Mapping[str, object]
    def __init__(
        self,
        commuter_usage_age_code: str | None = ...,
        common_code_name: str | None = ...,
        customer_age_from: int | None = ...,
        customer_age_to: int | None = ...,
        passenger_count_from: int | None = ...,
        passenger_count_to: int | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CommuterPassengerRequest(object):
    pass_data: PassMenuData
    source: CommuterInfoResponse
    passenger_counts: tuple[int, ...]
    def __init__(self) -> None: ...
    @classmethod
    def from_response(
        cls, pass_data: PassMenuData, source: CommuterInfoResponse, passenger_counts: tuple[int, ...]
    ) -> CommuterPassengerRequest: ...

@dataclass(frozen=True)
class CommuterTicketInquiryRequest(object):
    original_ticket: OriginalTicketReference
    inquiry_type: Literal["0", "1"]
    def __init__(
        self, original_ticket: OriginalTicketReference, inquiry_type: Literal["0", "1"] = ...
    ) -> None: ...

@dataclass(frozen=True)
class CrewRequestListResponse(BaseKorailResponse):
    items: tuple[CrewRequestOption, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[CrewRequestOption, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CrewRequestOption(object):
    message_code: str | None
    content: str | None
    raw: Mapping[str, object]
    def __init__(
        self, message_code: str | None = ..., content: str | None = ..., raw: Mapping[str, object] = ...
    ) -> None: ...

@dataclass(frozen=True)
class CustomerTripInfo(object):
    additional_seat_attribute_code: str | None
    adult_disabled_person_count: str | None
    adult_count: str | None
    arrival_station_code: str | None
    arrival_station_name: str | None
    baby_accompanying_person_count: str | None
    changed_at: str | None
    changed_by: str | None
    child_count: str | None
    child_disabled_person_count: str | None
    customer_management_no: str | None
    day_code: str | None
    direction_seat_attribute_group_code: str | None
    direct_transfer_division_code: str | None
    departure_station_code: str | None
    departure_station_name: str | None
    early_train_departure_time: str | None
    elderly_person_count: str | None
    included_flag: str | None
    job_start_hour: str | None
    location_seat_attribute_group_code: str | None
    media_division_code: str | None
    room_class_code: str | None
    passenger_total: str | None
    registered_at: str | None
    registration_sequence: str | None
    registered_by: str | None
    trip_day_no: str | None
    train_classification_code: str | None
    train_connection_flag: str | None
    train_group_code: str | None
    usage_day_no: str | None
    goods_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        additional_seat_attribute_code: str | None = ...,
        adult_disabled_person_count: str | None = ...,
        adult_count: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_station_name: str | None = ...,
        baby_accompanying_person_count: str | None = ...,
        changed_at: str | None = ...,
        changed_by: str | None = ...,
        child_count: str | None = ...,
        child_disabled_person_count: str | None = ...,
        customer_management_no: str | None = ...,
        day_code: str | None = ...,
        direction_seat_attribute_group_code: str | None = ...,
        direct_transfer_division_code: str | None = ...,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        early_train_departure_time: str | None = ...,
        elderly_person_count: str | None = ...,
        included_flag: str | None = ...,
        job_start_hour: str | None = ...,
        location_seat_attribute_group_code: str | None = ...,
        media_division_code: str | None = ...,
        room_class_code: str | None = ...,
        passenger_total: str | None = ...,
        registered_at: str | None = ...,
        registration_sequence: str | None = ...,
        registered_by: str | None = ...,
        trip_day_no: str | None = ...,
        train_classification_code: str | None = ...,
        train_connection_flag: str | None = ...,
        train_group_code: str | None = ...,
        usage_day_no: str | None = ...,
        goods_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CustomerTripInfoResponse(BaseKorailResponse):
    trips: tuple[CustomerTripInfo, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        trips: tuple[CustomerTripInfo, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DelayCertificateResponse(BaseKorailResponse):
    delays: tuple[DelayCertificateRow, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        delays: tuple[DelayCertificateRow, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DelayCertificateRow(object):
    run_day: str
    train_no: str
    departure_station_code: str
    arrival_station_code: str
    arrival_station_name: str
    delay_arrival_flag: str
    delay_minutes: str
    run_date: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        run_day: str,
        train_no: str,
        departure_station_code: str,
        arrival_station_code: str,
        arrival_station_name: str,
        delay_arrival_flag: str,
        delay_minutes: str,
        run_date: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DelayReturnReceiptResponse(BaseKorailResponse):
    return_date: str | None
    payment_method_name: str | None
    return_amount: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        return_date: str | None = ...,
        payment_method_name: str | None = ...,
        return_amount: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DeliveredTicketRetrievalResponse(BaseKorailResponse):
    process_flags: tuple[str, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        process_flags: tuple[str, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DynapathConfig(object):
    enabled: bool
    token_provider: DynapathTokenProvider | None
    token_settings: DynapathTokenSettings | None
    timestamp_ms_provider: TimestampMsProvider | None
    random_text_provider: RandomTextProvider | None
    header_name: str
    allowlist_paths: frozenset[str]
    device_name: str
    os_version: str
    def __init__(
        self,
        enabled: bool = ...,
        token_provider: DynapathTokenProvider | None = ...,
        token_settings: DynapathTokenSettings | None = ...,
        timestamp_ms_provider: TimestampMsProvider | None = ...,
        random_text_provider: RandomTextProvider | None = ...,
        header_name: str = ...,
        allowlist_paths: frozenset[str] = ...,
        device_name: str = ...,
        os_version: str = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DynapathRequestContext(object):
    method: str
    path: str
    url: str
    device: str
    version: str
    key: str
    user_agent: str
    device_name: str
    os_version: str
    def __init__(
        self,
        method: str,
        path: str,
        url: str,
        device: str,
        version: str,
        key: str,
        user_agent: str,
        device_name: str,
        os_version: str,
    ) -> None: ...

@dataclass(frozen=True)
class DynapathTokenSettings(object):
    device_id: str
    as_value: str
    app_start_ts: str
    os_version: str
    device_model: str
    app_id: str
    os_type: str
    sdk_version: str
    table_index: int
    table: str
    i8: int
    i9: int
    i10: int
    secure_user: bool
    debug: bool
    emulator: bool
    hooked: bool
    def __init__(
        self,
        device_id: str,
        as_value: str,
        app_start_ts: str,
        os_version: str,
        device_model: str,
        app_id: str = ...,
        os_type: str = ...,
        sdk_version: str = ...,
        table_index: int = ...,
        table: str = ...,
        i8: int = ...,
        i9: int = ...,
        i10: int = ...,
        secure_user: bool = ...,
        debug: bool = ...,
        emulator: bool = ...,
        hooked: bool = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DelayDiscountTicket(object):
    fare: str | None
    original_sale_date: str | None
    window_no: str | None
    sale_sequence: str | None
    return_password: str | None
    ticket_sequence: str | None
    ticket_kind_code: str | None
    original_ticket_sale_date: str | None
    received_amount: str | None
    train_class_code: str | None
    room_class_code: str | None
    train_no: str | None
    departure_station_code: str | None
    departure_date: str | None
    departure_time: str | None
    arrival_station_code: str | None
    arrival_date: str | None
    arrival_time: str | None
    ticket_status_code: str | None
    ticket_status_name: str | None
    buyer_name: str | None
    passenger_name: str | None
    page_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        fare: str | None = ...,
        original_sale_date: str | None = ...,
        window_no: str | None = ...,
        sale_sequence: str | None = ...,
        return_password: str | None = ...,
        ticket_sequence: str | None = ...,
        ticket_kind_code: str | None = ...,
        original_ticket_sale_date: str | None = ...,
        received_amount: str | None = ...,
        train_class_code: str | None = ...,
        room_class_code: str | None = ...,
        train_no: str | None = ...,
        departure_station_code: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        ticket_status_code: str | None = ...,
        ticket_status_name: str | None = ...,
        buyer_name: str | None = ...,
        passenger_name: str | None = ...,
        page_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DelayDiscountTicketListResponse(BaseKorailResponse):
    items: tuple[DelayDiscountTicket, ...]
    current_page: str | None
    total_pages: str | None
    total_count: str | None
    row_count: str | None
    last_page_flag: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[DelayDiscountTicket, ...] = ...,
        current_page: str | None = ...,
        total_pages: str | None = ...,
        total_count: str | None = ...,
        row_count: str | None = ...,
        last_page_flag: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DeliveryRecipientResponse(BaseKorailResponse):
    acceptance_customer_management_no: str
    acceptance_customer_name: str
    acceptance_customer_phone: str
    member_card_no: str
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        *,
        acceptance_customer_management_no: str,
        acceptance_customer_name: str,
        acceptance_customer_phone: str,
        member_card_no: str,
    ) -> None: ...

@dataclass(frozen=True)
class DepositBank(object):
    code: str | None
    display_name: str | None
    raw: Mapping[str, object]
    def __init__(
        self, code: str | None = ..., display_name: str | None = ..., raw: Mapping[str, object] = ...
    ) -> None: ...

@dataclass(frozen=True)
class DepositBankListResponse(BaseKorailResponse):
    items: tuple[DepositBank, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[DepositBank, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardScheduleRequest(object):
    card_kind_management_no: str
    departure_station_name: str
    arrival_station_name: str
    departure_date: str
    card_kind_code: str
    usable_trip_count: str
    usage_period_days: str | None
    page_no: str | None
    departure_time: str
    train_group_code: str
    direct_transfer_division_code: str
    def __init__(
        self,
        card_kind_management_no: str,
        departure_station_name: str,
        arrival_station_name: str,
        departure_date: str,
        card_kind_code: str = ...,
        usable_trip_count: str = ...,
        usage_period_days: str | None = ...,
        page_no: str | None = ...,
        departure_time: str = ...,
        train_group_code: str = ...,
        direct_transfer_division_code: str = ...,
    ) -> None: ...
    @classmethod
    def for_card(
        cls,
        card_kind_management_no: str,
        *,
        departure_station_name: str,
        arrival_station_name: str,
        departure_date: str,
        usable_trip_count: str = ...,
        usage_period_days: str | None = ...,
        page_no: str | None = ...,
    ) -> DiscountCardScheduleRequest: ...

@dataclass(frozen=True)
class DiscountCardAdditionalUser(object):
    customer_no: str
    name: str
    phone: str
    def __init__(self, customer_no: str, name: str, phone: str) -> None: ...

@dataclass(frozen=True)
class DiscountCardOnTicket(object):
    card_no: str | None
    term_extension_possible_flag: str | None
    sections: tuple[DiscountCardSection, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        card_no: str | None = ...,
        term_extension_possible_flag: str | None = ...,
        sections: tuple[DiscountCardSection, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardPurchaseRequest(object):
    card_kind_management_no: str
    customer_no: str
    validity_start_date: str
    usable_trip_count: str
    sections: tuple[DiscountCardSectionRequest, ...]
    additional_users: tuple[DiscountCardAdditionalUser, ...]
    def __init__(
        self,
        card_kind_management_no: str,
        customer_no: str,
        validity_start_date: str = ...,
        usable_trip_count: str = ...,
        sections: tuple[DiscountCardSectionRequest, ...] = ...,
        additional_users: tuple[DiscountCardAdditionalUser, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardPurchaseResponse(BaseKorailResponse):
    lump_settlement_target_no: str | None
    discount_card_settlement_target_no: str | None
    received_amount: str | None
    stx_amount: str | None
    taxt_supply_amount: str | None
    usable_trip_count: str | None
    validity_start_date: str | None
    validity_end_date: str | None
    registered_card_kind_management_no: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        lump_settlement_target_no: str | None = ...,
        discount_card_settlement_target_no: str | None = ...,
        received_amount: str | None = ...,
        stx_amount: str | None = ...,
        taxt_supply_amount: str | None = ...,
        usable_trip_count: str | None = ...,
        validity_start_date: str | None = ...,
        validity_end_date: str | None = ...,
        registered_card_kind_management_no: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardScheduleResponse(BaseKorailResponse):
    following_page_exists: str | None
    trains: tuple[DiscountCardScheduleTrain, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        following_page_exists: str | None = ...,
        trains: tuple[DiscountCardScheduleTrain, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardScheduleTrain(object):
    train_no: str | None
    train_group_code: str | None
    run_date: str | None
    departure_station_code: str | None
    departure_station_name: str | None
    arrival_station_code: str | None
    arrival_station_name: str | None
    departure_station_order: str | None
    arrival_station_order: str | None
    departure_run_order: str | None
    arrival_run_order: str | None
    transfer_train_order_no: str | None
    price_class_code: str | None
    settlement_car_type_code: str | None
    settlement_train_class_code: str | None
    commuter_price: str | None
    direct_transfer_division_code: str | None
    detour_code: str | None
    detour_name: str | None
    route_code: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        train_no: str | None = ...,
        train_group_code: str | None = ...,
        run_date: str | None = ...,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_station_name: str | None = ...,
        departure_station_order: str | None = ...,
        arrival_station_order: str | None = ...,
        departure_run_order: str | None = ...,
        arrival_run_order: str | None = ...,
        transfer_train_order_no: str | None = ...,
        price_class_code: str | None = ...,
        settlement_car_type_code: str | None = ...,
        settlement_train_class_code: str | None = ...,
        commuter_price: str | None = ...,
        direct_transfer_division_code: str | None = ...,
        detour_code: str | None = ...,
        detour_name: str | None = ...,
        route_code: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardSection(object):
    departure_station_name: str | None
    arrival_station_name: str | None
    journey_sequence: str | None
    journey_type_code: str | None
    train_group_code: str | None
    detour_division_name: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        departure_station_name: str | None = ...,
        arrival_station_name: str | None = ...,
        journey_sequence: str | None = ...,
        journey_type_code: str | None = ...,
        train_group_code: str | None = ...,
        detour_division_name: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardSectionRequest(object):
    run_date: str
    train_no: str
    departure_station_code: str
    arrival_station_code: str
    journey_type_code: str
    def __init__(
        self,
        run_date: str,
        train_no: str,
        departure_station_code: str,
        arrival_station_code: str,
        journey_type_code: str = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardTicket(object):
    sale_window_no: str
    sale_date: str
    sale_sequence: str
    return_password: str
    def __init__(
        self, sale_window_no: str, sale_date: str, sale_sequence: str, return_password: str
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardUsage(object):
    passenger_name: str | None
    departure_station_name: str | None
    arrival_station_name: str | None
    run_date: str | None
    additional_user_flag: str | None
    raw: Mapping[str, object]
    sale_date: str | None
    sale_sequence: str | None
    sale_window_no: str | None
    def __init__(
        self,
        passenger_name: str | None = ...,
        departure_station_name: str | None = ...,
        arrival_station_name: str | None = ...,
        run_date: str | None = ...,
        additional_user_flag: str | None = ...,
        raw: Mapping[str, object] = ...,
        sale_date: str | None = ...,
        sale_sequence: str | None = ...,
        sale_window_no: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCardUsageListResponse(BaseKorailResponse):
    items: tuple[DiscountCardUsage, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[DiscountCardUsage, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCoupon(object):
    guide: str | None
    start_date: str | None
    expiration_date: str | None
    discount_kind_code: str | None
    discount_rate_amount_division_code: str | None
    weekday_fare_discount: str | None
    weekday_price_discount: str | None
    weekend_fare_discount: str | None
    weekend_price_discount: str | None
    remarks: tuple[str, ...]
    coupon_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        guide: str | None = ...,
        start_date: str | None = ...,
        expiration_date: str | None = ...,
        discount_kind_code: str | None = ...,
        discount_rate_amount_division_code: str | None = ...,
        weekday_fare_discount: str | None = ...,
        weekday_price_discount: str | None = ...,
        weekend_fare_discount: str | None = ...,
        weekend_price_discount: str | None = ...,
        remarks: tuple[str, ...] = ...,
        coupon_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class DiscountCouponListResponse(BaseKorailResponse):
    items: tuple[DiscountCoupon, ...]
    current_page: int | None
    total_pages: int | None
    total_count: str | None
    row_count: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[DiscountCoupon, ...] = ...,
        current_page: int | None = ...,
        total_pages: int | None = ...,
        total_count: str | None = ...,
        row_count: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class FreeSeatCarRequest(object):
    run_date: str
    train_no: str
    departure_construction_order: str
    arrival_construction_order: str
    departure_run_order: str
    arrival_run_order: str
    def __init__(
        self,
        run_date: str,
        train_no: str,
        departure_construction_order: str,
        arrival_construction_order: str,
        departure_run_order: str,
        arrival_run_order: str,
    ) -> None: ...

@dataclass(frozen=True)
class FreeSeatCarResponse(BaseKorailResponse):
    title: str | None
    car_no: str | None
    content: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        title: str | None = ...,
        car_no: str | None = ...,
        content: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class GuideSeatConditionRequest(object):
    seat_attribute_code: str
    def __init__(self, seat_attribute_code: str) -> None: ...

@dataclass(frozen=True)
class GuideSeatConditionResponse(BaseKorailResponse):
    time_stamp: int | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        time_stamp: int | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class IntermediateStation(object):
    code: str | None
    name: str | None
    run_order: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        code: str | None = ...,
        name: str | None = ...,
        run_order: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class KorailConfig(object):
    base_url: str
    device: str
    version: str
    key: str
    timeout: float
    user_agent: str
    dynapath: DynapathConfig
    device_width: int
    device_height: int
    android_sdk_int: int
    advertising_id: str
    netfunnel_url: str
    netfunnel_timeout: float
    netfunnel_user_agent: str
    netfunnel_enabled: bool
    lang: str | None
    netfunnel_wait_limit: float | None
    netfunnel_actions: collections.abc.Mapping[str, str] | None
    disable_dynapath: bool
    app_version: str | None
    proxy: str | None
    dynapath_mode: typing.Literal["legacy", "v2-diagnostic", "v2-declaration"]
    transport_profile: typing.Literal["okhttp", "httpx"]
    def __init__(
        self,
        base_url: str = ...,
        device: str = ...,
        version: str = ...,
        key: str = ...,
        timeout: float = ...,
        user_agent: str = ...,
        dynapath: DynapathConfig = ...,
        device_width: int = ...,
        device_height: int = ...,
        android_sdk_int: int = ...,
        advertising_id: str = ...,
        netfunnel_url: str = ...,
        netfunnel_timeout: float = ...,
        netfunnel_user_agent: str = ...,
        netfunnel_enabled: bool = ...,
        lang: str | None = ...,
        netfunnel_wait_limit: float | None = ...,
        netfunnel_actions: collections.abc.Mapping[str, str] | None = ...,
        disable_dynapath: bool = ...,
        app_version: str | None = ...,
        proxy: str | None = ...,
        dynapath_mode: typing.Literal["legacy", "v2-diagnostic", "v2-declaration"] = ...,
        transport_profile: typing.Literal["okhttp", "httpx"] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class KorailDeviceProfile(object):
    device_id: str
    model: str
    android_release: str
    build_id: str
    android_sdk_int: int
    width: int
    height: int
    def __init__(
        self,
        device_id: str,
        model: str,
        android_release: str,
        build_id: str,
        android_sdk_int: int = ...,
        width: int = ...,
        height: int = ...,
    ) -> None: ...

@dataclass(frozen=True)
class KorailPassengerCounts(object):
    adult: int
    teenager: int
    child: int
    infant: int
    senior: int
    severe_disability: int
    mild_disability: int
    guide_dog: int
    def __init__(
        self,
        adult: int = ...,
        teenager: int = ...,
        child: int = ...,
        infant: int = ...,
        senior: int = ...,
        severe_disability: int = ...,
        mild_disability: int = ...,
        guide_dog: int = ...,
    ) -> None: ...
    @property
    def total(self) -> int: ...

@dataclass(frozen=True)
class KorailSeatAssignment(object):
    car_no: int
    seat_no: str
    def __init__(self, car_no: int, seat_no: str) -> None: ...
    @classmethod
    def from_inventory(cls, inventory: SeatInventoryResponse, seat: PhysicalSeat) -> KorailSeatAssignment: ...

@dataclass(frozen=True)
class KorailStation(object):
    code: str
    name: str
    longitude: str | None
    latitude: str | None
    raw: collections.abc.Mapping[str, object]
    group: str | None
    major: str | None
    popup_type: str | None
    popup_message: str | None
    popup_link_title: str | None
    popup_link_url: str | None
    area: str | None
    stop: str | None
    def __init__(
        self,
        code: str,
        name: str,
        longitude: str | None = ...,
        latitude: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        group: str | None = ...,
        major: str | None = ...,
        popup_type: str | None = ...,
        popup_message: str | None = ...,
        popup_link_title: str | None = ...,
        popup_link_url: str | None = ...,
        area: str | None = ...,
        stop: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class KorailSession(object):
    jsessionid: str | None
    member_no: str | None
    raw: collections.abc.Mapping[str, object]
    member_card_no: str | None
    customer_no: str | None
    def __init__(
        self,
        jsessionid: str | None = ...,
        member_no: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        member_card_no: str | None = ...,
        customer_no: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class LimousineSchedule(object):
    arrival_date: str | None
    arrival_station_code: str | None
    arrival_run_order: str | None
    arrival_time: str | None
    transfer_division_code: str | None
    departure_date: str | None
    departure_station_code: str | None
    departure_run_order: str | None
    departure_time: str | None
    general_remaining_seat_count: str | None
    delay_minutes: str | None
    free_remaining_seat_count: str | None
    standing_remaining_seat_count: str | None
    run_date: str | None
    special_remaining_seat_count: str | None
    train_class_code: str | None
    service_code: str | None
    train_no: str | None
    train_order_no: str | None
    yms_application_flag: str | None
    raw: Mapping[str, object]
    received_price: str | None
    def __init__(
        self,
        arrival_date: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_run_order: str | None = ...,
        arrival_time: str | None = ...,
        transfer_division_code: str | None = ...,
        departure_date: str | None = ...,
        departure_station_code: str | None = ...,
        departure_run_order: str | None = ...,
        departure_time: str | None = ...,
        general_remaining_seat_count: str | None = ...,
        delay_minutes: str | None = ...,
        free_remaining_seat_count: str | None = ...,
        standing_remaining_seat_count: str | None = ...,
        run_date: str | None = ...,
        special_remaining_seat_count: str | None = ...,
        train_class_code: str | None = ...,
        service_code: str | None = ...,
        train_no: str | None = ...,
        train_order_no: str | None = ...,
        yms_application_flag: str | None = ...,
        raw: Mapping[str, object] = ...,
        received_price: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class LimousineScheduleQuery(object):
    departure_date: str
    departure_station_code: str
    arrival_station_code: str
    service_code: str
    room_class_code: str
    departure_time: str
    train_no: str
    seat_attribute_code: str
    reservation_sale_division_code: str
    def __init__(
        self,
        departure_date: str,
        departure_station_code: str,
        arrival_station_code: str,
        service_code: str,
        room_class_code: str,
        departure_time: str,
        train_no: str,
        seat_attribute_code: str,
        reservation_sale_division_code: str,
    ) -> None: ...

@dataclass(frozen=True)
class LimousineScheduleResponse(BaseKorailResponse):
    following_page_extension: str | None
    long_short_division_code: str | None
    schedules: tuple[LimousineSchedule, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        following_page_extension: str | None = ...,
        long_short_division_code: str | None = ...,
        schedules: tuple[LimousineSchedule, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class LimousineSeat(object):
    direction_attribute_code: str | None
    other_attribute_code: str | None
    integrated_message: str | None
    integrated_message_code: str | None
    requested_attribute_code: str | None
    sale_possible_flag: str | None
    seat_no: str | None
    specification: str | None
    sequence_no: str | None
    visual_message_division_code: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        direction_attribute_code: str | None = ...,
        other_attribute_code: str | None = ...,
        integrated_message: str | None = ...,
        integrated_message_code: str | None = ...,
        requested_attribute_code: str | None = ...,
        sale_possible_flag: str | None = ...,
        seat_no: str | None = ...,
        specification: str | None = ...,
        sequence_no: str | None = ...,
        visual_message_division_code: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class LimousineSeatInventoryQuery(object):
    train_class_code: str
    service_code: str
    run_date: str
    train_no: str
    car_no: str
    room_class_code: str
    departure_station_code: str
    arrival_station_code: str
    seat_attribute_code: str
    departure_run_order: str
    arrival_run_order: str
    passenger_count: int
    product_no: str | None
    is_arrow: bool
    def __init__(
        self,
        train_class_code: str,
        service_code: str,
        run_date: str,
        train_no: str,
        car_no: str,
        room_class_code: str,
        departure_station_code: str,
        arrival_station_code: str,
        seat_attribute_code: str,
        departure_run_order: str,
        arrival_run_order: str,
        passenger_count: int,
        product_no: str | None = ...,
        is_arrow: bool = ...,
    ) -> None: ...

@dataclass(frozen=True)
class LimousineSeatInventoryResponse(BaseKorailResponse):
    car_type_code: str | None
    car_no: str | None
    seat_arrangement_code: str | None
    up_down_division_code: str | None
    layout_type: str | None
    vr_banner_url: str | None
    windows: tuple[SeatWindow, ...]
    seats: tuple[LimousineSeat, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        car_type_code: str | None = ...,
        car_no: str | None = ...,
        seat_arrangement_code: str | None = ...,
        up_down_division_code: str | None = ...,
        layout_type: str | None = ...,
        vr_banner_url: str | None = ...,
        windows: tuple[SeatWindow, ...] = ...,
        seats: tuple[LimousineSeat, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MaasMenuItem(object):
    active: str | None
    additional_service_code: str | None
    app_data: str | None
    icon_off: str | None
    icon_on: str | None
    info: str | None
    login_required: str | None
    name: str | None
    popup_image: str | None
    menu_type: str | None
    url: str | None
    raw: collections.abc.Mapping[str, object]
    def __init__(
        self,
        active: str | None = ...,
        additional_service_code: str | None = ...,
        app_data: str | None = ...,
        icon_off: str | None = ...,
        icon_on: str | None = ...,
        info: str | None = ...,
        login_required: str | None = ...,
        name: str | None = ...,
        popup_image: str | None = ...,
        menu_type: str | None = ...,
        url: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...
    @property
    def uses_station_selection(self) -> bool: ...

@dataclass(frozen=True)
class MaasMenuListResponse(BaseKorailResponse):
    items: tuple[MaasMenuItem, ...]
    departure_elevator_url: str | None
    departure_navigation_url: str | None
    departure_parking_url: str | None
    arrival_elevator_url: str | None
    arrival_bus_info_url: str | None
    arrival_parking_url: str | None
    arrival_baggage_transfer_robot_url: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[MaasMenuItem, ...] = ...,
        departure_elevator_url: str | None = ...,
        departure_navigation_url: str | None = ...,
        departure_parking_url: str | None = ...,
        arrival_elevator_url: str | None = ...,
        arrival_bus_info_url: str | None = ...,
        arrival_parking_url: str | None = ...,
        arrival_baggage_transfer_robot_url: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MaasServiceDetail(object):
    additional_service_division_code: str | None
    additional_service_goods_code: str | None
    additional_service_id: str | None
    marketing_entity_id: str | None
    marketing_entity_name: str | None
    additional_service_name: str | None
    progress_status_code: str | None
    request_no: str | None
    passenger_reference_content: str | None
    partner_reservation_no: str | None
    delivery_close_time: str | None
    delivery_start_time: str | None
    lead_message_1: str | None
    lead_message_2: str | None
    pnr_no: str | None
    request_date: str | None
    request_quantity: str | None
    reservation_station_code_name: str | None
    reservation_specification_url: str | None
    usage_close_date: str | None
    usage_start_date: str | None
    detail_info: MaasServiceDetailInfo | None
    raw: Mapping[str, object]
    def __init__(
        self,
        additional_service_division_code: str | None = ...,
        additional_service_goods_code: str | None = ...,
        additional_service_id: str | None = ...,
        marketing_entity_id: str | None = ...,
        marketing_entity_name: str | None = ...,
        additional_service_name: str | None = ...,
        progress_status_code: str | None = ...,
        request_no: str | None = ...,
        passenger_reference_content: str | None = ...,
        partner_reservation_no: str | None = ...,
        delivery_close_time: str | None = ...,
        delivery_start_time: str | None = ...,
        lead_message_1: str | None = ...,
        lead_message_2: str | None = ...,
        pnr_no: str | None = ...,
        request_date: str | None = ...,
        request_quantity: str | None = ...,
        reservation_station_code_name: str | None = ...,
        reservation_specification_url: str | None = ...,
        usage_close_date: str | None = ...,
        usage_start_date: str | None = ...,
        detail_info: MaasServiceDetailInfo | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MaasServiceDetailInfo(object):
    additional_service_request_no: str | None
    booking_time: str | None
    branch_name: str | None
    partner_name: str | None
    delivery_datetime: str | None
    drop_times: str | None
    dropoff_name: str | None
    image: str | None
    name: str | None
    option_name: str | None
    pickup_name: str | None
    pickup_place: str | None
    pickup_times: str | None
    reservation_date: str | None
    return_datetime: str | None
    start_datetime: str | None
    cancel_deadline_date: str | None
    cancel_return_amount: str | None
    cancel_return_fee: str | None
    goods_sequence: str | None
    intermediate_value: str | None
    received_amount: str | None
    reservation_status_name: str | None
    reservation_passenger_name: str | None
    settlement_deadline_date: str | None
    settlement_deadline_datetime: str | None
    settlement_status_code: str | None
    settlement_status_name: str | None
    total_settlement_amount: str | None
    usage_period_content: str | None
    entity_one: tuple[Mapping[str, object], ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        additional_service_request_no: str | None = ...,
        booking_time: str | None = ...,
        branch_name: str | None = ...,
        partner_name: str | None = ...,
        delivery_datetime: str | None = ...,
        drop_times: str | None = ...,
        dropoff_name: str | None = ...,
        image: str | None = ...,
        name: str | None = ...,
        option_name: str | None = ...,
        pickup_name: str | None = ...,
        pickup_place: str | None = ...,
        pickup_times: str | None = ...,
        reservation_date: str | None = ...,
        return_datetime: str | None = ...,
        start_datetime: str | None = ...,
        cancel_deadline_date: str | None = ...,
        cancel_return_amount: str | None = ...,
        cancel_return_fee: str | None = ...,
        goods_sequence: str | None = ...,
        intermediate_value: str | None = ...,
        received_amount: str | None = ...,
        reservation_status_name: str | None = ...,
        reservation_passenger_name: str | None = ...,
        settlement_deadline_date: str | None = ...,
        settlement_deadline_datetime: str | None = ...,
        settlement_status_code: str | None = ...,
        settlement_status_name: str | None = ...,
        total_settlement_amount: str | None = ...,
        usage_period_content: str | None = ...,
        entity_one: tuple[Mapping[str, object], ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MaasServiceDetailListResponse(BaseKorailResponse):
    details: tuple[MaasServiceDetail, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        details: tuple[MaasServiceDetail, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MaasServiceDetailQuery(object):
    start_date: str | None
    end_date: str | None
    def __init__(self, start_date: str | None = ..., end_date: str | None = ...) -> None: ...
    @classmethod
    def current(cls) -> MaasServiceDetailQuery: ...
    @classmethod
    def history(cls, start_date: str, end_date: str) -> MaasServiceDetailQuery: ...

@dataclass(frozen=True)
class MergeSeatsInquiryRequest(object):
    boarding_datetime: str
    run_datetime: str
    train_no: str
    departure_station_name: str
    arrival_station_name: str
    selected_station_name: str | None
    room_class_code: str
    seat_attribute_code: str
    passenger_count: int
    def __init__(
        self,
        boarding_datetime: str,
        run_datetime: str,
        train_no: str,
        departure_station_name: str,
        arrival_station_name: str,
        selected_station_name: str | None,
        room_class_code: str,
        seat_attribute_code: str,
        passenger_count: int,
    ) -> None: ...

@dataclass(frozen=True)
class MergeSeatsInquiryResponse(BaseKorailResponse):
    merge_reservation_possible_flag: str | None
    run_date: str | None
    intermediate_stations: tuple[IntermediateStation, ...]
    trains: tuple[TrainScheduleItem, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        merge_reservation_possible_flag: str | None = ...,
        run_date: str | None = ...,
        intermediate_stations: tuple[IntermediateStation, ...] = ...,
        trains: tuple[TrainScheduleItem, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class KorailPointSummaryResponse(BaseKorailResponse):
    korail_point: str | None
    discount_coupon_count: str | None
    delay_discount_count: str | None
    disability_flag: str | None
    welfare_discount_class_name: str | None
    welfare_discount_class_code: str | None
    customer_lead_flag_name: str | None
    phone_verified_flag: str | None
    email_verified_flag: str | None
    contact_channel_content: str | None
    naver_linked_flag: str | None
    kakao_linked_flag: str | None
    google_linked_flag: str | None
    apple_linked_flag: str | None
    customer_lead_flag: str | None
    disability_type_code: str | None
    disability_type_name: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        korail_point: str | None = ...,
        discount_coupon_count: str | None = ...,
        delay_discount_count: str | None = ...,
        disability_flag: str | None = ...,
        welfare_discount_class_name: str | None = ...,
        welfare_discount_class_code: str | None = ...,
        customer_lead_flag_name: str | None = ...,
        phone_verified_flag: str | None = ...,
        email_verified_flag: str | None = ...,
        contact_channel_content: str | None = ...,
        naver_linked_flag: str | None = ...,
        kakao_linked_flag: str | None = ...,
        google_linked_flag: str | None = ...,
        apple_linked_flag: str | None = ...,
        customer_lead_flag: str | None = ...,
        disability_type_code: str | None = ...,
        disability_type_name: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MileageHistoryEntry(object):
    departure_date: str | None
    point_division_name: str | None
    accrual_division_name: str | None
    receipt_division_name: str | None
    point_amount: str | None
    saved_point_value: str | None
    settlement_amount: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        departure_date: str | None = ...,
        point_division_name: str | None = ...,
        accrual_division_name: str | None = ...,
        receipt_division_name: str | None = ...,
        point_amount: str | None = ...,
        saved_point_value: str | None = ...,
        settlement_amount: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MileageHistoryRequest(object):
    start_date: str
    end_date: str
    ledger: KorailMileageLedger
    movement: KorailMileageMovement
    page_no: int
    def __init__(
        self,
        start_date: str,
        end_date: str,
        ledger: KorailMileageLedger = ...,
        movement: KorailMileageMovement = ...,
        page_no: int = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MileageHistoryResponse(BaseKorailResponse):
    page_count: str | None
    query_count: str | None
    total_available_rail_point: str | None
    total_available_rail_point_1: str | None
    total_available_affiliate_point: str | None
    total_accumulated_rail_point_1: str | None
    total_used_rail_point_1: str | None
    expiring_point_value: str | None
    ktx_mileage_info: str | None
    entries: tuple[MileageHistoryEntry, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        page_count: str | None = ...,
        query_count: str | None = ...,
        total_available_rail_point: str | None = ...,
        total_available_rail_point_1: str | None = ...,
        total_available_affiliate_point: str | None = ...,
        total_accumulated_rail_point_1: str | None = ...,
        total_used_rail_point_1: str | None = ...,
        expiring_point_value: str | None = ...,
        ktx_mileage_info: str | None = ...,
        entries: tuple[MileageHistoryEntry, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MultiChildDiscountTarget(object):
    birth_date: str | None
    customer_family_name: str | None
    discount_kind_code: str | None
    family_sequence: str | None
    passenger_type_code: str | None
    passenger_type_name: str | None
    room_class_code: str | None
    requested_discount_kind_code: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        birth_date: str | None = ...,
        customer_family_name: str | None = ...,
        discount_kind_code: str | None = ...,
        family_sequence: str | None = ...,
        passenger_type_code: str | None = ...,
        passenger_type_name: str | None = ...,
        room_class_code: str | None = ...,
        requested_discount_kind_code: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MultiChildDiscountTargetResponse(BaseKorailResponse):
    targets: tuple[MultiChildDiscountTarget, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        targets: tuple[MultiChildDiscountTarget, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class NoticeResponse(BaseKorailResponse):
    board_id: str | None
    post_sequence: str | None
    post_title: str | None
    post_content: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        board_id: str | None = ...,
        post_sequence: str | None = ...,
        post_title: str | None = ...,
        post_content: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class OriginalTicket(object):
    pnr_no: str | None
    ticket_kind_code: str | None
    original_sale_datetime: str | None
    original_window_no: str | None
    original_sale_sequence: str | None
    original_return_password: str | None
    member_card_no: str | None
    adult_count: str | None
    child_count: str | None
    group_discount_count: str | None
    passenger_type_division_code: str | None
    received_amount: str | None
    received_fare: str | None
    received_price: str | None
    change_sale_transaction_no: str | None
    sms_send_flag: str | None
    forced_sale_reason_text: str | None
    journeys: tuple[OriginalTicketJourney, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        pnr_no: str | None = ...,
        ticket_kind_code: str | None = ...,
        original_sale_datetime: str | None = ...,
        original_window_no: str | None = ...,
        original_sale_sequence: str | None = ...,
        original_return_password: str | None = ...,
        member_card_no: str | None = ...,
        adult_count: str | None = ...,
        child_count: str | None = ...,
        group_discount_count: str | None = ...,
        passenger_type_division_code: str | None = ...,
        received_amount: str | None = ...,
        received_fare: str | None = ...,
        received_price: str | None = ...,
        change_sale_transaction_no: str | None = ...,
        sms_send_flag: str | None = ...,
        forced_sale_reason_text: str | None = ...,
        journeys: tuple[OriginalTicketJourney, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class OriginalTicketInquiryResponse(BaseKorailResponse):
    tickets: tuple[OriginalTicket, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        tickets: tuple[OriginalTicket, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class OriginalTicketJourney(object):
    journey_sequence: str | None
    journey_order: str | None
    journey_type_code: str | None
    train_no: str | None
    train_group_code: str | None
    departure_date: str | None
    departure_time: str | None
    departure_station_code: str | None
    departure_station_name: str | None
    departure_construction_order: str | None
    arrival_date: str | None
    arrival_time: str | None
    arrival_station_code: str | None
    arrival_station_name: str | None
    arrival_construction_order: str | None
    goods_no: str | None
    total_seat_count: str | None
    total_standing_count: str | None
    general_change_allowed_flag: str | None
    single_ticket_flag: str | None
    seats: tuple[OriginalTicketSeat, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        journey_sequence: str | None = ...,
        journey_order: str | None = ...,
        journey_type_code: str | None = ...,
        train_no: str | None = ...,
        train_group_code: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        departure_construction_order: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_station_name: str | None = ...,
        arrival_construction_order: str | None = ...,
        goods_no: str | None = ...,
        total_seat_count: str | None = ...,
        total_standing_count: str | None = ...,
        general_change_allowed_flag: str | None = ...,
        single_ticket_flag: str | None = ...,
        seats: tuple[OriginalTicketSeat, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class OriginalTicketReference(object):
    sale_window_no: str
    sale_date: str
    sale_sequence: str
    return_password: str
    def __init__(
        self, sale_window_no: str, sale_date: str, sale_sequence: str, return_password: str
    ) -> None: ...

@dataclass(frozen=True)
class OriginalTicketSeat(object):
    passenger_sequence: str | None
    assign_sequence: str | None
    passenger_type_code: str | None
    room_class_code: str | None
    car_no: str | None
    seat_no: str | None
    seat_count: str | None
    received_fare: str | None
    received_price: str | None
    requested_seat_attribute_code: str | None
    direction_seat_attribute_code: str | None
    location_seat_attribute_code: str | None
    smoking_seat_attribute_code: str | None
    additional_seat_attribute_code: str | None
    etc_seat_attribute_code: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        passenger_sequence: str | None = ...,
        assign_sequence: str | None = ...,
        passenger_type_code: str | None = ...,
        room_class_code: str | None = ...,
        car_no: str | None = ...,
        seat_no: str | None = ...,
        seat_count: str | None = ...,
        received_fare: str | None = ...,
        received_price: str | None = ...,
        requested_seat_attribute_code: str | None = ...,
        direction_seat_attribute_code: str | None = ...,
        location_seat_attribute_code: str | None = ...,
        smoking_seat_attribute_code: str | None = ...,
        additional_seat_attribute_code: str | None = ...,
        etc_seat_attribute_code: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PhysicalSeat(object):
    seat_no: str
    sale_possible: str
    direction_code: str
    other_attribute_code: str | None
    requested_attribute_code: str
    floor: str | None
    specification: str
    sequence_no: str
    message_code: str
    message: str
    visual_message_division_code: str | None
    def __init__(
        self,
        seat_no: str,
        sale_possible: str,
        direction_code: str,
        other_attribute_code: str | None,
        requested_attribute_code: str,
        floor: str | None,
        specification: str,
        sequence_no: str,
        message_code: str,
        message: str,
        visual_message_division_code: str | None,
    ) -> None: ...

@dataclass(frozen=True)
class PassAvailabilityMainInfo(object):
    message_code: str | None
    total_count: str | None
    row_count: str | None
    selected_page_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        message_code: str | None = ...,
        total_count: str | None = ...,
        row_count: str | None = ...,
        selected_page_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassAvailabilityResponse(BaseKorailResponse):
    open_dates: tuple[str, ...]
    ticket_issue_dates: tuple[str, ...]
    offices: tuple[PassOffice, ...]
    pass_info: tuple[PassOpenDate, ...]
    main_info: PassAvailabilityMainInfo | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        open_dates: tuple[str, ...] = ...,
        ticket_issue_dates: tuple[str, ...] = ...,
        offices: tuple[PassOffice, ...] = ...,
        pass_info: tuple[PassOpenDate, ...] = ...,
        main_info: PassAvailabilityMainInfo | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassAgeOption(object):
    commuter_age_code: str | None
    display_name: str | None
    minimum_age: str | None
    maximum_age: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        commuter_age_code: str | None = ...,
        display_name: str | None = ...,
        minimum_age: str | None = ...,
        maximum_age: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassGoodsInfo(object):
    h_cnd_flg_disc_no: str | None
    psg_infos: PassPassengerInfos | None
    raw: Mapping[str, object]
    def __init__(
        self,
        h_cnd_flg_disc_no: str | None = ...,
        psg_infos: PassPassengerInfos | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassMenuData(object):
    commuter_kind_code: str | None
    station_selection: str | None
    age_options: tuple[PassAgeOption, ...]
    period_options: tuple[PassPeriodOption, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        commuter_kind_code: str | None = ...,
        station_selection: str | None = ...,
        age_options: tuple[PassAgeOption, ...] = ...,
        period_options: tuple[PassPeriodOption, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassMenuItem(object):
    after_day: str | None
    agreement: str | None
    detail_type: str | None
    detail_description: str | None
    enabled: str | None
    item_id: str | None
    information: str | None
    sale_message_1: str | None
    sale_message_2: str | None
    sale_message_3: str | None
    expanded: str | None
    parent_id: str | None
    representative_arrival: str | None
    representative_departure: str | None
    title: str | None
    train_group_code: str | None
    item_type: str | None
    goods_data: PassGoodsInfo | None
    pass_data: PassMenuData | None
    url: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        after_day: str | None = ...,
        agreement: str | None = ...,
        detail_type: str | None = ...,
        detail_description: str | None = ...,
        enabled: str | None = ...,
        item_id: str | None = ...,
        information: str | None = ...,
        sale_message_1: str | None = ...,
        sale_message_2: str | None = ...,
        sale_message_3: str | None = ...,
        expanded: str | None = ...,
        parent_id: str | None = ...,
        representative_arrival: str | None = ...,
        representative_departure: str | None = ...,
        title: str | None = ...,
        train_group_code: str | None = ...,
        item_type: str | None = ...,
        goods_data: PassGoodsInfo | None = ...,
        pass_data: PassMenuData | None = ...,
        url: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassMenuResponse(BaseKorailResponse):
    items: tuple[PassMenuItem, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[PassMenuItem, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassScheduleInfo(object):
    trains: tuple[PassScheduleTrain, ...]
    raw: Mapping[str, object]
    def __init__(
        self, trains: tuple[PassScheduleTrain, ...] = ..., raw: Mapping[str, object] = ...
    ) -> None: ...

@dataclass(frozen=True)
class PassScheduleMainInfo(object):
    sale_window_no: str | None
    work_date: str | None
    work_time: str | None
    job_id: str | None
    version_no: str | None
    message_code: str | None
    selected_count: str | None
    total_selected_count: str | None
    count_per_page: str | None
    page_count: str | None
    next_page_flag: str | None
    change_train_division_code: str | None
    page_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        sale_window_no: str | None = ...,
        work_date: str | None = ...,
        work_time: str | None = ...,
        job_id: str | None = ...,
        version_no: str | None = ...,
        message_code: str | None = ...,
        selected_count: str | None = ...,
        total_selected_count: str | None = ...,
        count_per_page: str | None = ...,
        page_count: str | None = ...,
        next_page_flag: str | None = ...,
        change_train_division_code: str | None = ...,
        page_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassScheduleRequest(object):
    selected_train_code: str
    departure_date: str
    departure_time: str
    transfer_type_code: str
    pass_kind_code: str
    pass_period_code: str
    pass_age_code: str
    page_no: str
    page_size: str
    departure_station_name: str
    arrival_station_name: str
    weekend_use_flag: str
    def __init__(
        self,
        selected_train_code: str,
        departure_date: str,
        departure_time: str,
        transfer_type_code: str,
        pass_kind_code: str,
        pass_period_code: str,
        pass_age_code: str,
        page_no: str,
        page_size: str,
        departure_station_name: str,
        arrival_station_name: str,
        weekend_use_flag: str,
    ) -> None: ...

@dataclass(frozen=True)
class PassScheduleResponse(BaseKorailResponse):
    main_info: PassScheduleMainInfo | None
    schedules: tuple[PassScheduleInfo, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        main_info: PassScheduleMainInfo | None = ...,
        schedules: tuple[PassScheduleInfo, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassScheduleTrain(object):
    arrival_station_code: str | None
    arrival_station_name: str | None
    departure_station_code: str | None
    departure_station_name: str | None
    detour_code: str | None
    schedule_price: str | None
    train_group_code: str | None
    train_no: str | None
    train_sequence: str | None
    change_train_sequence: str | None
    change_train_division_code: str | None
    run_date: str | None
    price_class_code: str | None
    route_code: str | None
    departure_construction_order: str | None
    arrival_construction_order: str | None
    car_type_code: str | None
    train_class_code: str | None
    commuter_use_terminal_code: str | None
    commuter_use_terminal_name: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        arrival_station_code: str | None = ...,
        arrival_station_name: str | None = ...,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        detour_code: str | None = ...,
        schedule_price: str | None = ...,
        train_group_code: str | None = ...,
        train_no: str | None = ...,
        train_sequence: str | None = ...,
        change_train_sequence: str | None = ...,
        change_train_division_code: str | None = ...,
        run_date: str | None = ...,
        price_class_code: str | None = ...,
        route_code: str | None = ...,
        departure_construction_order: str | None = ...,
        arrival_construction_order: str | None = ...,
        car_type_code: str | None = ...,
        train_class_code: str | None = ...,
        commuter_use_terminal_code: str | None = ...,
        commuter_use_terminal_name: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassOffice(object):
    code: str | None
    display_name: str | None
    raw: Mapping[str, object]
    def __init__(
        self, code: str | None = ..., display_name: str | None = ..., raw: Mapping[str, object] = ...
    ) -> None: ...

@dataclass(frozen=True)
class PassOpenDate(object):
    open_date: str | None
    item_sequence: str | None
    pnr_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        open_date: str | None = ...,
        item_sequence: str | None = ...,
        pnr_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassPassengerInfo(object):
    h_cls_prnb: int | None
    h_dcnt_knd_cd: str | None
    h_st_prnb: int | None
    raw: Mapping[str, object]
    def __init__(
        self,
        h_cls_prnb: int | None = ...,
        h_dcnt_knd_cd: str | None = ...,
        h_st_prnb: int | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassPassengerInfos(object):
    h_chtn_allw_flg: str | None
    h_max_cnt: str | None
    h_min_cnt: str | None
    psg_info: tuple[PassPassengerInfo, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        h_chtn_allw_flg: str | None = ...,
        h_max_cnt: str | None = ...,
        h_min_cnt: str | None = ...,
        psg_info: tuple[PassPassengerInfo, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PassPeriodOption(object):
    commuter_period_code: str | None
    display_name: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        commuter_period_code: str | None = ...,
        display_name: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PbpAcceptanceJourney(object):
    acceptance_customer_name: str
    acceptance_customer_phone: str
    journey_type_code: str
    member_division_name: str
    acceptance_kind_name: str
    pbp_reservation_no: str
    registered_date: str
    withdrawal_possible_flag: str
    seats: tuple[PbpAcceptanceSeat, ...]
    raw: Mapping[str, object]
    member_card_no: str
    def __init__(
        self,
        *,
        acceptance_customer_name: str,
        acceptance_customer_phone: str,
        journey_type_code: str,
        member_division_name: str,
        acceptance_kind_name: str,
        pbp_reservation_no: str,
        registered_date: str,
        withdrawal_possible_flag: str,
        seats: tuple[PbpAcceptanceSeat, ...] = ...,
        raw: Mapping[str, object] = ...,
        member_card_no: str,
    ) -> None: ...

@dataclass(frozen=True)
class PbpAcceptanceSeat(object):
    passenger_type_division_name: str
    room_class_code: str
    room_class_name: str
    car_no: int
    seat_no: str
    raw: Mapping[str, object]
    def __init__(
        self,
        *,
        passenger_type_division_name: str,
        room_class_code: str,
        room_class_name: str,
        car_no: int,
        seat_no: str,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PbpAcceptanceSpecificationResponse(BaseKorailResponse):
    tickets: tuple[PbpAcceptanceTicket, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        tickets: tuple[PbpAcceptanceTicket, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PbpAcceptanceTicket(object):
    pnr_no: str
    sale_date: str
    sale_sequence: str
    sale_window_no: str
    return_password: str
    journeys: tuple[PbpAcceptanceJourney, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        *,
        pnr_no: str,
        sale_date: str,
        sale_sequence: str,
        sale_window_no: str,
        return_password: str,
        journeys: tuple[PbpAcceptanceJourney, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ProductCancelResponse(BaseKorailResponse):
    integrated_message_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        integrated_message_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ProductDetailResponse(BaseKorailResponse):
    product_name: str | None
    reservation_status: str | None
    cancellation_deadline: str | None
    cancellation_amount: str | None
    cancellation_fee: str | None
    received_amount: str | None
    total_amount: str | None
    usage_period: str | None
    included_item_names: tuple[str, ...]
    virtual_reservation_no: str | None
    detail_raw: Mapping[str, object]
    goods_sequence: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        product_name: str | None = ...,
        reservation_status: str | None = ...,
        cancellation_deadline: str | None = ...,
        cancellation_amount: str | None = ...,
        cancellation_fee: str | None = ...,
        received_amount: str | None = ...,
        total_amount: str | None = ...,
        usage_period: str | None = ...,
        included_item_names: tuple[str, ...] = ...,
        virtual_reservation_no: str | None = ...,
        detail_raw: Mapping[str, object] = ...,
        goods_sequence: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ProductReservation(object):
    product_name: str | None
    reservation_status: str | None
    payment_deadline: str | None
    payment_status: str | None
    virtual_reservation_no: str | None
    raw: Mapping[str, object]
    reservation_sequence: str | None
    reservation_status_code: str | None
    def __init__(
        self,
        product_name: str | None = ...,
        reservation_status: str | None = ...,
        payment_deadline: str | None = ...,
        payment_status: str | None = ...,
        virtual_reservation_no: str | None = ...,
        raw: Mapping[str, object] = ...,
        reservation_sequence: str | None = ...,
        reservation_status_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ProductReservationListResponse(BaseKorailResponse):
    items: tuple[ProductReservation, ...]
    total_count: int | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[ProductReservation, ...] = ...,
        total_count: int | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PriceFare(object):
    journey_sequence: str | None
    room_class_name: str | None
    received_fare: str | None
    received_price: str | None
    total_amount: str | None
    train_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        journey_sequence: str | None = ...,
        room_class_name: str | None = ...,
        received_fare: str | None = ...,
        received_price: str | None = ...,
        total_amount: str | None = ...,
        train_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PriceFareLeg(object):
    departure_station_code: str
    arrival_station_code: str
    run_date: str
    train_no: str
    requested_seat_attribute_code: str
    train_group_code: str
    train_class_code: str
    goods_no: str | None
    def __init__(
        self,
        departure_station_code: str,
        arrival_station_code: str,
        run_date: str,
        train_no: str,
        requested_seat_attribute_code: str,
        train_group_code: str,
        train_class_code: str,
        goods_no: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PriceFareQuoteRequest(object):
    legs: tuple[PriceFareLeg, ...]
    menu_id: str
    def __init__(self, legs: tuple[PriceFareLeg, ...], menu_id: str = ...) -> None: ...

@dataclass(frozen=True)
class PriceFareQuoteResponse(BaseKorailResponse):
    fares: tuple[PriceFare, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        fares: tuple[PriceFare, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RecentDeliveryHistoryResponse(BaseKorailResponse):
    changed_acceptance_reservation_no: str | None
    recipients: tuple[RecentDeliveryRecipient, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        changed_acceptance_reservation_no: str | None = ...,
        recipients: tuple[RecentDeliveryRecipient, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RecentDeliveryRecipient(object):
    acceptance_customer_management_flag: str
    acceptance_customer_management_no: str
    acceptance_customer_name: str
    acceptance_customer_phone: str
    acceptance_customer_phone_2: str
    member_card_no: str
    raw: Mapping[str, object]
    def __init__(
        self,
        *,
        acceptance_customer_management_flag: str,
        acceptance_customer_management_no: str,
        acceptance_customer_name: str,
        acceptance_customer_phone: str,
        acceptance_customer_phone_2: str,
        member_card_no: str,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReceiptCashPayment(object):
    approval_method_name: str
    authentication_domain_recognition_no: str
    cash_receipt_approval_no: str
    cash_receipt_transaction_division_code: str
    total_approved_amount: int
    raw: Mapping[str, object]
    def __init__(
        self,
        *,
        approval_method_name: str,
        authentication_domain_recognition_no: str,
        cash_receipt_approval_no: str,
        cash_receipt_transaction_division_code: str,
        total_approved_amount: int,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReceiptPayment(object):
    payment_method: str
    approval_date: str
    installment_months: int
    amount: int
    account_no: str
    approval_no: str
    card_no: str
    point_no: str
    raw: Mapping[str, object]
    def __init__(
        self,
        *,
        payment_method: str,
        approval_date: str,
        installment_months: int,
        amount: int,
        account_no: str,
        approval_no: str,
        card_no: str,
        point_no: str,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RefundCommissionResponse(BaseKorailResponse):
    refund_amount: str | None
    refund_fee: str | None
    proceed_possible_flag: str | None
    ticket_return_times_division_code: str | None
    usable_mileage: str | None
    secondary_message_code: str | None
    secondary_message_text: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        refund_amount: str | None = ...,
        refund_fee: str | None = ...,
        proceed_possible_flag: str | None = ...,
        ticket_return_times_division_code: str | None = ...,
        usable_mileage: str | None = ...,
        secondary_message_code: str | None = ...,
        secondary_message_text: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RefundCompanion(object):
    name: str
    certificate_no: str
    def __init__(self, name: str = ..., certificate_no: str = ...) -> None: ...

@dataclass(frozen=True)
class RefundTicketDetailResponse(BaseKorailResponse):
    pnr_no: str | None
    sale_date: str | None
    sale_time: str | None
    window_name: str | None
    original_sale_date: str | None
    original_window_no: str | None
    original_sale_sequence: str | None
    original_return_password: str | None
    ticket_kind_code: str | None
    ticket_kind_name: str | None
    refund_possible_flag: str | None
    return_flag: str | None
    total_fare_amount: str | None
    total_discount_amount: str | None
    total_received_amount: str | None
    train_running_flag: str | None
    passenger_name: str | None
    passenger_birth_date: str | None
    companion_name: str | None
    companion_birth_date: str | None
    pbp_acceptance_target_flag: str | None
    delay_flag: str | None
    delay_ticket_flag: str | None
    additional_service_flag: str | None
    additional_service_cancel: str | None
    qr_code: str | None
    passenger_names: tuple[Mapping[str, object], ...]
    seat_tickets: tuple[Mapping[str, object], ...]
    limousine: Mapping[str, object] | None
    delay_details: tuple[Mapping[str, object], ...]
    journeys: tuple[RefundTicketJourney, ...]
    discount_card: DiscountCardOnTicket | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        pnr_no: str | None = ...,
        sale_date: str | None = ...,
        sale_time: str | None = ...,
        window_name: str | None = ...,
        original_sale_date: str | None = ...,
        original_window_no: str | None = ...,
        original_sale_sequence: str | None = ...,
        original_return_password: str | None = ...,
        ticket_kind_code: str | None = ...,
        ticket_kind_name: str | None = ...,
        refund_possible_flag: str | None = ...,
        return_flag: str | None = ...,
        total_fare_amount: str | None = ...,
        total_discount_amount: str | None = ...,
        total_received_amount: str | None = ...,
        train_running_flag: str | None = ...,
        passenger_name: str | None = ...,
        passenger_birth_date: str | None = ...,
        companion_name: str | None = ...,
        companion_birth_date: str | None = ...,
        pbp_acceptance_target_flag: str | None = ...,
        delay_flag: str | None = ...,
        delay_ticket_flag: str | None = ...,
        additional_service_flag: str | None = ...,
        additional_service_cancel: str | None = ...,
        qr_code: str | None = ...,
        passenger_names: tuple[Mapping[str, object], ...] = ...,
        seat_tickets: tuple[Mapping[str, object], ...] = ...,
        limousine: Mapping[str, object] | None = ...,
        delay_details: tuple[Mapping[str, object], ...] = ...,
        journeys: tuple[RefundTicketJourney, ...] = ...,
        discount_card: DiscountCardOnTicket | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RefundTicketJourney(object):
    journey_sequence: str | None
    journey_type_code: str | None
    departure_date: str | None
    departure_time: str | None
    departure_station_name: str | None
    arrival_date: str | None
    arrival_time: str | None
    arrival_station_name: str | None
    train_no: str | None
    train_class_name: str | None
    room_class_name: str | None
    platform_no: str | None
    seats: tuple[RefundTicketSeat, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        journey_sequence: str | None = ...,
        journey_type_code: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        departure_station_name: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        arrival_station_name: str | None = ...,
        train_no: str | None = ...,
        train_class_name: str | None = ...,
        room_class_name: str | None = ...,
        platform_no: str | None = ...,
        seats: tuple[RefundTicketSeat, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RefundTicketSeat(object):
    car_no: str | None
    seat_no: str | None
    buyer_name: str | None
    checkin_status_code: str | None
    discount_kind_code: str | None
    discount_kind_name: str | None
    passenger_type_code: str | None
    passenger_type_name: str | None
    seat_group_name: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        car_no: str | None = ...,
        seat_no: str | None = ...,
        buyer_name: str | None = ...,
        checkin_status_code: str | None = ...,
        discount_kind_code: str | None = ...,
        discount_kind_name: str | None = ...,
        passenger_type_code: str | None = ...,
        passenger_type_name: str | None = ...,
        seat_group_name: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class RefundTicketResponse(BaseKorailResponse):
    settlement_method_codes: tuple[str, ...]
    settlement_list_is_null: bool
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        settlement_method_codes: tuple[str, ...] = ...,
        settlement_list_is_null: bool = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfCheckInCancelResponse(BaseKorailResponse):
    message_id: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        message_id: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfCheckInInfoResponse(BaseKorailResponse):
    pnr_no: str | None
    train_no: str | None
    departure_station_name: str | None
    departure_time: str | None
    arrival_station_name: str | None
    arrival_time: str | None
    car_no: str | None
    seat_no: str | None
    train_class_name: str | None
    checkin_division_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        pnr_no: str | None = ...,
        train_no: str | None = ...,
        departure_station_name: str | None = ...,
        departure_time: str | None = ...,
        arrival_station_name: str | None = ...,
        arrival_time: str | None = ...,
        car_no: str | None = ...,
        seat_no: str | None = ...,
        train_class_name: str | None = ...,
        checkin_division_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfCheckInRegisterResponse(BaseKorailResponse):
    message_id: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        message_id: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfCheckInSeat(object):
    pnr_no: str
    journey_sequence: str
    assignment_sequence: str
    run_date: str
    train_no: str
    departure_construction_order: str
    departure_station_code: str
    arrival_construction_order: str
    arrival_station_code: str
    ticket_kind_code: str
    train_group_code: str
    car_no: str
    seat_no: str
    departure_datetime: str
    arrival_datetime: str
    cps_no: str
    raw: Mapping[str, object]
    def __init__(
        self,
        pnr_no: str,
        journey_sequence: str,
        assignment_sequence: str,
        run_date: str,
        train_no: str,
        departure_construction_order: str,
        departure_station_code: str,
        arrival_construction_order: str,
        arrival_station_code: str,
        ticket_kind_code: str,
        train_group_code: str,
        car_no: str,
        seat_no: str,
        departure_datetime: str,
        arrival_datetime: str,
        cps_no: str,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfCheckInSeatCheckResponse(BaseKorailResponse):
    seats: tuple[SelfCheckInSeat, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        seats: tuple[SelfCheckInSeat, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class StationRefundExecutionRequest(object):
    pnr_no: str
    original_sale_date: str
    original_sale_window_no: str
    original_sale_sequence: str
    original_return_password: str
    refund_division_code: str
    refund_reason_code: str
    ticket_kind_code: str
    customer_phone: str
    refund_amount: str
    refund_fee: str
    customer_name: str
    def __init__(
        self,
        pnr_no: str,
        original_sale_date: str,
        original_sale_window_no: str,
        original_sale_sequence: str,
        original_return_password: str,
        refund_division_code: str,
        refund_reason_code: str,
        ticket_kind_code: str,
        customer_phone: str,
        refund_amount: str,
        refund_fee: str,
        customer_name: str,
    ) -> None: ...
    @classmethod
    def from_verification(
        cls, verification: StationRefundVerificationResponse, *, customer_phone: str, customer_name: str
    ) -> StationRefundExecutionRequest: ...

@dataclass(frozen=True)
class StationRefundExecutionResponse(BaseKorailResponse):
    refund_division_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        refund_division_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class StationRefundOriginalTicket(object):
    pnr_no: str
    original_sale_date: str | None
    original_sale_window_no: str | None
    original_sale_sequence: str | None
    original_return_password: str | None
    ticket_kind_code: str | None
    refund_division_code: str | None
    refund_reason_code: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        pnr_no: str,
        original_sale_date: str | None = ...,
        original_sale_window_no: str | None = ...,
        original_sale_sequence: str | None = ...,
        original_return_password: str | None = ...,
        ticket_kind_code: str | None = ...,
        refund_division_code: str | None = ...,
        refund_reason_code: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class StationRefundVerificationRequest(object):
    customer_name: str
    return_no_1: str
    return_no_2: str
    return_no_3: str
    return_no_4: str
    def __init__(
        self, customer_name: str, return_no_1: str, return_no_2: str, return_no_3: str, return_no_4: str
    ) -> None: ...

@dataclass(frozen=True)
class StationRefundVerificationResponse(BaseKorailResponse):
    received_amount: str | None
    refund_fee: str | None
    refund_amount: str | None
    popup_message: str | None
    result_message: str | None
    original_tickets: tuple[StationRefundOriginalTicket, ...]
    original_ticket_list_is_null: bool
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        received_amount: str | None = ...,
        refund_fee: str | None = ...,
        refund_amount: str | None = ...,
        popup_message: str | None = ...,
        result_message: str | None = ...,
        original_tickets: tuple[StationRefundOriginalTicket, ...] = ...,
        original_ticket_list_is_null: bool = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationDetailJourney(object):
    journey_sequence: str | None
    journey_type_code: str | None
    reservation_change_no: str | None
    run_date: str | None
    departure_date: str | None
    departure_time: str | None
    arrival_time: str | None
    arrival_date: str | None
    departure_station_name: str | None
    arrival_station_name: str | None
    train_no: str | None
    train_class_name: str | None
    seats: tuple[ReservationSeatDetail, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        journey_sequence: str | None = ...,
        journey_type_code: str | None = ...,
        reservation_change_no: str | None = ...,
        run_date: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        arrival_time: str | None = ...,
        arrival_date: str | None = ...,
        departure_station_name: str | None = ...,
        arrival_station_name: str | None = ...,
        train_no: str | None = ...,
        train_class_name: str | None = ...,
        seats: tuple[ReservationSeatDetail, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHistoryJourney(object):
    trains: tuple[ReservationHistoryTrain, ...]
    service_infos: tuple[Mapping[str, object], ...]
    accompanying_infos: tuple[Mapping[str, object], ...]
    reservation: ReservationHistoryReservation | None
    raw: Mapping[str, object]
    def __init__(
        self,
        trains: tuple[ReservationHistoryTrain, ...] = ...,
        service_infos: tuple[Mapping[str, object], ...] = ...,
        accompanying_infos: tuple[Mapping[str, object], ...] = ...,
        reservation: ReservationHistoryReservation | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHistoryOriginalTicket(object):
    sale_date: str | None
    window_no: str | None
    sale_sequence: str | None
    return_password: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        sale_date: str | None = ...,
        window_no: str | None = ...,
        sale_sequence: str | None = ...,
        return_password: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHistoryPassenger(object):
    passenger_type_code: str | None
    passenger_count_per_info: str | None
    discount_kind_code: str | None
    discount_kind_code_2: str | None
    discount_no: str | None
    discount_no_2: str | None
    delay_original_window_no: str | None
    delay_original_sale_date: str | None
    delay_original_sale_sequence: str | None
    delay_original_return_password: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        passenger_type_code: str | None = ...,
        passenger_count_per_info: str | None = ...,
        discount_kind_code: str | None = ...,
        discount_kind_code_2: str | None = ...,
        discount_no: str | None = ...,
        discount_no_2: str | None = ...,
        delay_original_window_no: str | None = ...,
        delay_original_sale_date: str | None = ...,
        delay_original_sale_sequence: str | None = ...,
        delay_original_return_password: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHistoryReservation(object):
    pnr_no: str | None
    total_fare: str | None
    total_price: str | None
    total_discount_amount: str | None
    total_received_amount: str | None
    payment_flag: str | None
    tickets: tuple[ReservationHistoryTicket, ...]
    original_tickets: tuple[ReservationHistoryOriginalTicket, ...]
    passengers: tuple[ReservationHistoryPassenger, ...]
    raw: Mapping[str, object]
    def __init__(
        self,
        pnr_no: str | None = ...,
        total_fare: str | None = ...,
        total_price: str | None = ...,
        total_discount_amount: str | None = ...,
        total_received_amount: str | None = ...,
        payment_flag: str | None = ...,
        tickets: tuple[ReservationHistoryTicket, ...] = ...,
        original_tickets: tuple[ReservationHistoryOriginalTicket, ...] = ...,
        passengers: tuple[ReservationHistoryPassenger, ...] = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHistoryResponse(BaseKorailResponse):
    reservation_passenger_name: str | None
    phone_no: str | None
    reservation_limit_flag: str | None
    seatmap_flag: str | None
    process_flag: str | None
    follow_flag: str | None
    customer_no: str | None
    customer_division_code: str | None
    customer_sort_code: str | None
    customer_class_code: str | None
    journey_count: str | None
    guide_info: str | None
    journeys: tuple[ReservationHistoryJourney, ...]
    items: tuple[ReservationHistoryTrain, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        reservation_passenger_name: str | None = ...,
        phone_no: str | None = ...,
        reservation_limit_flag: str | None = ...,
        seatmap_flag: str | None = ...,
        process_flag: str | None = ...,
        follow_flag: str | None = ...,
        customer_no: str | None = ...,
        customer_division_code: str | None = ...,
        customer_sort_code: str | None = ...,
        customer_class_code: str | None = ...,
        journey_count: str | None = ...,
        guide_info: str | None = ...,
        journeys: tuple[ReservationHistoryJourney, ...] = ...,
        items: tuple[ReservationHistoryTrain, ...] = ...,
    ) -> None: ...
    @property
    def trains(self) -> tuple[ReservationHistoryTrain, ...]: ...

@dataclass(frozen=True)
class ReservationHistoryTicket(object):
    sale_date: str | None
    sale_window_no: str | None
    sale_sequence: str | None
    ticket_kind_code: str | None
    movie_ticket_flag: str | None
    delay_discount_flag: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        sale_date: str | None = ...,
        sale_window_no: str | None = ...,
        sale_sequence: str | None = ...,
        ticket_kind_code: str | None = ...,
        movie_ticket_flag: str | None = ...,
        delay_discount_flag: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHistoryTrain(object):
    departure_station: str | None
    departure_time: str | None
    arrival_station: str | None
    arrival_time: str | None
    run_date: str | None
    train_no: str | None
    train_class_code: str | None
    train_class_name: str | None
    reservation_type_code: str | None
    acceptance_possible_flag: str | None
    payment_flag: str | None
    settlement_flag: str | None
    reserved_amount: str | None
    seat_count: int | None
    standing_count: int | None
    pnr_no: str | None
    raw: Mapping[str, object]
    payment_deadline_date: str | None
    payment_deadline_time: str | None
    payment_message: str | None
    payment_possible_date: str | None
    prepayment_target_flag: str | None
    journey_sequence: str | None
    def __init__(
        self,
        departure_station: str | None = ...,
        departure_time: str | None = ...,
        arrival_station: str | None = ...,
        arrival_time: str | None = ...,
        run_date: str | None = ...,
        train_no: str | None = ...,
        train_class_code: str | None = ...,
        train_class_name: str | None = ...,
        reservation_type_code: str | None = ...,
        acceptance_possible_flag: str | None = ...,
        payment_flag: str | None = ...,
        settlement_flag: str | None = ...,
        reserved_amount: str | None = ...,
        seat_count: int | None = ...,
        standing_count: int | None = ...,
        pnr_no: str | None = ...,
        raw: Mapping[str, object] = ...,
        payment_deadline_date: str | None = ...,
        payment_deadline_time: str | None = ...,
        payment_message: str | None = ...,
        payment_possible_date: str | None = ...,
        prepayment_target_flag: str | None = ...,
        journey_sequence: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationSeatDetail(object):
    car_no: str | None
    seat_no: str | None
    room_class_code: str | None
    room_class_name: str | None
    passenger_type_code: str | None
    received_amount: str | None
    seat_price: str | None
    seat_fare: str | None
    total_discount_amount: str | None
    seat_group_name: str | None
    raw: Mapping[str, object]
    passenger_type_name: str | None
    def __init__(
        self,
        car_no: str | None = ...,
        seat_no: str | None = ...,
        room_class_code: str | None = ...,
        room_class_name: str | None = ...,
        passenger_type_code: str | None = ...,
        received_amount: str | None = ...,
        seat_price: str | None = ...,
        seat_fare: str | None = ...,
        total_discount_amount: str | None = ...,
        seat_group_name: str | None = ...,
        raw: Mapping[str, object] = ...,
        passenger_type_name: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class CardPayment(object):
    card_number: str
    card_password: str
    card_expire: str
    birthday: str
    installment: str
    card_type: Literal["J", "S"]
    def __init__(
        self,
        card_number: str,
        card_password: str,
        card_expire: str,
        birthday: str,
        installment: str = ...,
        card_type: Literal["J", "S"] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class PaidTicket(object):
    pnr_no: str
    sale_date: str
    sale_window_no: str
    sale_sequence: str
    return_password: str
    train_no: str
    pbp_acceptance_target_flag: str | None
    def __init__(
        self,
        pnr_no: str,
        sale_date: str,
        sale_window_no: str,
        sale_sequence: str,
        return_password: str,
        train_no: str = ...,
        pbp_acceptance_target_flag: str | None = ...,
    ) -> None: ...
    @classmethod
    def from_refund_detail(cls, detail: RefundTicketDetailResponse, *, train_no: str = ...) -> PaidTicket: ...

@dataclass(frozen=True)
class PriceRecalculationRequest(object):
    pnr_no: str
    rows: tuple[PriceRecalculationRow, ...]
    non_member_no: str | None
    cabin_class_code: str | None
    seat_attribute_code_2: str | None
    seat_attribute_code_4: str | None
    seat_attribute_code_5: str | None
    def __init__(
        self,
        pnr_no: str,
        rows: tuple[PriceRecalculationRow, ...] = ...,
        non_member_no: str | None = ...,
        cabin_class_code: str | None = ...,
        seat_attribute_code_2: str | None = ...,
        seat_attribute_code_4: str | None = ...,
        seat_attribute_code_5: str | None = ...,
    ) -> None: ...
    @classmethod
    def for_hold(
        cls, hold: ReservationHoldResponse, requested_discount_codes: Sequence[str]
    ) -> PriceRecalculationRequest: ...

@dataclass(frozen=True)
class PriceRecalculationRow(object):
    passenger_type_code: str
    room_class_code: str
    discount_kind_code: str
    requested_discount_code: str
    certificate_no: str
    family_sequence_no: str
    def __init__(
        self,
        passenger_type_code: str,
        room_class_code: str,
        discount_kind_code: str,
        requested_discount_code: str = ...,
        certificate_no: str = ...,
        family_sequence_no: str = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationHoldResponse(BaseKorailResponse):
    pnr_no: str | None
    journey_count: str | None
    window_no: str | None
    temporary_job_sequence_1: str | None
    temporary_job_sequence_2: str | None
    payment_flag: str | None
    payment_message: str | None
    payment_deadline_message: str | None
    payment_deadline_notice: str | None
    payment_deadline_date: str | None
    payment_deadline_time: str | None
    total_fare: str | None
    total_price: str | None
    received_amount: str | None
    journeys: tuple[ReservationJourney, ...]
    total_discount_amount: str | None
    customer_management_no: str | None
    mandatory_message: str | None
    additional_service_flag: str | None
    disability_certificate_number: str | None
    pre_settlement_target_flag: str | None
    family_info_confirm_flag: str | None
    special_room_fare: str | None
    issue_possible_date: str | None
    issue_possible_time: str | None
    passengers: tuple[ReservationPassengerInfo, ...]
    payable: bool
    cart_addition: CartAddResponse | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        pnr_no: str | None = ...,
        journey_count: str | None = ...,
        window_no: str | None = ...,
        temporary_job_sequence_1: str | None = ...,
        temporary_job_sequence_2: str | None = ...,
        payment_flag: str | None = ...,
        payment_message: str | None = ...,
        payment_deadline_message: str | None = ...,
        payment_deadline_notice: str | None = ...,
        payment_deadline_date: str | None = ...,
        payment_deadline_time: str | None = ...,
        total_fare: str | None = ...,
        total_price: str | None = ...,
        received_amount: str | None = ...,
        journeys: tuple[ReservationJourney, ...] = ...,
        total_discount_amount: str | None = ...,
        customer_management_no: str | None = ...,
        mandatory_message: str | None = ...,
        additional_service_flag: str | None = ...,
        disability_certificate_number: str | None = ...,
        pre_settlement_target_flag: str | None = ...,
        family_info_confirm_flag: str | None = ...,
        special_room_fare: str | None = ...,
        issue_possible_date: str | None = ...,
        issue_possible_time: str | None = ...,
        passengers: tuple[ReservationPassengerInfo, ...] = ...,
        payable: bool = ...,
        cart_addition: CartAddResponse | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationJourney(object):
    journey_sequence: str | None
    reservation_change_no: str | None
    departure_date: str | None
    departure_time: str | None
    arrival_date: str | None
    arrival_time: str | None
    departure_station_code: str | None
    arrival_station_code: str | None
    train_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        journey_sequence: str | None = ...,
        reservation_change_no: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        departure_station_code: str | None = ...,
        arrival_station_code: str | None = ...,
        train_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationPaymentCoupon(object):
    certificate_password: str | None
    coupon_no: str | None
    management_close_date: str | None
    management_start_date: str | None
    ticket_return_no: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        certificate_password: str | None = ...,
        coupon_no: str | None = ...,
        management_close_date: str | None = ...,
        management_start_date: str | None = ...,
        ticket_return_no: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationPaymentResponse(BaseKorailResponse):
    image_ticket_flag: str | None
    reservation_no: str | None
    settlement_approval_no: str | None
    total_received_amount: str | None
    settlement_amount: str | None
    total_settlement_amount: str | None
    customer_no: str | None
    member_card_no: str | None
    buyer_name: str | None
    publication_start_no: str | None
    publication_end_no: str | None
    mixed_settlement_division: str | None
    cancellation_fee: str | None
    coupons: tuple[ReservationPaymentCoupon, ...]
    tickets: tuple[ReservationPaymentTicket, ...]
    settlements: tuple[ReservationPaymentSettlement, ...]
    table_seats: tuple[ReservationPaymentTableSeat, ...]
    window_no: str | None
    settlement_count: str | None
    discount_card_count: str | None
    total_price: str | None
    total_fare: str | None
    total_discount_amount: str | None
    adult_count: str | None
    child_count: str | None
    table_seat_count: str | None
    ticket_count: str | None
    settlement_type_code: str | None
    trade_division: str | None
    remark: str | None
    survey_flag: str | None
    survey_title: str | None
    survey_text: str | None
    survey_url: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        image_ticket_flag: str | None = ...,
        reservation_no: str | None = ...,
        settlement_approval_no: str | None = ...,
        total_received_amount: str | None = ...,
        settlement_amount: str | None = ...,
        total_settlement_amount: str | None = ...,
        customer_no: str | None = ...,
        member_card_no: str | None = ...,
        buyer_name: str | None = ...,
        publication_start_no: str | None = ...,
        publication_end_no: str | None = ...,
        mixed_settlement_division: str | None = ...,
        cancellation_fee: str | None = ...,
        coupons: tuple[ReservationPaymentCoupon, ...] = ...,
        tickets: tuple[ReservationPaymentTicket, ...] = ...,
        settlements: tuple[ReservationPaymentSettlement, ...] = ...,
        table_seats: tuple[ReservationPaymentTableSeat, ...] = ...,
        window_no: str | None = ...,
        settlement_count: str | None = ...,
        discount_card_count: str | None = ...,
        total_price: str | None = ...,
        total_fare: str | None = ...,
        total_discount_amount: str | None = ...,
        adult_count: str | None = ...,
        child_count: str | None = ...,
        table_seat_count: str | None = ...,
        ticket_count: str | None = ...,
        settlement_type_code: str | None = ...,
        trade_division: str | None = ...,
        remark: str | None = ...,
        survey_flag: str | None = ...,
        survey_title: str | None = ...,
        survey_text: str | None = ...,
        survey_url: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationPaymentSettlement(object):
    settlement_sequence: str | None
    settlement_type_code: str | None
    settlement_result: str | None
    transaction_division: str | None
    card_installment_count: str | None
    installment_months: str | None
    settlement_amount: str | None
    settlement_card_no: str | None
    card_company_code: str | None
    card_company_name: str | None
    approval_date: str | None
    approval_time: str | None
    approval_no: str | None
    point_division: str | None
    point_no: str | None
    point_approval_no: str | None
    remnant_amount: str | None
    remote_point: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        settlement_sequence: str | None = ...,
        settlement_type_code: str | None = ...,
        settlement_result: str | None = ...,
        transaction_division: str | None = ...,
        card_installment_count: str | None = ...,
        installment_months: str | None = ...,
        settlement_amount: str | None = ...,
        settlement_card_no: str | None = ...,
        card_company_code: str | None = ...,
        card_company_name: str | None = ...,
        approval_date: str | None = ...,
        approval_time: str | None = ...,
        approval_no: str | None = ...,
        point_division: str | None = ...,
        point_no: str | None = ...,
        point_approval_no: str | None = ...,
        remnant_amount: str | None = ...,
        remote_point: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationPaymentTableSeat(object):
    room_class_name_1: str | None
    car_no_1: str | None
    seat_no_start_1: str | None
    seat_no_end_1: str | None
    seat_count_1: str | None
    group_name_1: str | None
    room_class_name_2: str | None
    car_no_2: str | None
    seat_no_start_2: str | None
    seat_no_end_2: str | None
    seat_count_2: str | None
    group_name_2: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        room_class_name_1: str | None = ...,
        car_no_1: str | None = ...,
        seat_no_start_1: str | None = ...,
        seat_no_end_1: str | None = ...,
        seat_count_1: str | None = ...,
        group_name_1: str | None = ...,
        room_class_name_2: str | None = ...,
        car_no_2: str | None = ...,
        seat_no_start_2: str | None = ...,
        seat_no_end_2: str | None = ...,
        seat_count_2: str | None = ...,
        group_name_2: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationPaymentTicket(object):
    ticket_sequence: str | None
    sale_date: str | None
    sale_sequence: str | None
    return_password: str | None
    return_no: str | None
    recipient_name: str | None
    discount_card_no: str | None
    ticket_price: str | None
    ticket_fare: str | None
    bz5_fare_discount_amount: str | None
    bz6_fare_discount_amount: str | None
    total_discount_amount: str | None
    total_received_amount: str | None
    standard_seat_price_fare: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        ticket_sequence: str | None = ...,
        sale_date: str | None = ...,
        sale_sequence: str | None = ...,
        return_password: str | None = ...,
        return_no: str | None = ...,
        recipient_name: str | None = ...,
        discount_card_no: str | None = ...,
        ticket_price: str | None = ...,
        ticket_fare: str | None = ...,
        bz5_fare_discount_amount: str | None = ...,
        bz6_fare_discount_amount: str | None = ...,
        total_discount_amount: str | None = ...,
        total_received_amount: str | None = ...,
        standard_seat_price_fare: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ReservationPassengerInfo(object):
    passenger_type_code: str | None
    passenger_count: str | None
    discount_kind_code: str | None
    discount_kind_code_2: str | None
    discount_proof_no: str | None
    discount_proof_no_2: str | None
    delay_original_window_no: str | None
    delay_original_sale_date: str | None
    delay_original_sale_sequence: str | None
    delay_original_return_password: str | None
    raw: collections.abc.Mapping[str, object]
    def __init__(
        self,
        passenger_type_code: str | None = ...,
        passenger_count: str | None = ...,
        discount_kind_code: str | None = ...,
        discount_kind_code_2: str | None = ...,
        discount_proof_no: str | None = ...,
        discount_proof_no_2: str | None = ...,
        delay_original_window_no: str | None = ...,
        delay_original_sale_date: str | None = ...,
        delay_original_sale_sequence: str | None = ...,
        delay_original_return_password: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SeatAttribute(object):
    name: str
    code: str | None
    def __init__(self, name: str, code: str | None = ...) -> None: ...

@dataclass(frozen=True)
class SeatCar(object):
    car_no: int | None
    room_class_name: str
    remaining_seat_count: int | None
    attributes: tuple[SeatAttribute, ...]
    room_class_code: str | None
    total_seat_count: int | None
    def __init__(
        self,
        car_no: int | None,
        room_class_name: str,
        remaining_seat_count: int | None,
        attributes: tuple[SeatAttribute, ...],
        room_class_code: str | None = ...,
        total_seat_count: int | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SeatCarListResponse(BaseKorailResponse):
    recommended_car_no: int | None
    train_no: str | None
    cars: tuple[SeatCar, ...]
    train_class_code: str | None
    train_group_code: str | None
    car_count: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        recommended_car_no: int | None = ...,
        train_no: str | None = ...,
        cars: tuple[SeatCar, ...] = ...,
        train_class_code: str | None = ...,
        train_group_code: str | None = ...,
        car_count: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SeatInventoryResponse(BaseKorailResponse):
    layout_type: str
    arrangement_code: str
    remaining_count: int | None
    total_count: int | None
    seats: tuple[PhysicalSeat, ...]
    windows: tuple[SeatWindow, ...]
    vr_banner_url: str | None
    car_type_code: str | None
    car_no: int | None
    up_down_division_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        layout_type: str = ...,
        arrangement_code: str = ...,
        remaining_count: int | None = ...,
        total_count: int | None = ...,
        seats: tuple[PhysicalSeat, ...] = ...,
        windows: tuple[SeatWindow, ...] = ...,
        vr_banner_url: str | None = ...,
        car_type_code: str | None = ...,
        car_no: int | None = ...,
        up_down_division_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SeatAssignmentScheduleRequest(object):
    menu_id: str
    departure_date: str
    departure_time: str
    departure_station_name: str
    arrival_station_name: str
    train_group_code: str
    room_class_code: str
    seat_attribute_code: str
    passenger_count: int
    standing_detour_division_name: str
    transfer_type_code: str
    connection_arrival_station_name: str
    def __init__(
        self,
        menu_id: str,
        departure_date: str,
        departure_time: str,
        departure_station_name: str,
        arrival_station_name: str,
        train_group_code: str,
        room_class_code: str,
        seat_attribute_code: str,
        passenger_count: int,
        standing_detour_division_name: str,
        transfer_type_code: str,
        connection_arrival_station_name: str,
    ) -> None: ...

@dataclass(frozen=True)
class SeatAssignmentScheduleResponse(BaseKorailResponse):
    next_page_flag: str | None
    merge_reservation_possible_flag: str | None
    job_id: str | None
    menu_id: str | None
    goods_no: str | None
    notice_message: str | None
    first_seat_count: str | None
    second_seat_count: str | None
    agreement_text: str | None
    first_departure_time: str | None
    result_count: str | None
    next_query_station_no: str | None
    next_train_no: str | None
    next_preceding_train_no: str | None
    next_connecting_train_no: str | None
    remaining_seat_count: str | None
    trains: tuple[TrainScheduleItem, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        next_page_flag: str | None = ...,
        merge_reservation_possible_flag: str | None = ...,
        job_id: str | None = ...,
        menu_id: str | None = ...,
        goods_no: str | None = ...,
        notice_message: str | None = ...,
        first_seat_count: str | None = ...,
        second_seat_count: str | None = ...,
        agreement_text: str | None = ...,
        first_departure_time: str | None = ...,
        result_count: str | None = ...,
        next_query_station_no: str | None = ...,
        next_train_no: str | None = ...,
        next_preceding_train_no: str | None = ...,
        next_connecting_train_no: str | None = ...,
        remaining_seat_count: str | None = ...,
        trains: tuple[TrainScheduleItem, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SeatWindow(object):
    start_location_ratio: float | None
    close_location_ratio: float | None
    def __init__(self, start_location_ratio: float | None, close_location_ratio: float | None) -> None: ...

@dataclass(frozen=True)
class SelfSeatChangeInfoRequest(object):
    run_date: str
    train_no: str
    departure_station_code: str
    arrival_station_code: str
    room_class_code: KorailSelfSeatChangeRoomClassCode | None
    def __init__(
        self,
        run_date: str,
        train_no: str,
        departure_station_code: str,
        arrival_station_code: str,
        room_class_code: KorailSelfSeatChangeRoomClassCode | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfSeatChangeInfoResponse(BaseKorailResponse):
    train_no: str | None
    train_class_code: str | None
    train_class_name: str | None
    train_group_code: str | None
    train_group_name: str | None
    run_date: str | None
    general_reservation_possible_code: str | None
    special_reservation_possible_code: str | None
    change_before_departure_construction_order: str | None
    change_before_arrival_construction_order: str | None
    existing_departure_run_order: str | None
    existing_arrival_run_order: str | None
    stations: tuple[SelfSeatChangeStation, ...]
    reasons: tuple[SelfSeatChangeReason, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        train_no: str | None = ...,
        train_class_code: str | None = ...,
        train_class_name: str | None = ...,
        train_group_code: str | None = ...,
        train_group_name: str | None = ...,
        run_date: str | None = ...,
        general_reservation_possible_code: str | None = ...,
        special_reservation_possible_code: str | None = ...,
        change_before_departure_construction_order: str | None = ...,
        change_before_arrival_construction_order: str | None = ...,
        existing_departure_run_order: str | None = ...,
        existing_arrival_run_order: str | None = ...,
        stations: tuple[SelfSeatChangeStation, ...] = ...,
        reasons: tuple[SelfSeatChangeReason, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfSeatChangeReason(object):
    query_code: str | None
    query_order: str | None
    reason_text: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        query_code: str | None = ...,
        query_order: str | None = ...,
        reason_text: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class SelfSeatChangeStation(object):
    departure_station_code: str | None
    departure_station_name: str | None
    departure_date: str | None
    departure_time: str | None
    arrival_date: str | None
    arrival_time: str | None
    departure_construction_order: str | None
    departure_run_order: str | None
    general_remaining_seats: str | None
    special_remaining_seats: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        departure_construction_order: str | None = ...,
        departure_run_order: str | None = ...,
        general_remaining_seats: str | None = ...,
        special_remaining_seats: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class ServiceStatusResponse(BaseKorailResponse):
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class StationDataResponse(BaseKorailResponse):
    stations: tuple[KorailStation, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        stations: tuple[KorailStation, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class StationInfoResponse(BaseKorailResponse):
    count: str
    map_version: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        count: str = ...,
        map_version: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainCalendarDay(object):
    run_date: str | None
    business_day_stage_code: str | None
    day_division_code: str | None
    holiday_division_code: str | None
    sale_day_division_code: str | None
    a_train_operation_flag: str | None
    d_train_operation_flag: str | None
    g_train_operation_flag: str | None
    o_train_operation_flag: str | None
    s_train_operation_flag: str | None
    v_train_operation_flag: str | None
    x_train_operation_flag: str | None
    raw: collections.abc.Mapping[str, object]
    def __init__(
        self,
        run_date: str | None = ...,
        business_day_stage_code: str | None = ...,
        day_division_code: str | None = ...,
        holiday_division_code: str | None = ...,
        sale_day_division_code: str | None = ...,
        a_train_operation_flag: str | None = ...,
        d_train_operation_flag: str | None = ...,
        g_train_operation_flag: str | None = ...,
        o_train_operation_flag: str | None = ...,
        s_train_operation_flag: str | None = ...,
        v_train_operation_flag: str | None = ...,
        x_train_operation_flag: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainCalendarResponse(BaseKorailResponse):
    days: tuple[TrainCalendarDay, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        days: tuple[TrainCalendarDay, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainSearchContinuation(object):
    query_station_no: str
    query_train_no: str
    query_train_no2: str
    def __init__(self, query_station_no: str, query_train_no: str, query_train_no2: str = ...) -> None: ...

@dataclass(frozen=True)
class TrainSearchQuery(object):
    departure_station_code: str
    arrival_station_code: str
    departure_date: str
    departure_time: str
    passengers: int
    train_group_code: str
    include_srt: bool
    child_passengers: int
    senior_passengers: int
    high_disability_passengers: int
    low_disability_passengers: int
    seat_attribute_code: str
    connection_station_codes: tuple[str, ...]
    connection_train_group_code: str | None
    query_division_code: str
    teenager_passengers: int
    infant_passengers: int
    guide_dog_passengers: int
    include_nearby_stations: bool
    def __init__(
        self,
        departure_station_code: str,
        arrival_station_code: str,
        departure_date: str,
        departure_time: str = ...,
        passengers: int = ...,
        train_group_code: str = ...,
        include_srt: bool = ...,
        child_passengers: int = ...,
        senior_passengers: int = ...,
        high_disability_passengers: int = ...,
        low_disability_passengers: int = ...,
        seat_attribute_code: str = ...,
        connection_station_codes: tuple[str, ...] = ...,
        connection_train_group_code: str | None = ...,
        query_division_code: str = ...,
        teenager_passengers: int = ...,
        infant_passengers: int = ...,
        guide_dog_passengers: int = ...,
        include_nearby_stations: bool = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainSearchMetadata(object):
    job_id: str | None
    menu_id: str | None
    product_no: str | None
    next_page_flag: str | None
    next_query_station_no: str | None
    next_train_no: str | None
    next_preceding_train_no: str | None
    next_connecting_train_no: str | None
    result_count: str | None
    notice_message: str | None
    first_seat_count: str | None
    second_seat_count: str | None
    first_departure_time: str | None
    raw: collections.abc.Mapping[str, object]
    agreement_text: str | None
    remaining_seat_count: str | None
    def __init__(
        self,
        job_id: str | None = ...,
        menu_id: str | None = ...,
        product_no: str | None = ...,
        next_page_flag: str | None = ...,
        next_query_station_no: str | None = ...,
        next_train_no: str | None = ...,
        next_preceding_train_no: str | None = ...,
        next_connecting_train_no: str | None = ...,
        result_count: str | None = ...,
        notice_message: str | None = ...,
        first_seat_count: str | None = ...,
        second_seat_count: str | None = ...,
        first_departure_time: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        agreement_text: str | None = ...,
        remaining_seat_count: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainSearchResult(object):
    trains: list[TrainSummary]
    response: BaseKorailResponse
    raw: collections.abc.Mapping[str, object]
    metadata: TrainSearchMetadata
    unfiltered_trains: list[TrainSummary] | None
    def __init__(
        self,
        trains: list[TrainSummary],
        response: BaseKorailResponse,
        raw: collections.abc.Mapping[str, object] = ...,
        metadata: TrainSearchMetadata = ...,
        unfiltered_trains: list[TrainSummary] | None = ...,
    ) -> None: ...
    def next_page(self) -> TrainSearchContinuation | None: ...
    def next_query_from_last_departure(self, query: TrainSearchQuery) -> TrainSearchQuery | None: ...

@dataclass(frozen=True)
class TrainScheduleResponse(BaseKorailResponse):
    delay_detail_reason_content: str | None
    stops: tuple[TrainScheduleStop, ...]
    delay_station_construction_order: str | None
    integrated_message_code: str | None
    message_code: str | None
    message_content: str | None
    message_text: str | None
    origin_station_code: str | None
    origin_station_name: str | None
    route_code: str | None
    route_name: str | None
    run_date: str | None
    run_segment_order: str | None
    regular_sale_flag: str | None
    standard_train_class_code: str | None
    terminal_station_code: str | None
    terminal_station_name: str | None
    train_attribute_code: str | None
    train_departure_flag: str | None
    train_no: str | None
    special_train_flag: str | None
    up_down_division_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        delay_detail_reason_content: str | None = ...,
        stops: tuple[TrainScheduleStop, ...] = ...,
        delay_station_construction_order: str | None = ...,
        integrated_message_code: str | None = ...,
        message_code: str | None = ...,
        message_content: str | None = ...,
        message_text: str | None = ...,
        origin_station_code: str | None = ...,
        origin_station_name: str | None = ...,
        route_code: str | None = ...,
        route_name: str | None = ...,
        run_date: str | None = ...,
        run_segment_order: str | None = ...,
        regular_sale_flag: str | None = ...,
        standard_train_class_code: str | None = ...,
        terminal_station_code: str | None = ...,
        terminal_station_name: str | None = ...,
        train_attribute_code: str | None = ...,
        train_departure_flag: str | None = ...,
        train_no: str | None = ...,
        special_train_flag: str | None = ...,
        up_down_division_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainScheduleStop(object):
    station_code: str | None
    station_name: str | None
    station_construction_order: str | None
    run_order: str | None
    actual_arrival_delay_count: str | None
    actual_arrival_date: str | None
    actual_arrival_time: str | None
    actual_departure_date: str | None
    actual_departure_time: str | None
    planned_arrival_date: str | None
    planned_arrival_time: str | None
    planned_departure_date: str | None
    planned_departure_time: str | None
    delay_fare_return_division_code: str | None
    delay_fare_return_division_name: str | None
    solo_operation_delay_flag: str | None
    detour_driver_delay_count: str | None
    expected_arrival_delay_count: str | None
    expected_departure_delay_count: str | None
    regular_flag: str | None
    service_flag: str | None
    raw: collections.abc.Mapping[str, object]
    def __init__(
        self,
        station_code: str | None = ...,
        station_name: str | None = ...,
        station_construction_order: str | None = ...,
        run_order: str | None = ...,
        actual_arrival_delay_count: str | None = ...,
        actual_arrival_date: str | None = ...,
        actual_arrival_time: str | None = ...,
        actual_departure_date: str | None = ...,
        actual_departure_time: str | None = ...,
        planned_arrival_date: str | None = ...,
        planned_arrival_time: str | None = ...,
        planned_departure_date: str | None = ...,
        planned_departure_time: str | None = ...,
        delay_fare_return_division_code: str | None = ...,
        delay_fare_return_division_name: str | None = ...,
        solo_operation_delay_flag: str | None = ...,
        detour_driver_delay_count: str | None = ...,
        expected_arrival_delay_count: str | None = ...,
        expected_departure_delay_count: str | None = ...,
        regular_flag: str | None = ...,
        service_flag: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainScheduleItem(object):
    train_no: str | None
    train_no_qb: str | None
    train_sequence: str | None
    train_group_code: str | None
    train_class_code: str | None
    train_class_name: str | None
    run_date: str | None
    departure_date: str | None
    departure_time: str | None
    departure_time_qb: str | None
    arrival_date: str | None
    arrival_time: str | None
    arrival_time_qb: str | None
    departure_station_code: str | None
    departure_station_name: str | None
    arrival_station_code: str | None
    arrival_station_name: str | None
    departure_construction_order: str | None
    arrival_construction_order: str | None
    departure_run_order: str | None
    arrival_run_order: str | None
    car_type_name: str | None
    general_room_name: str | None
    special_room_name: str | None
    general_reservation_code: str | None
    general_reservation_name: str | None
    special_reservation_code: str | None
    free_seat_reservation_code: str | None
    standing_reservation_code: str | None
    standing_reservation_name: str | None
    journey_reservation_code: str | None
    journey_reservation_name: str | None
    seat_map_flag: str | None
    delay_sale_flag: str | None
    wait_reservation_flag: str | None
    reservation_possible_name: str | None
    special_reservation_possible_name: str | None
    info_text: str | None
    popup_message: str | None
    shuttle_standing_open_flag: str | None
    remaining_standing_count: str | None
    standard_remaining_seat_count: str | None
    first_remaining_seat_count: str | None
    merge_target_flag: str | None
    train_suspended_flag: str | None
    raw: Mapping[str, object]
    special_reservation_name: str | None
    free_seat_reservation_name: str | None
    def __init__(
        self,
        train_no: str | None = ...,
        train_no_qb: str | None = ...,
        train_sequence: str | None = ...,
        train_group_code: str | None = ...,
        train_class_code: str | None = ...,
        train_class_name: str | None = ...,
        run_date: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        departure_time_qb: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        arrival_time_qb: str | None = ...,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_station_name: str | None = ...,
        departure_construction_order: str | None = ...,
        arrival_construction_order: str | None = ...,
        departure_run_order: str | None = ...,
        arrival_run_order: str | None = ...,
        car_type_name: str | None = ...,
        general_room_name: str | None = ...,
        special_room_name: str | None = ...,
        general_reservation_code: str | None = ...,
        general_reservation_name: str | None = ...,
        special_reservation_code: str | None = ...,
        free_seat_reservation_code: str | None = ...,
        standing_reservation_code: str | None = ...,
        standing_reservation_name: str | None = ...,
        journey_reservation_code: str | None = ...,
        journey_reservation_name: str | None = ...,
        seat_map_flag: str | None = ...,
        delay_sale_flag: str | None = ...,
        wait_reservation_flag: str | None = ...,
        reservation_possible_name: str | None = ...,
        special_reservation_possible_name: str | None = ...,
        info_text: str | None = ...,
        popup_message: str | None = ...,
        shuttle_standing_open_flag: str | None = ...,
        remaining_standing_count: str | None = ...,
        standard_remaining_seat_count: str | None = ...,
        first_remaining_seat_count: str | None = ...,
        merge_target_flag: str | None = ...,
        train_suspended_flag: str | None = ...,
        raw: Mapping[str, object] = ...,
        special_reservation_name: str | None = ...,
        free_seat_reservation_name: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TrainSummary(object):
    train_no: str
    train_group_code: str | None
    departure_station_code: str | None
    arrival_station_code: str | None
    departure_date: str | None
    departure_time: str | None
    arrival_time: str | None
    raw: collections.abc.Mapping[str, object]
    departure_station_name: str | None
    arrival_station_name: str | None
    run_date: str | None
    train_class_code: str | None
    departure_run_order: str | None
    arrival_run_order: str | None
    seat_map_flag: str | None
    general_reservation_code: str | None
    general_reservation_flag: str | None
    departure_construction_order: str | None
    arrival_construction_order: str | None
    seat_attribute_code: str | None
    car_type_code: str | None
    car_type_name: str | None
    train_class_name: str | None
    train_group_name: str | None
    general_room_class_name: str | None
    special_room_class_name: str | None
    secondary_general_reservation_code: str | None
    special_reservation_code: str | None
    special_reservation_flag: str | None
    secondary_special_reservation_code: str | None
    free_reservation_code: str | None
    free_reservation_flag: str | None
    standing_reservation_code: str | None
    standing_reservation_flag: str | None
    reservation_available_flag: str | None
    general_availability_name: str | None
    special_availability_name: str | None
    wait_reservation_flag: str | None
    standard_remaining_seat_count: str | None
    first_class_remaining_seat_count: str | None
    free_remaining_seat_count: str | None
    standing_remaining_seat_count: str | None
    free_car_count: str | None
    reservation_wait_passenger_count: str | None
    total_passenger_count: int | None
    goods_no: str | None
    train_sequence: str | None
    change_train_sequence: str | None
    change_train_division_code: str | None
    merge_seat_application_flag: str | None
    train_suspension_flag: str | None
    general_fare_text: str | None
    special_fare_text: str | None
    standing_availability_name: str | None
    free_availability_name: str | None
    arrival_date: str | None
    def __init__(
        self,
        train_no: str,
        train_group_code: str | None = ...,
        departure_station_code: str | None = ...,
        arrival_station_code: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        arrival_time: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        departure_station_name: str | None = ...,
        arrival_station_name: str | None = ...,
        run_date: str | None = ...,
        train_class_code: str | None = ...,
        departure_run_order: str | None = ...,
        arrival_run_order: str | None = ...,
        seat_map_flag: str | None = ...,
        general_reservation_code: str | None = ...,
        general_reservation_flag: str | None = ...,
        departure_construction_order: str | None = ...,
        arrival_construction_order: str | None = ...,
        seat_attribute_code: str | None = ...,
        car_type_code: str | None = ...,
        car_type_name: str | None = ...,
        train_class_name: str | None = ...,
        train_group_name: str | None = ...,
        general_room_class_name: str | None = ...,
        special_room_class_name: str | None = ...,
        secondary_general_reservation_code: str | None = ...,
        special_reservation_code: str | None = ...,
        special_reservation_flag: str | None = ...,
        secondary_special_reservation_code: str | None = ...,
        free_reservation_code: str | None = ...,
        free_reservation_flag: str | None = ...,
        standing_reservation_code: str | None = ...,
        standing_reservation_flag: str | None = ...,
        reservation_available_flag: str | None = ...,
        general_availability_name: str | None = ...,
        special_availability_name: str | None = ...,
        wait_reservation_flag: str | None = ...,
        standard_remaining_seat_count: str | None = ...,
        first_class_remaining_seat_count: str | None = ...,
        free_remaining_seat_count: str | None = ...,
        standing_remaining_seat_count: str | None = ...,
        free_car_count: str | None = ...,
        reservation_wait_passenger_count: str | None = ...,
        total_passenger_count: int | None = ...,
        goods_no: str | None = ...,
        train_sequence: str | None = ...,
        change_train_sequence: str | None = ...,
        change_train_division_code: str | None = ...,
        merge_seat_application_flag: str | None = ...,
        train_suspension_flag: str | None = ...,
        general_fare_text: str | None = ...,
        special_fare_text: str | None = ...,
        standing_availability_name: str | None = ...,
        free_availability_name: str | None = ...,
        arrival_date: str | None = ...,
    ) -> None: ...
    def has_general_seat(self) -> bool: ...
    def has_special_seat(self) -> bool: ...
    def has_seat(self) -> bool: ...
    def has_waiting_list(self) -> bool: ...
    @property
    def duration_minutes(self) -> int | None: ...
    @property
    def duration_text(self) -> str | None: ...
    def summary(self) -> str: ...
    @classmethod
    def from_raw(cls, raw: collections.abc.Mapping[str, object]) -> typing.Self: ...

@dataclass(frozen=True)
class TransferItinerary(object):
    first: TrainSummary
    second: TrainSummary
    def __init__(self, first: TrainSummary, second: TrainSummary) -> None: ...
    @property
    def legs(self) -> tuple[TrainSummary, ...]: ...
    @property
    def transfer_station_code(self) -> str | None: ...
    @property
    def transfer_station_name(self) -> str | None: ...

@dataclass(frozen=True)
class TransferSearchResult(object):
    itineraries: list[TransferItinerary]
    trains: list[TrainSummary]
    response: BaseKorailResponse
    raw: collections.abc.Mapping[str, object]
    metadata: TrainSearchMetadata
    def __init__(
        self,
        itineraries: list[TransferItinerary],
        trains: list[TrainSummary],
        response: BaseKorailResponse,
        raw: collections.abc.Mapping[str, object] = ...,
        metadata: TrainSearchMetadata = ...,
    ) -> None: ...
    def next_page(self) -> TrainSearchContinuation | None: ...

@dataclass(frozen=True)
class TicketReceipt(object):
    travel_date: str
    departure_station: str
    departure_time: str
    arrival_station: str
    arrival_time: str
    commuter_kind_code: str
    journey_type_code: str
    printed_discount_name: str
    printed_discount_kind_code: str
    print_type: str
    seat_class_name: str
    ticket_kind_code: str
    ticket_kind_name: str
    ticket_status_code: str
    train_class_code: str
    train_class_name: str
    train_group_code: str
    train_no: str
    passenger_counts: tuple[int, int, int]
    received_amount: int
    card_refund_amount: int
    refund_fee: int
    refund_received_amount: int
    point_refund_amount: int
    payments: tuple[ReceiptPayment, ...]
    cash_receipts: tuple[ReceiptCashPayment, ...]
    member_card_no: str
    raw: Mapping[str, object]
    def __init__(
        self,
        *,
        travel_date: str,
        departure_station: str,
        departure_time: str,
        arrival_station: str,
        arrival_time: str,
        commuter_kind_code: str,
        journey_type_code: str,
        printed_discount_name: str,
        printed_discount_kind_code: str,
        print_type: str,
        seat_class_name: str,
        ticket_kind_code: str,
        ticket_kind_name: str,
        ticket_status_code: str,
        train_class_code: str,
        train_class_name: str,
        train_group_code: str,
        train_no: str,
        passenger_counts: tuple[int, int, int],
        received_amount: int,
        card_refund_amount: int,
        refund_fee: int,
        refund_received_amount: int,
        point_refund_amount: int,
        payments: tuple[ReceiptPayment, ...] = ...,
        cash_receipts: tuple[ReceiptCashPayment, ...] = ...,
        member_card_no: str,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketReceiptResponse(BaseKorailResponse):
    items: tuple[TicketReceipt, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[TicketReceipt, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketReservationDetailRequest(object):
    pnr_no: str
    def __init__(self, pnr_no: str) -> None: ...

@dataclass(frozen=True)
class TicketReservationDetailResponse(BaseKorailResponse):
    pnr_no: str | None
    window_no: str | None
    journey_count: str | None
    total_fare: str | None
    total_price: str | None
    total_discount_amount: str | None
    total_received_amount: str | None
    payment_flag: str | None
    journeys: tuple[ReservationDetailJourney, ...]
    customer_management_no: str | None
    mandatory_message: str | None
    additional_service_flag: str | None
    disability_certificate_number: str | None
    pre_settlement_target_flag: str | None
    family_info_confirm_flag: str | None
    special_room_fare: str | None
    issue_possible_date: str | None
    issue_possible_time: str | None
    passengers: tuple[ReservationPassengerInfo, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        pnr_no: str | None = ...,
        window_no: str | None = ...,
        journey_count: str | None = ...,
        total_fare: str | None = ...,
        total_price: str | None = ...,
        total_discount_amount: str | None = ...,
        total_received_amount: str | None = ...,
        payment_flag: str | None = ...,
        journeys: tuple[ReservationDetailJourney, ...] = ...,
        customer_management_no: str | None = ...,
        mandatory_message: str | None = ...,
        additional_service_flag: str | None = ...,
        disability_certificate_number: str | None = ...,
        pre_settlement_target_flag: str | None = ...,
        family_info_confirm_flag: str | None = ...,
        special_room_fare: str | None = ...,
        issue_possible_date: str | None = ...,
        issue_possible_time: str | None = ...,
        passengers: tuple[ReservationPassengerInfo, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketDuplicationCheckRequest(object):
    pnr_no: str
    def __init__(self, pnr_no: str) -> None: ...

@dataclass(frozen=True)
class TicketDuplicationCheckResponse(BaseKorailResponse):
    reservation_count: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        reservation_count: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketListReservation(object):
    tickets: tuple[TicketListTicket, ...]
    departure_datetime: str | None
    ticket_kind_code: str | None
    list_count: str | None
    seat_assign_count: int | None
    ticket_status: str | None
    is_finished: bool | None
    is_history: bool | None
    is_emergency: bool | None
    display_ticket_name: str | None
    is_non_member: bool | None
    is_transfer: bool | None
    is_wheelchair_member: bool | None
    is_rail_police_enabled: bool | None
    raw: Mapping[str, object]
    additional_service: MaasServiceDetail | None
    ticket_kind: str | None
    def __init__(
        self,
        tickets: tuple[TicketListTicket, ...] = ...,
        departure_datetime: str | None = ...,
        ticket_kind_code: str | None = ...,
        list_count: str | None = ...,
        seat_assign_count: int | None = ...,
        ticket_status: str | None = ...,
        is_finished: bool | None = ...,
        is_history: bool | None = ...,
        is_emergency: bool | None = ...,
        display_ticket_name: str | None = ...,
        is_non_member: bool | None = ...,
        is_transfer: bool | None = ...,
        is_wheelchair_member: bool | None = ...,
        is_rail_police_enabled: bool | None = ...,
        raw: Mapping[str, object] = ...,
        additional_service: MaasServiceDetail | None = ...,
        ticket_kind: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketListResponse(BaseKorailResponse):
    reservations: tuple[TicketListReservation, ...]
    total_count: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        reservations: tuple[TicketListReservation, ...] = ...,
        total_count: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketListTicket(object):
    pnr_no: str | None
    sale_window_no: str | None
    sale_date: str | None
    return_sale_date: str | None
    sale_sequence: str | None
    return_password: str | None
    ticket_status_code: str | None
    ticket_kind_code: str | None
    ticket_kind_name: str | None
    train_info: tuple[Mapping[str, object], ...]
    raw: Mapping[str, object]
    ticket_sequence: str | None
    ticket_status_name: str | None
    return_possible_flag: str | None
    use_transaction_no: str | None
    notify_use_transaction_no: str | None
    pbp_acceptance_target_flag: str | None
    trains: tuple[TicketListTrain, ...]
    def __init__(
        self,
        pnr_no: str | None = ...,
        sale_window_no: str | None = ...,
        sale_date: str | None = ...,
        return_sale_date: str | None = ...,
        sale_sequence: str | None = ...,
        return_password: str | None = ...,
        ticket_status_code: str | None = ...,
        ticket_kind_code: str | None = ...,
        ticket_kind_name: str | None = ...,
        train_info: tuple[Mapping[str, object], ...] = ...,
        raw: Mapping[str, object] = ...,
        ticket_sequence: str | None = ...,
        ticket_status_name: str | None = ...,
        return_possible_flag: str | None = ...,
        use_transaction_no: str | None = ...,
        notify_use_transaction_no: str | None = ...,
        pbp_acceptance_target_flag: str | None = ...,
        trains: tuple[TicketListTrain, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TicketListTrain(object):
    journey_sequence: str | None
    run_date: str | None
    train_no: str | None
    train_class_code: str | None
    train_class_name: str | None
    departure_station_code: str | None
    departure_station_name: str | None
    departure_date: str | None
    departure_time: str | None
    arrival_station_code: str | None
    arrival_station_name: str | None
    arrival_date: str | None
    arrival_time: str | None
    car_no: str | None
    seat_no: str | None
    seat_count: str | None
    passenger_type_code: str | None
    received_amount: str | None
    buyer_name: str | None
    passenger_name: str | None
    train_suspension_flag: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        journey_sequence: str | None = ...,
        run_date: str | None = ...,
        train_no: str | None = ...,
        train_class_code: str | None = ...,
        train_class_name: str | None = ...,
        departure_station_code: str | None = ...,
        departure_station_name: str | None = ...,
        departure_date: str | None = ...,
        departure_time: str | None = ...,
        arrival_station_code: str | None = ...,
        arrival_station_name: str | None = ...,
        arrival_date: str | None = ...,
        arrival_time: str | None = ...,
        car_no: str | None = ...,
        seat_no: str | None = ...,
        seat_count: str | None = ...,
        passenger_type_code: str | None = ...,
        received_amount: str | None = ...,
        buyer_name: str | None = ...,
        passenger_name: str | None = ...,
        train_suspension_flag: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TripMenuContent(object):
    title: str | None
    detail: str | None
    detail_type: str | None
    active: str | None
    agree: str | None
    info: str | None
    image: str | None
    url: str | None
    raw: Mapping[str, object]
    commuter_kind_code: str | None
    pass_type: str | None
    pass_data: PassMenuData | None
    def __init__(
        self,
        title: str | None = ...,
        detail: str | None = ...,
        detail_type: str | None = ...,
        active: str | None = ...,
        agree: str | None = ...,
        info: str | None = ...,
        image: str | None = ...,
        url: str | None = ...,
        raw: Mapping[str, object] = ...,
        commuter_kind_code: str | None = ...,
        pass_type: str | None = ...,
        pass_data: PassMenuData | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TripMenuItem(object):
    title: str | None
    detail: str | None
    menu_type: str | None
    button: str | None
    contents: tuple[TripMenuContent, ...]
    url: str | None
    raw: Mapping[str, object]
    content_count: int | None
    def __init__(
        self,
        title: str | None = ...,
        detail: str | None = ...,
        menu_type: str | None = ...,
        button: str | None = ...,
        contents: tuple[TripMenuContent, ...] = ...,
        url: str | None = ...,
        raw: Mapping[str, object] = ...,
        content_count: int | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TripMenuResponse(BaseKorailResponse):
    items: tuple[TripMenuItem, ...]
    popup_message: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        items: tuple[TripMenuItem, ...] = ...,
        popup_message: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TripChangeDateResponse(BaseKorailResponse):
    last_run_date: str | None
    trip_change_dates: tuple[str, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        last_run_date: str | None = ...,
        trip_change_dates: tuple[str, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TransferStation(object):
    station_code: str | None
    station_name: str | None
    raw: collections.abc.Mapping[str, object]
    def __init__(
        self,
        station_code: str | None = ...,
        station_name: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TransferStationListResponse(BaseKorailResponse):
    stations: tuple[TransferStation, ...]
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        stations: tuple[TransferStation, ...] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class UuidResponse(BaseKorailResponse):
    verification_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        verification_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class LoginCryptoInfo(object):
    idx: str
    key: str
    pwd_aes_cphd: str
    def __init__(self, idx: str = ..., key: str = ..., pwd_aes_cphd: str = ...) -> None: ...

@dataclass(frozen=True)
class MaasCancelFeeResponse(BaseKorailResponse):
    cancel_fee: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        cancel_fee: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TravelProduct(object):
    goods_no: str | None
    name: str | None
    area_code: str | None
    area_name: str | None
    event_start_date: str | None
    event_end_date: str | None
    company_name: str | None
    info_url: str | None
    representative_fare: str | None
    description: str | None
    standard_clause_1: str | None
    standard_clause_2: str | None
    raw: Mapping[str, object]
    def __init__(
        self,
        goods_no: str | None = ...,
        name: str | None = ...,
        area_code: str | None = ...,
        area_name: str | None = ...,
        event_start_date: str | None = ...,
        event_end_date: str | None = ...,
        company_name: str | None = ...,
        info_url: str | None = ...,
        representative_fare: str | None = ...,
        description: str | None = ...,
        standard_clause_1: str | None = ...,
        standard_clause_2: str | None = ...,
        raw: Mapping[str, object] = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TravelProductSearchResponse(BaseKorailResponse):
    products: tuple[TravelProduct, ...]
    query_count: str | None
    page_count: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        products: tuple[TravelProduct, ...] = ...,
        query_count: str | None = ...,
        page_count: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class MaasCancelResponse(BaseKorailResponse):
    integrated_message_code: str | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        integrated_message_code: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class TravelProductSearchQuery(object):
    keyword: str
    keyword_field: Literal["name", "area", "theme", "category"]
    page_no: int
    function_code: str | None
    order_code: str | None
    page_size: str | None
    def __init__(
        self,
        keyword: str,
        keyword_field: Literal["name", "area", "theme", "category"] = ...,
        page_no: int = ...,
        function_code: str | None = ...,
        order_code: str | None = ...,
        page_size: str | None = ...,
    ) -> None: ...

@dataclass(frozen=True)
class AppDataResponse(BaseKorailResponse):
    disability_certification_msg: str | None
    railplus_cardinfo: str | None
    version: AppVersionInfo | None
    notice: NoticeResponse | None
    def __init__(
        self,
        h_msg_cd: str | None = ...,
        h_msg_txt: str | None = ...,
        str_result: str | None = ...,
        raw: collections.abc.Mapping[str, object] = ...,
        disability_certification_msg: str | None = ...,
        railplus_cardinfo: str | None = ...,
        version: AppVersionInfo | None = ...,
        notice: NoticeResponse | None = ...,
    ) -> None: ...

KorailSelfSeatChangeRoomClassCode = str
KorailLoginInputFlag = Literal["2", "4", "5"]
KorailRoomClassCode = Literal["1", "2"] | KorailSeatClass
KorailMileageLedger = Literal["1", "2"]
KorailMileageMovement = Literal["0", "1", "2"]
TimestampMsProvider = Callable[[], int]
RandomTextProvider = Callable[[], str]
CommuterInfoRequest = CommuterInitialRequest | CommuterPassengerRequest | CommuterTicketInquiryRequest
DynapathTokenProvider = Callable[[DynapathRequestContext], str | None]
