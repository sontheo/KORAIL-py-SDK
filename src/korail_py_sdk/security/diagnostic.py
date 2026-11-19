"""Serialize SDK 2 diagnostic metadata without claiming device registration."""

import base64
import re

NATIVE_UNAVAILABLE_STATE = 165489088780120535


def urlsafe_b64(data):
    if not isinstance(data, bytes):
        raise TypeError("Diagnostic metadata must be bytes")
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def diagnostic_header(
    state,
    app_id="korailplus",
    *,
    os_version=None,
    device_model=None,
    install_id=None,
    manufacturer=None,
    board=None,
    sdk_int=None,
):
    if type(state) is not int:
        raise TypeError("State must be an integer")
    if not -(1 << 63) <= state < 1 << 63:
        raise ValueError("State is outside signed 64-bit range")
    if not isinstance(app_id, str):
        raise TypeError("Application identifier must be text")
    if re.fullmatch(r"[A-Za-z0-9._-]+", app_id) is None:
        raise ValueError("Invalid application identifier")
    fields = [("v", "2"), ("es", str(state)), ("st", "Android"), ("sv", "2.0.1"), ("ai", app_id)]
    for key, data in zip(
        ("os", "dm", "iid", "mf", "bd"), (os_version, device_model, install_id, manufacturer, board)
    ):
        if data is not None:
            fields.append((key, urlsafe_b64(data)))
    if sdk_int is not None:
        if type(sdk_int) is not int:
            raise TypeError("SDK version must be an integer")
        if not 0 <= sdk_int < 1 << 31:
            raise ValueError("SDK version is outside signed 32-bit range")
        fields.append(("sl", str(sdk_int)))
    return "2!" + "&".join(f"{k}={v}" for k, v in fields)


def diagnostic_token(context=None):
    # This is an observed compatibility marker, not a native or hardware signature.
    # Restrict it to the read-only endpoint for which acceptance was measured.
    if context is not None and context.path == "/classes/com.korail.mobile.seatMovie.ScheduleView":
        return "201"
    return diagnostic_header(NATIVE_UNAVAILABLE_STATE)
