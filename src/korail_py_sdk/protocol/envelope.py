"""Convert the common response envelope once, preserving the original object."""

from collections.abc import Mapping

from korail_py_sdk.models.errors import KorailProtocolError
from korail_py_sdk.models.records import BaseKorailResponse


def decode_envelope(raw):
    if not isinstance(raw, Mapping):
        error = KorailProtocolError("Response JSON must be an object")
        error.raw = raw
        raise error
    fields = []
    for key in ("h_msg_cd", "h_msg_txt", "strResult"):
        value = raw.get(key)
        if value is not None and type(value) is not str:
            try:
                if type(value) is not int:
                    raise ValueError
                value = str(value)
            except ValueError:
                error = KorailProtocolError("Invalid response envelope field")
                error.raw = raw
                raise error from None
        fields.append(value)
    return BaseKorailResponse(fields[0], fields[1], fields[2], raw)
