"""Shared value validation."""

from __future__ import annotations

import re
from enum import Enum

from korail_py_sdk.models import errors as E


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise E.KorailProtocolError(f"{label} must be nonempty text")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise E.KorailProtocolError(f"{label} contains invalid text") from error
    return value


def number(value, label, *, minimum=0):
    if type(value) is bool or not isinstance(value, (str, int)):
        raise E.KorailProtocolError(f"{label} must be an integer")
    if isinstance(value, str) and re.fullmatch(r"-?[0-9]+", value) is None:
        raise E.KorailProtocolError(f"{label} must be an ASCII integer")
    try:
        result = int(value)
    except ValueError as error:
        raise E.KorailProtocolError(f"{label} must be an integer") from error
    if result < minimum:
        raise E.KorailProtocolError(
            f"{label} must be positive" if minimum == 1 else f"{label} is below its minimum"
        )
    return result


def _value(item):
    return item.value if isinstance(item, Enum) else item
