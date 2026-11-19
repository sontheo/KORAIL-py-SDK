"""Synchronous KORAIL protocol client and public value objects."""

from typing import Callable, Literal

from korail_py_sdk.api.annotations import install as _install_annotations
from korail_py_sdk.api.client import KorailClient
from korail_py_sdk.api.facade import Korail, ReservationResource, StationResource, TicketResource, TrainResource
from korail_py_sdk.configuration.device import build_config_from_env, build_config_from_profile
from korail_py_sdk.messages.catalog import get_error_message, resolve_error_message
from korail_py_sdk.models import errors
from korail_py_sdk.models.records import CONTRACT, REGISTRY

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

__version__ = "0.1.1"
__all__ = CONTRACT["exports"]

_install_annotations(globals())
