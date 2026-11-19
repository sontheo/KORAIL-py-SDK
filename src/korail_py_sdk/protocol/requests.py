"""Compile immutable field mappings once and render fresh forms per request."""

import time
from dataclasses import dataclass
from enum import Enum

from korail_py_sdk.models.errors import KorailProtocolError

CONFIG_FIELDS = {"Device": "device", "Version": "version", "AppVersion": "app_version", "Key": "key"}
_PLANS = {}


def read_path(obj, path):
    for part in path:
        if obj is None:
            return None
        if isinstance(obj, dict):
            obj = obj.get(part)
        elif isinstance(part, int):
            if not isinstance(obj, (list, tuple, str)):
                raise KorailProtocolError("An ordered collection is required")
            obj = obj[part] if len(obj) > part else None
        else:
            obj = getattr(obj, part, None)
    return obj.value if isinstance(obj, Enum) else obj


def source(path):
    if len(path) == 1:
        key = path[0]

        def get(context, arguments):
            value = arguments.get(key)
            return value.value if isinstance(value, Enum) else value

        return get
    if len(path) == 2 and isinstance(path[1], str):
        key, attribute = path

        def get(context, arguments):
            obj = arguments.get(key)
            value = obj.get(attribute) if isinstance(obj, dict) else getattr(obj, attribute, None)
            return value.value if isinstance(value, Enum) else value

        return get

    def get(context, arguments):
        return read_path(arguments, path)

    return get


def expression(term):
    if "parts" in term:
        parts = tuple(part if isinstance(part, str) else source(part["source"]) for part in term["parts"])

        def composite(context, arguments):
            return "".join(
                part if isinstance(part, str) else str(part(context, arguments) or "") for part in parts
            )

        return composite
    getter = source(term["source"])
    transform = term.get("transform")
    template = term.get("template")
    if transform is None and template is None:
        return getter

    def converted(context, arguments):
        value = getter(context, arguments)
        if value is None:
            return None
        if transform == "yn":
            value = "Y" if value else "N"
        elif transform == "lower":
            value = str(value).lower()
        if template:
            value = template[0] + str(value) + template[1]
        return value

    return converted


def member_card(context, arguments):
    return context.session.current.member_card_no if context.session.current else None


def customer(context, arguments):
    return context._require_customer_no("Account query")


def timestamp(context, arguments):
    value = arguments.get("timestamp_ms")
    return int(time.time() * 1000) if value is None else value


@dataclass(frozen=True, slots=True)
class FormPlan:
    template: dict
    config_fields: tuple
    fields: tuple
    has_language: bool

    def render(self, context, arguments, include_language):
        if not self.template:
            return {}
        result = self.template.copy()
        for key, attribute in self.config_fields:
            value = getattr(context.config, attribute)
            if value is None:
                result.pop(key, None)
            else:
                result[key] = value
        if self.has_language:
            if include_language and context.config.lang not in (None, ""):
                result["lang"] = context.config.lang
            else:
                result.pop("lang", None)
        for key, getter in self.fields:
            value = getter(context, arguments)
            if value is None:
                result.pop(key, None)
            else:
                result[key] = value
        return result


def compile_form(recipe):
    identity = id(recipe)
    cached = _PLANS.get(identity)
    if cached is not None:
        return cached[1]
    config = tuple((key, CONFIG_FIELDS[key]) for key in recipe if key in CONFIG_FIELDS)
    template = dict.fromkeys(key for key, _ in config)
    has_language = "Device" in recipe
    if has_language:
        template["lang"] = None
    fields = []
    for key, term in recipe.items():
        if key in CONFIG_FIELDS:
            continue
        if "source" in term or "parts" in term:
            template[key] = None
            fields.append((key, expression(term)))
            continue
        literal = term.get("literal", [])
        getter = (
            member_card
            if literal == ["SYNTHETIC-MEMBER-CARD"]
            else customer
            if literal == ["SYNTHETIC-CUSTOMER"]
            else timestamp
            if key == "timeStamp"
            else None
        )
        if getter:
            template[key] = None
            fields.append((key, getter))
        else:
            if any("SYNTHETIC" in str(value) or "시험역" in str(value) for value in literal):
                raise KorailProtocolError("Protocol recipe contains an unresolved synthetic value")
            template[key] = literal[0] if len(literal) == 1 else tuple(literal)
    plan = FormPlan(template, config, tuple(fields), has_language)
    if len(_PLANS) >= 512:
        del _PLANS[next(iter(_PLANS))]
    _PLANS[identity] = (recipe, plan)
    return plan
