"""Pure form adapters; they never construct connection pools or send requests."""

from types import SimpleNamespace

from korail_api.api.client import KorailClient, _signature, order_fields
from korail_api.models.records import CONTRACT
from korail_api.protocol.schema import load
from korail_api.services.operations import prepare


def build(operation, config, supplied):
    context = object.__new__(KorailClient)
    context.config = config
    context.session = SimpleNamespace(current=None)
    signature = _signature(CONTRACT["client"][operation])
    args = signature.bind(context, **supplied)
    args.apply_defaults()
    values = dict(args.arguments)
    del values["self"]
    steps = [row for row in load("requests")[operation]["exchanges"] if row["path"] != "/ts.wseq"]
    forms = [context._build(row["form"], values) for row in steps]
    steps, forms = prepare(context, operation, values, steps, forms)
    is_query = steps[-1]["method"] == "GET"
    order = list(steps[-1].get("field_order", {}).get("query" if is_query else "form", ()))
    if operation == "reserve_transfer":
        forms[-1]["txtGdNo"] = values["legs"][0].goods_no or ""
        if "txtGdNo" not in order:
            order.insert(order.index("hidFreeFlg"), "txtGdNo")

    def encode(value):
        return str(value).lower() if isinstance(value, bool) else str(value)

    result = {}
    for key, val in forms[-1].items():
        if val is None or (
            val == ""
            and not is_query
            and not (
                (operation == "get_limousine_schedules" and key in {"trnNo", "rsvSaleDvCd"})
                or (operation == "reserve_transfer" and key == "txtGdNo")
            )
        ):
            continue
        if isinstance(val, (tuple, list)):
            result[key] = encode(val[0]) if len(val) == 1 else [encode(v) for v in val]
        else:
            result[key] = encode(val)
    return order_fields(result, order)
