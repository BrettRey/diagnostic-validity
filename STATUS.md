# STATUS — diagnostic-validity

*Do categorial diagnostics measure anything? A psychometric study of English lexical categories.*
Target: *Language*

## Current phase

**Phase 0 complete. Phase 1 BLOCKED (see below).**

Phase 0 (pm-node, Brett + Claude chat): plan, diagnostic battery, tested pipeline, outcome-neutral §1–2, verified references. DONE.

Phase 1 (executor): fetch MegaAcceptability v2, run src/pipeline.py, emit results/pilot_findings.md + CSVs, post pm-update.

## Blockers

**Golden test failure on this machine (`test_network_signature`).**

`python -m pytest tests/ -q` fails: `edge_f1: 0.199` (expected > 0.55); `edge_density: 1.0` (expected ~0.16).

Root cause: `src/models.py:65` uses `l1_ratio=1.0` with `solver="liblinear"`.
The `l1_ratio` parameter is only valid for `elasticnet`; `liblinear` ignores it and
uses `l2` penalty, producing a fully connected (non-sparse) network. The golden
numbers in GOLDEN.md were computed in an environment where this was treated
differently (possibly older sklearn where `liblinear` defaulted to `l1`).

Fix: change line 65 from `l1_ratio=1.0` to `penalty="l1"`.
After fixing, re-run both golden commands and update GOLDEN.md numbers.

**Per CLAUDE.md rule 3: executor must not touch `src/` until Brett clears this via pm-update.**

## Last updated

2026-06-10 — Project scaffold set up from Phase 0 bundle; golden test failure found.
