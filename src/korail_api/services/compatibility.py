"""Observed ordinary-reservation wire profile, selected before transmission."""

from korail_api.models.records import _DefaultProtocolVersion
from korail_api.security.declaration import DeclarationTokenProvider


def uses_declaration(config):
    return config.dynapath.enabled and isinstance(config.dynapath.token_provider, DeclarationTokenProvider)


def ordinary_reservation(config, arguments, steps, forms):
    if (
        not uses_declaration(config)
        or steps[-1]["path"] not in config.dynapath.allowlist_paths
        or arguments.get("seats")
        or getattr(arguments["job_type"], "value", arguments["job_type"]) != "1101"
    ):
        return steps, forms
    original = forms[-1]
    # These are protocol fields, including deliberately empty second-leg slots.
    keys = (
        "Device Version Key txtMenuId txtJobId txtGdNo hidFreeFlg txtTotPsgCnt "
        "txtSeatAttCd1 txtSeatAttCd2 txtSeatAttCd3 txtSeatAttCd4 txtSeatAttCd5 "
        "txtStndFlg txtSrcarCnt txtJrnyCnt txtJrnySqno1 txtJrnyTpCd1 txtDptDt1 "
        "txtDptRsStnCd1 txtDptTm1 txtArvRsStnCd1 txtTrnNo1 txtRunDt1 txtTrnClsfCd1 "
        "txtTrnGpCd1 txtPsrmClCd1 txtChgFlg1 txtJrnySqno2 txtJrnyTpCd2 txtDptDt2 "
        "txtDptRsStnCd2 txtDptTm2 txtArvRsStnCd2 txtTrnNo2 txtRunDt2 txtTrnClsfCd2 "
        "txtPsrmClCd2 txtChgFlg2"
    ).split()
    form = {key: original.get(key, "") for key in keys}
    form.update(txtSrcarCnt="0", txtChgFlg1="", txtSeatAttCd4=arguments.get("seat_attribute_code") or "015")
    if isinstance(config.version, _DefaultProtocolVersion):
        form["Version"] = "250722001"
    if config.lang is not None:
        form["lang"] = config.lang
    if config.app_version not in (None, "7.0.10"):
        form["AppVersion"] = config.app_version
    passengers = sorted(
        (
            str(value),
            str(original[f"txtDiscKndCd{key.removeprefix('txtPsgTpCd')}"]),
            original[f"txtCompaCnt{key.removeprefix('txtPsgTpCd')}"],
        )
        for key, value in original.items()
        if key.startswith("txtPsgTpCd")
    )
    for index, (kind, discount, count) in enumerate(passengers, 1):
        form.update(
            {f"txtPsgTpCd{index}": kind, f"txtDiscKndCd{index}": discount, f"txtCompaCnt{index}": count}
        )
        form.update({f"txtCard{part}_{index}": "" for part in ("Code", "No", "Pw")})
    step = dict(steps[-1], method="GET", field_order={"query": list(form), "form": list(form)})
    return [*steps[:-1], step], [*forms[:-1], form]
