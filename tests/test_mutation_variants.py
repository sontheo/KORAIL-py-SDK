"""Compare meaningful transaction input combinations with observed wire behavior."""

import dataclasses
import json
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

import korail_api as api
from korail_api.models.records import restore

DATA = Path(__file__).parents[1] / "tests" / "fixtures"
VARIANTS = json.loads((DATA / "variant-cases.json").read_text())
BASE = json.loads((DATA / "synthetic-cases.json").read_text())


def encode(obj):
    if dataclasses.is_dataclass(obj):
        return {
            "model": type(obj).__name__,
            "fields": {field.name: encode(getattr(obj, field.name)) for field in dataclasses.fields(obj)},
        }
    if isinstance(obj, tuple):
        return {"sequence": "tuple", "items": [encode(v) for v in obj]}
    if isinstance(obj, list):
        return [encode(v) for v in obj]
    if isinstance(obj, dict):
        return {k: encode(v) for k, v in obj.items()}
    return obj


@pytest.mark.parametrize("case", VARIANTS, ids=lambda item: item["label"])
def test_mutation_variant(case):
    observed = []
    counts = Counter()
    baseline = BASE[case["method"]]["reference"]["exchanges"]

    def handle(request):
        observed.append(
            {
                "method": request.method,
                "path": request.url.path,
                "content_type": request.headers.get("content-type"),
                "query": parse_qs(request.url.query.decode(), keep_blank_values=True),
                "form": parse_qs(request.content.decode(), keep_blank_values=True),
            }
        )
        choices = [step for step in baseline if step["path"] == request.url.path]
        raw = (
            choices[min(counts[request.url.path], len(choices) - 1)]["response"]
            if choices
            else {"strResult": "SUCC"}
        )
        counts[request.url.path] += 1
        return httpx.Response(200, text=raw) if isinstance(raw, str) else httpx.Response(200, json=raw)

    config = api.KorailConfig(
        base_url="https://api.example.invalid",
        netfunnel_url="https://queue.example.invalid",
        key="SYNTHETIC-APP-KEY",
    )
    error = None
    result = None
    with api.KorailClient(config, transport=httpx.MockTransport(handle)) as client:
        client.session.current = api.KorailSession(
            "SYNTHETIC-SESSION", "SYNTHETIC-MEMBER", {}, "SYNTHETIC-MEMBER-CARD", "SYNTHETIC-CUSTOMER"
        )
        client.http.cookies.set("JSESSIONID", "SYNTHETIC-SESSION")
        try:
            result = getattr(client, case["method"])(**restore(case["arguments"]))
        except Exception as failure:
            error = type(failure).__name__
    assert observed == case["events"]
    assert error == case["error"]
    assert encode(result) == case["result"]
