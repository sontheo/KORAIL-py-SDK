"""Attach concrete public type information from the local interface contract."""

from __future__ import annotations

import collections
import inspect
import re
import typing
from datetime import datetime
from types import TracebackType

import httpx

from korail_api.models import records


def resolve(text, namespace=None):
    if text == "<class 'inspect._empty'>":
        return inspect.Signature.empty
    text = re.sub(r"<(?:class|enum) '([^']+)'>", r"\1", text)
    text = text.replace("NoneType", "None").replace("datetime.datetime", "datetime")
    names = {
        **vars(records),
        "httpx": httpx,
        "datetime": datetime,
        "TracebackType": TracebackType,
        "typing": typing,
        "collections": collections,
        "Self": typing.Self,
        **(namespace or {}),
    }
    # The expressions come exclusively from bundled package data, never an HTTP
    # response, environment value, or caller-supplied annotation.
    return eval(text, names)


def attach(function, spec, namespace):
    # Type aliases are public values, not functions. Python 3.14's unified
    # Union objects do not permit assigning function annotation attributes.
    if typing.get_origin(function) is not None:
        return
    annotations = {
        p["name"]: resolve(p["annotation"], namespace)
        for p in spec.get("parameters", ())
        if p["annotation"] != "<class 'inspect._empty'>"
    }
    annotations["return"] = resolve(spec.get("return", "None"), namespace)
    function.__annotations__ = annotations
    signature = getattr(function, "__signature__", None)
    if signature is not None:
        function.__signature__ = signature.replace(
            parameters=[
                p.replace(annotation=annotations.get(p.name, inspect.Parameter.empty))
                for p in signature.parameters.values()
            ],
            return_annotation=annotations["return"],
        )


def install(namespace):
    from korail_api.services import authentication as session

    for name, spec in records.CONTRACT["client"].items():
        attach(getattr(namespace["KorailClient"], name), spec, namespace)
    for path, spec in records.CONTRACT.get("signatures", {}).items():
        parts = path.split(".")
        target = session if parts[0] == "session" else namespace[parts[0]]
        for part in parts[1:]:
            target = getattr(target, part)
        if inspect.ismethod(target):
            target = target.__func__
        attach(target, spec, namespace)
    for name, spec in records.CONTRACT["models"].items():
        cls = records.REGISTRY[name]
        for member, info in spec["members"].items():
            target = vars(cls).get(member)
            if isinstance(target, property):
                target = target.fget
            elif isinstance(target, (classmethod, staticmethod)):
                target = target.__func__
            if target is not None:
                attach(target, info, namespace)
