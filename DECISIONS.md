# DECISIONS — diagnostic-validity

2026-06-10 — Bib layout: references.bib set as symlink to central house-style bib; cgel2002, goodman1955, whiterawlins2016, whiterawlins2020 moved to references-local.bib. cgel2002 and goodman1955 duplicate central entries under project-internal keys to avoid changing main.tex keys.

2026-06-10 — Golden test blocker found during setup: src/models.py:65 uses l1_ratio=1.0 with liblinear solver (wrong parameter; should be penalty="l1"). Not fixed by executor per CLAUDE.md rule 3. Awaiting pm-update from Brett.

2026-06-10 — Golden blocker fixed (authorized by Brett via chat). models.py:65 l1_ratio=1.0 → penalty="l1". Verified in-memory before applying; pytest 4/4 after; both GOLDEN.md commands reproduce to 4 dp. GOLDEN.md left unchanged — anchors were already the correct l1 numbers, so the fix restores them (the prior "update GOLDEN.md" note was mistaken). sklearn 1.6.1.

2026-06-10 — Bib symlink REVERTED (pm directive, Brett via chat), superseding the symlink decision logged above. references.bib is now a project-local, verified-only regular file (not a symlink to central); references-local.bib removed and its \addbibresource line dropped from main.tex (single file). Reason: the verified-only invariant is a fabrication firewall — biber must fail loudly on any key not promoted from TO_VERIFY, which the central-bib symlink defeated; also keeps the repo self-contained. Duplicating central entries (croft2001, aarts2007, maling1983, matthews2014, cgel2002, goodman1955) is the accepted cost. whiterawlins2016/2020 stay OUT until pm promotion (Phase 2); the build fails on them by design. Overrides the portfolio-wide symlink+references-local workflow for this project.

2026-06-10 — Manifests record library versions (pm directive). pipeline.py writes python/numpy/scikit_learn/pandas into every manifest.json; GOLDEN.md notes anchors generated under sklearn 1.8.0 reproduce under 1.6.1 with penalty="l1". Documents the liblinear/l1_ratio cross-version bug class.

2026-06-10 — White & Rawlins 2016/2020 read (pm directive): lingbuzz 004596 PDF + publisher metadata. Bib details and the ordinal-model normalization summary logged to TO_VERIFY.md items 1, 2, D for pm promotion in Phase 2.

2026-06-10 — PHASE 1 PRE-REGISTRATION (pre-registered via pm-update, 2026-06-10; Brett). Verbatim:
1. Slice: past tense only (v1-equivalent) as primary; all-tense pooled mean as a sensitivity arm. Native-speaker filter as you proposed — endorsed, and report the (trivial) effect.
2. Normalization: participant-level z-scores (each rater standardized over their own responses), cell value = mean z across that cell's raters. Rationale: median five raters per cell makes rater scale-use the dominant nuisance, and per-rater standardization is the cheap, standard correction — we're not reproducing W&R's ordinal-model normalization, just citing it once read.
3. Primary threshold: z̄ > 0. The raw distribution being U-shaped means any mid-scale cut lands in the density trough, so the choice is less consequential than it looks — but z̄ > 0 specifically reads as "above this rater pool's own average," and its 0.356 base rate keeps frame columns furthest from degeneracy, which the BIC node fits need.
4. Sensitivity grid: z̄ > 0.25; raw mean ≥ 4; raw mean ≥ 4.5. Pre-registered robustness criterion: the verdict — sign of cv.diff_mean and the eigen-dominance band — must be invariant across the grid. If it isn't, threshold-dependence is itself the reported result; no arm gets promoted post hoc.
5. Continuous check: eigen spectrum of the undichotomized z̄ matrix reported alongside, satisfying PLAN §3's ordinal clause without new modeling code.
6. Missing cells: exclude verbs with any missing cell in the analyzed slice; report how many verbs that costs (bounded above by 264). Flag any frame with post-dichotomization base rate outside [0.02, 0.98]; they stay in, flagged.

Calibration note (pm, not a decision): with 1,007 verbs from a single putative category, the expected boring outcome is a strong first dimension (general embeddability); eigen-dominance alone will not adjudicate the theories on this dataset (it will on the Phase 3 cross-category grid). Informative quantities here: the CV comparison, residual structure after the first dimension, and which frames carry projectibility. High dominance is not a verdict for the reflective view.
