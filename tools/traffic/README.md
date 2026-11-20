# GitHub traffic archive

The workflow runs at 00:00 UTC (09:00 KST) daily, with a second run at
00:17 UTC as a fallback, and can also be started with `workflow_dispatch`.
GitHub may delay or drop scheduled runs, including the fallback. It stores `traffic.json`
on the separate `traffic-stats` branch, creating an orphan branch on first run.
That branch is visible to anyone who can read the repository.

Create a repository Actions secret named `TRAFFIC_TOKEN` containing a
fine-grained personal access token limited to this repository with
**Administration: read** permission. The token owner must be able to access
the repository traffic. The workflow uses this token only for traffic API
requests; the built-in `GITHUB_TOKEN` with contents write access pushes the
archive. Branch protection or Actions settings must allow that push. Renew
the secret before the token expires.

The version 2 archive stores `daily` entries keyed by UTC date, each containing
the available `views` and `clones` values (`count` and `uniques`). Existing dates in
the API response are replaced, not added, so corrections and partial current
days are updated without duplicate counting. Older dates are retained. Daily
unique counts are specific to that day and must not be summed to claim unique
users over multiple days. Missing dates or metrics are not assumed to be zero.
Version 1 archives are migrated on collection, retaining all existing buckets.

`rolling_14_days` stores GitHub's API-provided 14-day aggregate counts and
uniques keyed by the UTC date of collection, with the latest snapshot for
each day and its exact `collected_at` timestamp. This is a rolling API window,
not a sum of daily uniques or a lifetime unique count. `collection` records
the latest attempt, its success/failure, and the latest successful attempt.
The timestamp changes on every attempt, so each successful attempt normally
produces a commit even when the traffic counts have not changed.

GitHub only provides the most recent 14 days, so a longer interruption can
leave permanent gaps. Existing history cannot be recovered from this API.
API errors leave the traffic values untouched, record a failed attempt, and
fail the workflow. Failures before the archive is available or while pushing
cannot be recorded in the JSON; check Actions for those failures or missed runs.
