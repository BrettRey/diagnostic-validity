# STATUS — diagnostic-validity

*Do categorial diagnostics measure anything? A psychometric study of English lexical categories.*
Target: *Language*

## Current phase

**Phase 0 complete. Phase 1 IN PROGRESS (blocker resolved 2026-06-10).**

Phase 0 (pm-node, Brett + Claude chat): plan, diagnostic battery, tested pipeline, outcome-neutral §1–2, verified references. DONE.

Phase 1 (executor): fetch MegaAcceptability v2, run src/pipeline.py, emit results/pilot_findings.md + CSVs, post pm-update.

## Blockers

None. (Golden test blocker resolved 2026-06-10 — see Resolved below.)

## Resolved

**Golden test failure (`test_network_signature`) — FIXED 2026-06-10.**

Root cause: `src/models.py:65` passed `l1_ratio=1.0` to a `solver="liblinear"`
model without setting `penalty`. `l1_ratio` applies only to `penalty="elasticnet"`,
so it was ignored and the penalty defaulted to `l2`, producing a fully connected
network (`edge_density=1.0`, `edge_f1=0.199`).

Fix (authorized by Brett via chat, 2026-06-10): line 65 `l1_ratio=1.0` →
`penalty="l1"`. `pytest -q` now passes 4/4. Both GOLDEN.md commands reproduce
to the documented 4-decimal tolerance.

**GOLDEN.md was NOT changed.** The earlier instruction here ("update GOLDEN.md
numbers") was mistaken: the anchors were generated from correct l1 code, so the
fix restores them rather than changing them. Verified in-memory before applying.
sklearn 1.6.1 on this machine.

## Last updated

2026-06-10 — Golden blocker fixed; Phase 1 started (fetch MegaAcceptability v2).
