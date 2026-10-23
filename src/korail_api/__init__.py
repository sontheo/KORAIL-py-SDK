"""Synchronous KORAIL protocol client and public value objects."""

from typing import Callable, Literal

from korail_api.api.annotations import install as _install_annotations
from korail_api.api.client import KorailClient
from korail_api.api.facade import Korail, ReservationResource, StationResource, TicketResource, TrainResource
from korail_api.configuration.device import build_config_from_env, build_config_from_profile
from korail_api.messages.catalog import get_error_message, resolve_error_message
from korail_api.models import errors
from korail_api.models.records import CONTRACT, REGISTRY

globals().update(REGISTRY)
globals().update({name: getattr(errors, name) for name in CONTRACT["errors"]})

# Type aliases do not carry executable implementation. Preserve their imports
# while runtime validation remains in the request and decoding engines.

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

__version__ = "0.1.0"
__all__ = CONTRACT["exports"]

_install_annotations(globals())
