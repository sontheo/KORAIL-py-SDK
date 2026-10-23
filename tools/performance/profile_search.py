"""Profile complete mock searches using the selected public implementation."""

import cProfile
import json
import pstats
from pathlib import Path

import httpx

import korail_api as api

ROOT = Path(__file__).resolve().parents[2]
case = json.loads((ROOT / "tests/fixtures/synthetic-cases.json").read_text())["search_trains"]
raw = next(x["response"] for x in case["reference"]["exchanges"] if x["host"] == "api.example.invalid")
client = api.KorailClient(
    api.KorailConfig(netfunnel_enabled=False, transport_profile="httpx"),
    transport=httpx.MockTransport(lambda r: httpx.Response(200, json=raw)),
)
try:
    query = api.TrainSearchQuery("서울", "부산", "20991230", "090000")
    for _ in range(50):
        client.search_trains(query)
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(2000):
        client.search_trains(query)
    profiler.disable()
finally:
    client.close()
stats = pstats.Stats(profiler)
rows = [
    {
        "file": filename,
        "line": line,
        "function": name,
        "primitive_calls": cc,
        "calls": nc,
        "self_s": tt,
        "cumulative_s": ct,
    }
    for (filename, line, name), (cc, nc, tt, ct, callers) in stats.stats.items()
]
print(
    json.dumps(
        {
            "implementation": str(Path(api.__file__).resolve()),
            "searches": 2000,
            "total_s": stats.total_tt,
            "functions": sorted(rows, key=lambda r: r["self_s"], reverse=True),
        },
        indent=2,
    )
)
