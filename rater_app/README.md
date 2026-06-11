# External acceptability-rating app

`acceptability_kappa200.html` is a **self-contained** rating app — no install, no
server, no Python for the rater. One file.

## Running it
- **Double-click** the `.html` — it opens in any browser and works offline
  (`file://`).
- **Or host it** (GitHub Pages, or any static host) and send the link — identical
  behaviour. To host on GitHub Pages: drop the file in a public repo, enable
  Pages, send the URL.

## What a rater does
1. Open it, type name/initials (keeps each person's answers separate).
2. Read the instruction — the **same wording** the model judges and Brett's gold
   used (A4 construct invariant).
3. Rate each sentence **1–7** (click, or press a number key). Optional flags:
   `v` = "doesn't match my dialect", `u` = "unsure" — flags never replace a
   rating. **No back button**; one number for every sentence.
4. At the end (or anytime via *save & download progress*) click **Download my
   responses** and email the JSON to Brett.

Answers auto-save in the browser, so a rater can close and resume. Each file is
named `acceptability_kappa200_<initials>_<date>.json` — distinct per rater.

## The set
200 sentences drawn from the gold (so they overlap Brett's 600 → κ against the
human gold), + 20 repeats (intra-rater test–retest) + 10 warm-up (discarded). All
blind: sentence only, no category/diagnostic shown. Presentation order is shuffled
per rater (seeded by their initials, so resume is consistent). Cell-id key lives
in `kappa200_cellids.json` (executor-only; never shown to raters).

## Collecting + analysing
1. Put returned JSON files in `rater_app/responses/`.
2. `python src/ingest_raters.py` — merges them, joins via `cell_id` to the gold
   and the judges, and reports per-rater agreement (vs Brett, vs each judge), the
   external calibration curve, inter-rater reliability, and each rater's
   test–retest. This is the external check on whether the compression is
   judges-vs-**humans** or judges-vs-**Brett**.

## Regenerating / other sets
`python src/build_rater_app.py` rebuilds it (seed 26). Change `N_KAPPA` /
`SETNAME` at the top to make a different set (e.g. a full-600 version).
