# STATUS — diagnostic-validity

*Do categorial diagnostics measure anything? A psychometric study of English lexical categories.*
Target: *Language*

## Current phase

**Phase 1 COMPLETE (2026-06-10). Awaiting Phase 2 (pm-node: go/no-go vs PLAN §4; citing-papers sweep).**

Phase 0 (pm-node): plan, battery, tested pipeline, outcome-neutral §1–2, verified references. DONE.

Phase 1 (executor): DONE. MegaAcceptability v2 fetched + analysed per the 2026-06-10 pre-registration (DECISIONS.md). Driver: `src/run_phase1.py`. Deliverables: `results/pilot_findings.md`, `pilot_comparison.csv`, `pilot_projectibility.csv`, `pilot_misfit.csv`, `pilot_manifest.json`.

Phase 1 headline (factual; interpretation is Phase 2):
- Network (Model B) beats low-rank (Model A) on held-out cells in all 5 arms, all significant at 2 SE; verdict sign-invariant.
- A-vs-B gap narrows as Model A rank rises (diff_mean 0.149 @rank1 → 0.059 @rank5); best CV rank = 5 (the pre-set ceiling).
- Eigen-dominance uniformly ~1.5 (never >3); continuous z̄ spectrum has two large eigenvalues (12.9, 9.6). Band-invariance False (values straddle the 1.5 cutoff).
- 48/49 frames project >0.01; no degenerate frames. Primary slice = 1000 verbs × 49 frames (frame 'S, I V' is non-past-only).

Open for pm (Phase 2):
- Go/no-go vs PLAN §4 (T1/T2/T3).
- Promote whiterawlins2016/2020 from TO_VERIFY into references.bib (build fails on those keys by design until then).
- Optional: bootstrap projectibility SEs for formal T2 significance (deferred).

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

2026-06-10 — Phase 1 complete: bib firewall restored, manifests versioned, W&R 2020 read, pre-registration logged, MegaAcceptability v2 analysed. Awaiting Phase 2 (pm).
