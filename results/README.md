# results/ artifacts

These files are local measurement artifacts, not part of the published SDK.

Sensitive by default:

- `flows/*.json`: cookies, `JSESSIONID`, `_dts`, `fn4_` tokens, request bodies.
- `results/t1_*.json`, `results/t1s_*.json`: `x-dynapath-m-token` values and request forms.
- `results/token_split.json`: deterministic token example.

Do not commit, paste into issues, or share without stripping tokens, cookies, request IDs, and `di` values.

Current files:

- `403_map.tsv` — T1 mobile 8×3 table.
- `T1_403_MAP.md` — T1 verdicts H1–H4.
- `T2_WEB.md` — T2 web S4 5-run report.
- `T3_COOLDOWN.md` — T3 7-point cooldown + 2×2×2 factorial.
- `T4_S0_S4.md`, `T4_STAGES.tsv` — T4 fidelity stages.
- `T5_MOBILE.md` — T5 30-run reproduction.
- `T6_LAYER.md` — T6 layer separation.
- `T7_TOKEN.md` — T7 token segments/determinism.
- `layer_login.db`, `layer_search.db` — T6 SQLite.
- `cooldown.db`, `factorial.db` — T3 SQLite.
- `token_split.json`, `token_determinism.txt` — T7.
- `t5_runs.jsonl` — T5 30-run raw.
- `tools/analysis/mobile_client.py` — T5 client (v2 default, Sid, dynamic rt for v1).
- `T10_SOLUTION.md` — short v2 data envelope fix.
- `T11_SERVICE.md` — deployed korail-bot verification.
- `T12_WEB_NODEVTOOLS.md` — web block without DevTools.
