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
        "count": sum(count for _, count, _ in entries),
        "uniques": max((unique for _, _, unique in entries), default=0),
        metric: [
            {"timestamp": f"{date}T00:00:00Z", "count": count, "uniques": unique}
            for date, count, unique in entries
        ],
    }


def test_migrates_and_merges_without_losing_old_dates(tmp_path):
    path = tmp_path / "traffic.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "repository": "owner/repo",
                "views": {"2026-01-01": {"count": 3, "uniques": 2}, "2026-01-02": {"count": 5, "uniques": 3}},
                "clones": {"2026-01-01": {"count": 2, "uniques": 1}},
            }
        )
    )
    data = {
        "views": response("views", ("2026-01-02", 7, 4)),
        "clones": response("clones", ("2026-01-02", 4, 2)),
    }
    with patch.object(traffic, "fetch", side_effect=lambda repo, token, metric: data[metric]):
        traffic.collect(path, "owner/repo", "token")
        traffic.collect(path, "owner/repo", "token")
    archive = json.loads(path.read_text())
    assert archive["version"] == 2
    assert archive["daily"] == {
        "2026-01-01": {"views": {"count": 3, "uniques": 2}, "clones": {"count": 2, "uniques": 1}},
        "2026-01-02": {"views": {"count": 7, "uniques": 4}, "clones": {"count": 4, "uniques": 2}},
    }
    (snapshot,) = archive["rolling_14_days"].values()
    assert snapshot["views"] == {"count": 7, "uniques": 4}
    assert snapshot["clones"] == {"count": 4, "uniques": 2}
    assert archive["collection"]["last_attempt_status"] == "success"


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        {},
        {"clones": [{"timestamp": "bad", "count": 1, "uniques": 1}]},
        response("clones", ("2026-01-01", 1, 2)),
        response("clones", ("2026-01-01", 1, 1), ("2026-01-01", 1, 1)),
        {"clones": [], "count": 1, "uniques": 2},
    ],
)
def test_invalid_response_records_failure_without_partial_update(tmp_path, invalid):
    path = tmp_path / "traffic.json"
    old = {
        "version": 2,
        "repository": "owner/repo",
        "daily": {"old": {"views": {"count": 1, "uniques": 1}}},
        "rolling_14_days": {"old": {}},
        "collection": {"last_success_at": "previous"},
    }
    path.write_text(json.dumps(old))
    with patch.object(
        traffic,
        "fetch",
        side_effect=lambda repo, token, metric: (
            response("views", ("2026-01-01", 4, 2)) if metric == "views" else invalid
        ),
    ):
        with pytest.raises(ValueError):
            traffic.collect(path, "owner/repo", "token")
    archive = json.loads(path.read_text())
    assert archive["daily"] == old["daily"]
    assert archive["rolling_14_days"] == old["rolling_14_days"]
    assert archive["collection"]["last_success_at"] == "previous"
    assert archive["collection"]["last_attempt_status"] == "failed"


def test_api_failure_records_failure(tmp_path):
    path = tmp_path / "traffic.json"
    with patch.object(traffic, "fetch", side_effect=ValueError("API error")), pytest.raises(ValueError):
        traffic.collect(path, "owner/repo", "token")
    assert json.loads(path.read_text())["collection"]["last_attempt_status"] == "failed"


def test_invalid_archive_is_not_overwritten(tmp_path):
    path = tmp_path / "traffic.json"
    path.write_text('{"version": 10, "repository": "owner/repo"}')
    before = path.read_bytes()
    with pytest.raises(ValueError):
        traffic.collect(path, "owner/repo", "token")
    assert path.read_bytes() == before
