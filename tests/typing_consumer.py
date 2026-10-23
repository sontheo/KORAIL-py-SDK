"""A static consumer of both supported public import namespaces."""

from typing import assert_type

from korail_api import Korail, StationDataResponse
from korail_api.maintenance import MaintenanceDeferredError, MaintenancePolicy
from korail_mobile_api import (
    KorailClient,
    KorailConfig,
    KorailPassengerCounts,
    SelfSeatChangeInfoRequest,
    TrainSearchQuery,
    TrainSearchResult,
)


def example(client: KorailClient, facade: Korail) -> TrainSearchResult:
    query = TrainSearchQuery("서울", "부산", "20991230", "090000")
    assert_type(client.get_station_data(), StationDataResponse)
    assert_type(facade.stations.names(), set[str])
    return client.search_trains(query)


config: KorailConfig = KorailConfig()
passengers = KorailPassengerCounts(adult=2, child=1)
assert_type(passengers.total, int)
room = SelfSeatChangeInfoRequest("20991230", "90001", "9001", "9002", "FUTURE")
assert_type(room.room_class_code, str | None)
SelfSeatChangeInfoRequest("20991230", "90001", "9001", "9002", 1)  # type: ignore[arg-type]


def maintenance_types(policy: MaintenancePolicy, error: MaintenanceDeferredError) -> None:
    client = KorailClient(maintenance=policy)
    assert_type(client.maintenance, MaintenancePolicy)
    assert_type(error.next_probe_at, float)
    assert_type(error.retry_after, float)
    assert_type(policy.failure("https://api.example.invalid", error), float | None)
    client.close()
