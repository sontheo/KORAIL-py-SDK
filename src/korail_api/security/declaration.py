"""Software declaration tokens; no enrollment or hardware attestation.

The wire format is documented in docs/PROVENANCE.md. The build constant below
is a public protocol parameter, not a user credential or device secret.
"""

from __future__ import annotations

import base64
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from hashlib import sha256

_BUILD_CONSTANT = b"9a330fd663b62c5f888a7ce76ac7202d93f646b4e0bd605cd4183278ca4ca888"
_DIGITS = "TeFOuQBxj1qRUHwKkymSY8l3psvCzAL5tofNcihg9WDG072EZ4bVad6rJnPXIM"


def encode_declaration(payload: bytes, nonce: int) -> str:
    """Encode a declaration envelope, including the leading exclamation mark."""
    if not isinstance(payload, bytes) or not payload.startswith(b"!v=2&"):
        raise ValueError("A v2 declaration envelope is required")
    if type(nonce) is not int or not 0 <= nonce < 2**32:
        raise ValueError("Declaration nonce must be an unsigned 32-bit integer")
    prefix = nonce.to_bytes(4, "little")
    encrypted = bytearray()
    for offset in range(0, len(payload), 32):
        mask = sha256(_BUILD_CONSTANT + prefix + (offset // 32).to_bytes(4, "big")).digest()
        encrypted.extend(value ^ mask[index] for index, value in enumerate(payload[offset : offset + 32]))
    frame = prefix + sha256(_BUILD_CONSTANT + prefix + encrypted).digest()[:3] + encrypted
    output = ["201"]
    for offset in range(0, len(frame), 4):
        word = frame[offset : offset + 4]
        number = int.from_bytes(word, "big")
        width = (0, 2, 3, 5, 6)[len(word)]
        digits = [_DIGITS[0]] * width
        for index in range(width - 1, -1, -1):
            number, digit = divmod(number, 62)
            digits[index] = _DIGITS[digit]
        output.extend(digits)
    return "".join(output)


@dataclass(frozen=True)
class DeclarationTokenProvider:
    """One software device identity with fresh timestamps and nonces per call.

    The default board is unspecified; callers can supply accurate device facts.
    Synthetic identity and declaration values do not establish attestation.
    """

    device_id: str = field(default_factory=lambda: secrets.token_hex(8), repr=False)
    model: str = "SM-S948N"
    release: str = "17"
    manufacturer: str = "samsung"
    board: str = ""
    sdk_int: int = 37
    strongbox: bool = False
    timestamp_ms_provider: Callable[[], int] | None = field(default=None, repr=False, compare=False)
    nonce_provider: Callable[[], int] | None = field(default=None, repr=False, compare=False)
    _managed: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        for value in (self.device_id, self.model, self.release, self.manufacturer, self.board):
            if not isinstance(value, str) or len(value) > 1024:
                raise ValueError("Invalid declaration device fact")
        if not self.device_id or not self.model or not self.release:
            raise ValueError("Declaration identity, model and release are required")
        if type(self.sdk_int) is not int or not 1 <= self.sdk_int < 2**31:
            raise ValueError("Invalid declaration SDK level")
        if type(self.strongbox) is not bool:
            raise ValueError("Declaration StrongBox flag must be boolean")
        for provider in (self.timestamp_ms_provider, self.nonce_provider):
            if provider is not None and not callable(provider):
                raise TypeError("Declaration input providers must be callable")

    def __call__(self, context=None) -> str:
        stamp = self.timestamp_ms_provider() if self.timestamp_ms_provider else time.time_ns() // 1_000_000
        nonce = self.nonce_provider() if self.nonce_provider else secrets.randbits(32)
        if type(stamp) is not int or not 0 <= stamp < 2**63:
            raise ValueError("Invalid declaration timestamp")
        facts = ["!v=2", "es=288904575606514493", f"ts={stamp}", "st=Android", "sv=2.0.1", "ai=korailplus"]
        for name, value in zip(
            ("os", "dm", "iid", "mf", "bd"),
            (self.release, self.model, self.device_id, self.manufacturer, self.board),
        ):
            encoded = base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")
            facts.append(f"{name}={encoded}")
        facts.extend(
            (
                f"sl={self.sdk_int}",
                f"sb={int(self.strongbox)}",
                "kl=990094375841594426",
                "ec=978212327729758430",
            )
        )
        return encode_declaration("&".join(facts).encode("ascii"), nonce)
