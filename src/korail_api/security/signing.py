"""Opt-in request signing interface; no native or enrollment implementation."""

from dataclasses import dataclass, field
from typing import Callable

from korail_api.models.errors import KorailProtocolError


@dataclass(frozen=True)
class SigningRequest:
    """Final request identity. Sensitive URL and body digest are excluded from repr."""

    method: str
    path: str
    url: str = field(repr=False)
    body_sha256: bytes = field(repr=False)


class SigningRegistrationRequired(Exception):
    """The external signer requires a separately authorized registration."""


class PreparedRequestSigner:
    """Adapt an external signer to DynapathConfig.token_provider (fail closed)."""

    def __init__(self, signer: Callable[[SigningRequest], str]):
        if not callable(signer):
            raise TypeError("signer must be callable")
        self._signer = signer

    def __call__(self, context):
        raise KorailProtocolError("Prepared request signer requires a prepared request")

    def sign(self, request: SigningRequest) -> str:
        try:
            token = self._signer(request)
        except SigningRegistrationRequired:
            error = KorailProtocolError("Request signer requires registration")
            error.code = "SIGNER_REGISTRATION_REQUIRED"
            raise error from None
        except TimeoutError:
            error = KorailProtocolError("Request signer timed out")
            error.code = "SIGNER_TIMEOUT"
            raise error from None
        except ConnectionError:
            error = KorailProtocolError("Request signer is unavailable")
            error.code = "SIGNER_UNAVAILABLE"
            raise error from None
        except Exception:
            error = KorailProtocolError("Request signer failed")
            error.code = "SIGNER_FAILED"
            raise error from None
        if not isinstance(token, str) or not token or any(c in token for c in "\r\n"):
            error = KorailProtocolError("Request signer returned an invalid token")
            error.code = "SIGNER_INVALID_TOKEN"
            raise error
        return token
