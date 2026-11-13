"""Compare the new decoder with previously captured synthetic oracle outputs."""

import dataclasses
import json
from collections import Counter
from pathlib import Path

from korail_api.models.records import REGISTRY
from korail_api.protocol.codec import decode

ROOT = Path(__file__).resolve().parents[2]


def encode(obj):
    if dataclasses.is_dataclass(obj):
        return {
            "model": type(obj).__name__,
            "fields": {f.name: encode(getattr(obj, f.name)) for f in dataclasses.fields(obj)},
        }
    if isinstance(obj, tuple):
        return {"sequence": "tuple", "items": [encode(v) for v in obj]}
    if isinstance(obj, list):
        return [encode(v) for v in obj]
    if isinstance(obj, dict):
        return {k: encode(v) for k, v in obj.items()}
    return obj


def run():
    rows = json.loads((ROOT / "tools/validation/observations/decoder-observations.json").read_text())
    counts = Counter()
    failures = []
    seen = set()
    for row in rows:
        expected = row["result"]
        if not isinstance(expected, dict) or expected.get("model") not in REGISTRY:
            continue
        raw = expected["fields"].get("raw")
        if not isinstance(raw, dict):
            continue
        key = json.dumps(expected, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        name = expected["model"]
        try:
            actual = encode(decode(name, raw))
            different = [k for k, v in expected["fields"].items() if actual["fields"].get(k) != v]
            if different:
                counts["different"] += 1
                failures.append({"model": name, "fields": different, "function": row["function"]})
            else:
                counts["equal"] += 1
        except Exception as error:
            counts["error"] += 1
            failures.append({"model": name, "error": str(error), "function": row["function"]})
    grouped = Counter((r["model"], tuple(r.get("fields", [])), r.get("error", "")) for r in failures)
    print(dict(counts))
    for key, count in grouped.most_common(35):
        print(count, key)
    return int(bool(failures) or not counts["equal"])


if __name__ == "__main__":
    raise SystemExit(run())
