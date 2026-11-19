# GitHub traffic archive

The workflow runs at 00:00 UTC (09:00 KST) daily and can also be started with
`workflow_dispatch`. GitHub may delay scheduled runs. It stores `traffic.json`
on the separate `traffic-stats` branch, creating an orphan branch on first run.
That branch is visible to anyone who can read the repository.

Create a repository Actions secret named `TRAFFIC_TOKEN` containing a
fine-grained personal access token limited to this repository with
**Administration: read** permission. The token owner must be able to access
the repository traffic. The workflow uses this token only for traffic API
requests; the built-in `GITHUB_TOKEN` with contents write access pushes the
archive. Branch protection or Actions settings must allow that push. Renew
the secret before the token expires.

The archive contains `views` and `clones` objects keyed by UTC date. Each
value has `count` and `uniques`, as returned for that day. Existing dates in
the API response are replaced, not added, so corrections and partial current
days are updated without duplicate counting. Older dates are retained. Daily
unique counts are specific to that day and must not be summed to claim unique
users over multiple days. Missing dates are not assumed to be zero.

GitHub only provides the most recent 14 days, so a longer interruption can
leave permanent gaps. Existing history cannot be recovered from this API.
Errors cause the workflow to fail without committing a partial update.
