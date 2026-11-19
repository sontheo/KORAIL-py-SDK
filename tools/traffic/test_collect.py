import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

spec = importlib.util.spec_from_file_location("traffic_collect", Path(__file__).with_name("collect.py"))
traffic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(traffic)


def response(metric, *entries):
    return {
        metric: [
            {"timestamp": f"{date}T00:00:00Z", "count": count, "uniques": unique}
            for date, count, unique in entries
        ]
    }


def test_merge_replaces_overlaps_and_preserves_history(tmp_path):
    path = tmp_path / "traffic.json"
    old = {
        "views": response("views", ("2026-01-01", 3, 2), ("2026-01-02", 5, 3)),
        "clones": response("clones", ("2026-01-01", 2, 1)),
    }
    with patch.object(traffic, "fetch", side_effect=lambda repo, token, metric: old[metric]):
        traffic.collect(path, "owner/repo", "token")
    new = {"views": response("views", ("2026-01-02", 7, 4)), "clones": response("clones", ("2026-01-02", 4, 2))}
    with patch.object(traffic, "fetch", side_effect=lambda repo, token, metric: new[metric]):
        traffic.collect(path, "owner/repo", "token")
        before = path.read_bytes()
        modified = path.stat().st_mtime_ns
        traffic.collect(path, "owner/repo", "token")
    archive = json.loads(before)
    assert archive["views"] == {
        "2026-01-01": {"count": 3, "uniques": 2},
        "2026-01-02": {"count": 7, "uniques": 4},
    }
    assert archive["clones"] == {
        "2026-01-01": {"count": 2, "uniques": 1},
        "2026-01-02": {"count": 4, "uniques": 2},
    }
    assert path.read_bytes() == before
    assert path.stat().st_mtime_ns == modified


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        {},
        {"clones": [{"timestamp": "bad", "count": 1, "uniques": 1}]},
        response("clones", ("2026-01-01", 1, 2)),
        response("clones", ("2026-01-01", 1, 1), ("2026-01-01", 1, 1)),
    ],
)
def test_invalid_response_preserves_archive(tmp_path, invalid):
    path = tmp_path / "traffic.json"
    path.write_text(json.dumps({"version": 1, "repository": "owner/repo", "views": {}, "clones": {}}))
    before = path.read_bytes()
    with patch.object(
        traffic,
        "fetch",
        side_effect=lambda repo, token, metric: (
            response("views", ("2026-01-01", 4, 2)) if metric == "views" else invalid
        ),
    ):
        with pytest.raises(ValueError):
            traffic.collect(path, "owner/repo", "token")
    assert path.read_bytes() == before


def test_api_failure_does_not_create_archive(tmp_path):
    path = tmp_path / "traffic.json"
    with patch.object(traffic, "fetch", side_effect=ValueError("API error")), pytest.raises(ValueError):
        traffic.collect(path, "owner/repo", "token")
    assert not path.exists()
