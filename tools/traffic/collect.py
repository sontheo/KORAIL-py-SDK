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


def collect(path, repository, token):
    if not token:
        raise ValueError("TRAFFIC_TOKEN is not set")
    if len(repository.split("/")) != 2 or not all(repository.split("/")):
        raise ValueError("GITHUB_REPOSITORY must be OWNER/REPO")
    if path.exists():
        archive = json.loads(path.read_text(encoding="utf-8"))
        if (
            not isinstance(archive, dict)
            or archive.get("version") != 1
            or archive.get("repository") != repository
            or not isinstance(archive.get("views"), dict)
            or not isinstance(archive.get("clones"), dict)
        ):
            raise ValueError("Invalid or mismatched traffic archive")
    else:
        archive = {"version": 1, "repository": repository, "views": {}, "clones": {}}

    # Fetch and validate both responses before changing the archive.
    updates = {metric: buckets(fetch(repository, token, metric), metric) for metric in ("views", "clones")}
    for metric, daily in updates.items():
        archive[metric].update(daily)
        archive[metric] = dict(sorted(archive[metric].items()))
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


if __name__ == "__main__":
    try:
        collect(Path(sys.argv[1]), os.environ["GITHUB_REPOSITORY"], os.environ.get("TRAFFIC_TOKEN", ""))
    except (IndexError, KeyError, ValueError, OSError) as exc:
        print(f"Traffic collection failed: {exc}", file=sys.stderr)
        sys.exit(1)
