#!/usr/bin/env python3
"""Merge GitHub's daily traffic buckets into a durable JSON archive."""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(repository, token, metric):
    url = f"https://api.github.com/repos/{repository}/traffic/{metric}?per=day"
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-actions-traffic-archive",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        raise ValueError(f"GitHub {metric} API returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"GitHub {metric} API request failed: {type(exc).__name__}") from exc


def buckets(payload, metric):
    if not isinstance(payload, dict) or not isinstance(payload.get(metric), list):
        raise ValueError(f"Invalid {metric} API response")
    result = {}
    for entry in payload[metric]:
        try:
            timestamp = entry["timestamp"]
            parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if parsed.hour or parsed.minute or parsed.second:
                raise ValueError("timestamp is not aligned to UTC midnight")
            count, unique = entry["count"], entry["uniques"]
            if type(count) is not int or type(unique) is not int or min(count, unique) < 0 or unique > count:
                raise ValueError("invalid counts")
            date = parsed.date().isoformat()
            if date in result:
                raise ValueError("duplicate date")
            result[date] = {"count": count, "uniques": unique}
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {metric} daily bucket") from exc
    return result


def load_archive(path, repository):
    if path.exists():
        archive = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(archive, dict) or archive.get("repository") != repository:
            raise ValueError("Invalid or mismatched traffic archive")
        if archive.get("version") == 1:
            if not all(isinstance(archive.get(metric), dict) for metric in ("views", "clones")):
                raise ValueError("Invalid traffic archive")
            daily = {}
            for metric in ("views", "clones"):
                for date, value in archive[metric].items():
                    daily.setdefault(date, {})[metric] = value
            archive = {"version": 2, "repository": repository, "daily": daily, "rolling_14_days": {}}
        elif (
            archive.get("version") != 2
            or not isinstance(archive.get("daily"), dict)
            or not isinstance(archive.get("rolling_14_days"), dict)
        ):
            raise ValueError("Invalid traffic archive")
    else:
        archive = {"version": 2, "repository": repository, "daily": {}, "rolling_14_days": {}}
    return archive


def save_archive(path, archive):
    content = json.dumps(archive, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def collect(path, repository, token):
    if len(repository.split("/")) != 2 or not all(repository.split("/")):
        raise ValueError("GITHUB_REPOSITORY must be OWNER/REPO")
    archive = load_archive(path, repository)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        if not token:
            raise ValueError("TRAFFIC_TOKEN is not set")
        payloads = {metric: fetch(repository, token, metric) for metric in ("views", "clones")}
        daily = {metric: buckets(payloads[metric], metric) for metric in payloads}
        totals = {}
        for metric, payload in payloads.items():
            count, uniques = payload.get("count"), payload.get("uniques")
            if type(count) is not int or type(uniques) is not int or min(count, uniques) < 0 or uniques > count:
                raise ValueError(f"Invalid {metric} 14-day totals")
            totals[metric] = {"count": count, "uniques": uniques}
    except ValueError:
        archive["collection"] = {
            **archive.get("collection", {}),
            "last_attempt_at": timestamp,
            "last_attempt_status": "failed",
        }
        save_archive(path, archive)
        raise

    for metric, values in daily.items():
        for date, value in values.items():
            archive["daily"].setdefault(date, {})[metric] = value
    archive["daily"] = dict(sorted(archive["daily"].items()))
    archive["rolling_14_days"][timestamp[:10]] = {"collected_at": timestamp, **totals}
    archive["rolling_14_days"] = dict(sorted(archive["rolling_14_days"].items()))
    archive["collection"] = {
        "last_attempt_at": timestamp,
        "last_attempt_status": "success",
        "last_success_at": timestamp,
    }
    save_archive(path, archive)


if __name__ == "__main__":
    try:
        collect(Path(sys.argv[1]), os.environ["GITHUB_REPOSITORY"], os.environ.get("TRAFFIC_TOKEN", ""))
    except (IndexError, KeyError, ValueError, OSError) as exc:
        print(f"Traffic collection failed: {exc}", file=sys.stderr)
        sys.exit(1)
