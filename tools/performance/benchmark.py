"""Benchmark model decoding, token generation and mock searches offline."""

import json
import statistics
import time
from pathlib import Path

import httpx

import korail_api as api
from korail_api.security.legacy import generate_dynapath_token

ROOT = Path(__file__).resolve().parents[2]
case = json.loads((ROOT / "tests/fixtures/synthetic-cases.json").read_text())["search_trains"]
raw = next(x["response"] for x in case["reference"]["exchanges"] if x["host"] == "api.example.invalid")
train_raw = raw["trn_infos"]["trn_info"][0]
settings = api.DynapathTokenSettings(
    device_id="SYNTHETIC-DEVICE",
    as_value="SYNTHETIC-AS",
    app_start_ts="1700000000000",
    os_version="17",
    device_model="SYNTHETIC-MODEL",
)
config = api.KorailConfig(netfunnel_enabled=False, transport_profile="httpx")
client = api.KorailClient(config, transport=httpx.MockTransport(lambda request: httpx.Response(200, json=raw)))
query = api.TrainSearchQuery("서울", "부산", "20991230", "090000")


def measure(function, count):
    for i in range(20):
        function(i)
    samples = []
    for _ in range(5):
        start = time.perf_counter_ns()
        for i in range(count):
            function(i)
        samples.append((time.perf_counter_ns() - start) / count / 1000)
    return {
        "median_us": round(statistics.median(samples), 3),
        "samples_us": [round(v, 3) for v in samples],
        "iterations_per_sample": count,
    }


try:
    result = {
        "implementation": str(Path(api.__file__).resolve()),
        "train_decode": measure(lambda i: api.TrainSummary.from_raw(train_raw), 2000),
        "legacy_token": measure(
            lambda i: generate_dynapath_token(settings, timestamp_ms=1700000000000 + i, random_text="aB12"),
            1000,
        ),
        "mock_search": measure(lambda i: client.search_trains(query), 500),
    }
finally:
    client.close()
print(json.dumps(result, indent=2))
