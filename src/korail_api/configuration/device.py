"""Explicit configuration profiles; no implicit credential loading."""

import os
from dataclasses import replace

from korail_api.models.records import KorailConfig, KorailDeviceProfile


def build_dalvik_user_agent(
    release="17", model="SM-S948N", build_id="CP2A.260605.016", *, os_release=None, device_model=None
):
    if os_release is not None:
        release = os_release
    if device_model is not None:
        model = device_model
    pieces = [f"Android {release or '1.0'}"]
    if model:
        pieces.append(model)
    suffix = "; ".join(pieces)
    if build_id:
        suffix += " Build/" + build_id
    return f"Dalvik/2.1.0 (Linux; U; {suffix})"


def build_config_from_profile(profile, *, base=None):
    config = base or KorailConfig()
    from korail_api.security.declaration import DeclarationTokenProvider
    from korail_api.security.diagnostic import diagnostic_token

    if config.dynapath.token_provider not in (None, diagnostic_token) and not isinstance(
        config.dynapath.token_provider, DeclarationTokenProvider
    ):
        raise ValueError("A device profile requires configurable DynaPath settings")
    token = replace(config.dynapath, device_name=profile.model, os_version=profile.android_release)
    if isinstance(token.token_provider, DeclarationTokenProvider):
        token = replace(
            token,
            token_provider=replace(
                token.token_provider,
                device_id=profile.device_id,
                model=profile.model,
                release=profile.android_release,
                sdk_int=profile.android_sdk_int,
                manufacturer=("samsung" if profile.model.startswith("SM-") else "")
                if token.token_provider._managed
                else token.token_provider.manufacturer,
            ),
        )
    if token.token_settings is not None:
        token = replace(
            token,
            token_settings=replace(
                token.token_settings,
                device_id=profile.device_id,
                device_model=profile.model,
                os_version=profile.android_release,
            ),
        )
    return replace(
        config,
        device_width=profile.width,
        device_height=profile.height,
        android_sdk_int=profile.android_sdk_int,
        dynapath=token,
        netfunnel_user_agent=build_dalvik_user_agent(profile.android_release, profile.model, profile.build_id),
    )


def build_config_from_env(*, prefix="KORAIL_", base=None):
    def required(suffix):
        name = prefix + suffix
        val = os.environ.get(name)
        if not val:
            raise RuntimeError(f"{name} is required for KORAIL live DynaPath")
        return val

    def integer(suffix, fallback):
        try:
            return int(os.environ.get(prefix + suffix, fallback))
        except ValueError:
            raise ValueError("Invalid device configuration integer") from None

    config = base or KorailConfig()
    profile = KorailDeviceProfile(
        required("DYNAPATH_DEVICE_ID"),
        required("DYNAPATH_DEVICE_MODEL"),
        required("DYNAPATH_OS_VERSION"),
        required("ANDROID_BUILD_ID"),
        android_sdk_int=integer("ANDROID_SDK_INT", config.android_sdk_int),
        width=integer("DEVICE_WIDTH", config.device_width),
        height=integer("DEVICE_HEIGHT", config.device_height),
    )
    changes = {
        "dynapath_mode": os.environ.get(prefix + "DYNAPATH_MODE", config.dynapath_mode),
        "transport_profile": os.environ.get(prefix + "TRANSPORT_PROFILE", config.transport_profile),
        "proxy": os.environ.get(prefix + "PROXY") or None,
        "base_url": os.environ.get(prefix + "BASE_URL", config.base_url),
        "advertising_id": os.environ.get(prefix + "ADVERTISING_ID", config.advertising_id),
        "user_agent": os.environ.get(prefix + "USER_AGENT", config.user_agent),
    }
    result = build_config_from_profile(profile, base=replace(config, **changes))
    queue_agent = os.environ.get(prefix + "NETFUNNEL_USER_AGENT")
    if queue_agent:
        result = replace(result, netfunnel_user_agent=queue_agent)
    app_state = os.environ.get(prefix + "DYNAPATH_AS_VALUE")
    if app_state is not None and result.dynapath.token_settings is not None:
        result = replace(
            result,
            dynapath=replace(
                result.dynapath, token_settings=replace(result.dynapath.token_settings, as_value=app_state)
            ),
        )
    return result
