"""Compare complete mock searches at several response sizes; no live traffic."""

import copy
import json
import statistics
import time
from pathlib import Path

import httpx

import korail_api as api

ROOT = Path(__file__).resolve().parents[2]
case = json.loads((ROOT / "tests/fixtures/synthetic-cases.json").read_text())["search_trains"]
base = next(row["response"] for row in case["reference"]["exchanges"] if row["host"] == "api.example.invalid")
results = []
for rows, iterations in ((1, 500), (10, 200), (50, 100)):
    raw = copy.deepcopy(base)
    raw["trn_infos"]["trn_info"] *= rows
    seen = [0]

    def handle(request):
        seen[0] += 1
        return httpx.Response(200, json=raw)

    client = api.KorailClient(
        api.KorailConfig(netfunnel_enabled=False, transport_profile="httpx"),
        transport=httpx.MockTransport(handle),
    )
    query = api.TrainSearchQuery("서울", "부산", "20991230", "090000")
    try:
        for _ in range(30):
            assert len(client.search_trains(query).trains) == rows
        samples = []
        before = seen[0]
        for _ in range(5):
            start = time.perf_counter_ns()
            for _ in range(iterations):
                client.search_trains(query)
            samples.append((time.perf_counter_ns() - start) / iterations / 1000)
        assert seen[0] - before == 5 * iterations
        results.append(
            {
                "rows": rows,
                "iterations_per_sample": iterations,
                "median_us": round(statistics.median(samples), 3),
                "samples_us": [round(s, 3) for s in samples],
            }
        )
    finally:
        client.close()
print(json.dumps({"implementation": str(Path(api.__file__).resolve()), "samples": results}, indent=2))
