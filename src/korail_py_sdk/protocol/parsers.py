"""Adapters for existing parser imports; decoding is owned by the schema engine."""

from collections.abc import Mapping

from korail_py_sdk.models.records import REGISTRY
from korail_py_sdk.protocol.codec import decode
from korail_py_sdk.protocol.schema import load
from korail_py_sdk.transport.http import parse_base_response


def _validate_envelope(raw):
    parse_base_response(raw)
    return raw.get("strResult") == "FAIL"


def install(namespace, module_name):
    for name, spec in load("parser-functions").items():
        target = spec.get("result")
        if not name.startswith("parse_") or target not in REGISTRY:
            continue

        def parse(response=None, *, raw=None, __target=target, __name=name, **options):
            source = raw if raw is not None else response.raw if hasattr(response, "raw") else response
            from korail_py_sdk.api.client import KorailClient

            result = KorailClient._parse_mutation_response(source, lambda payload: decode(__target, payload))
            if __name == "parse_existing_reservation_hold_response":
                from korail_py_sdk.services.operations import finish

                result = finish(None, "get_reservation_hold", options, result)
            return result

        parse.__name__ = name
        parse.__qualname__ = name
        parse.__module__ = module_name
        parse.__annotations__ = {
            "response": Mapping[str, object] | REGISTRY["BaseKorailResponse"] | None,
            "raw": Mapping[str, object] | None,
            "return": REGISTRY[target],
        }
        namespace[name] = parse
