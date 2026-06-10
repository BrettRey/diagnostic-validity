# DECISIONS — diagnostic-validity

2026-06-10 — Bib layout: references.bib set as symlink to central house-style bib; cgel2002, goodman1955, whiterawlins2016, whiterawlins2020 moved to references-local.bib. cgel2002 and goodman1955 duplicate central entries under project-internal keys to avoid changing main.tex keys.

2026-06-10 — Golden test blocker found during setup: src/models.py:65 uses l1_ratio=1.0 with liblinear solver (wrong parameter; should be penalty="l1"). Not fixed by executor per CLAUDE.md rule 3. Awaiting pm-update from Brett.

2026-06-10 — Golden blocker fixed (authorized by Brett via chat). models.py:65 l1_ratio=1.0 → penalty="l1". Verified in-memory before applying; pytest 4/4 after; both GOLDEN.md commands reproduce to 4 dp. GOLDEN.md left unchanged — anchors were already the correct l1 numbers, so the fix restores them (the prior "update GOLDEN.md" note was mistaken). sklearn 1.6.1.
