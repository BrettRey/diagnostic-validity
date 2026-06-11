"""Phase 3 lexeme sampler (F1-F4). One script, one commit, seed 26.

Draws the Phase 3 lexeme sample per the pre-registration (DECISIONS.md
F1-F7, amended): adjectives in SUBTLEX-UK Zipf bands, a category-blind
stratum, plus the forced category seed-lists (prepositions, the Reynolds
determinatives + numeral extension, the boundary set). Dedups toward the
more specific stratum and logs collisions. Decision 1 (2026-06-11): a
rule-based inflection filter excludes inflectional comparative/superlative
variants from the adjective + blind strata (an inflected form is not a
lexeme), with random backfill from the same band. Emits the sample CSV +
a manifest. NO instantiation here (F5-gated).

Run from the repo root:  python src/sample_phase3.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(__file__))
import pipeline  # noqa: E402  (for _versions)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SAMPLING = os.path.join(ROOT, "sampling")
RESULTS = os.path.join(ROOT, "results")
SEED = 26

SUBTLEX = os.path.join(DATA, "SUBTLEX-UK.txt")
MATRIX = os.path.join(DATA, "reynolds2021_determinative_matrix.csv")
PREPS = os.path.join(SAMPLING, "prepositions_cgel_ch7.csv")
DETS = os.path.join(SAMPLING, "determinatives_reynolds73.txt")
DETS_EXT = os.path.join(SAMPLING, "determinatives_extension2026.txt")
DIAG = os.path.join(ROOT, "diagnostics.yaml")

# F1(a) amended bands (Zipf); 55 adjectives per band.
ADJ_BANDS = [("zipf>=5", 5.0, 99.0), ("4-5", 4.0, 5.0),
             ("3-4", 3.0, 4.0), ("2-3", 2.0, 3.0)]
ADJ_PER_BAND = 55
BLIND_TOPN = 10000
BLIND_N = 60

# Decision 1: inflectional comparative/superlative suppletives (logged rule).
# -ed/-ing participials are deliberately NOT filtered (conversion-zone lexemes).
SUPPLETIVE_INFL = {"better", "best", "worse", "worst", "more", "most",
                   "less", "least", "further", "furthest", "farther",
                   "farthest", "elder", "eldest"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git_rev():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=ROOT).decode().strip()
    except Exception:
        return "unknown"


def det_surface(label):
    """Reynolds label -> surface lexeme: strip category-disambiguation
    suffixes (_det, _rel_det, _int_det), underscores -> spaces."""
    s = re.sub(r"_(rel|int)_det$", "", label)
    s = re.sub(r"_det$", "", s)
    return s.replace("_", " ").strip()


def norm(form):
    return form.strip().lower()


def _deinflect(x):
    """Candidate adjective bases for a putative -er/-est form."""
    cands = []
    for suf in ("er", "est"):
        if x.endswith(suf):
            stem = x[:-len(suf)]
            cands += [stem, stem + "e"]
            if len(stem) >= 2 and stem[-1] == stem[-2]:
                cands.append(stem[:-1])          # bigger -> big
            if stem.endswith("i"):
                cands.append(stem[:-1] + "y")    # happier -> happy
    return cands


def is_inflectional(x, adjforms):
    """True if x is an inflectional comparative/superlative of an attested
    adjective base (regular -er/-est, or suppletive). Leaves -ed/-ing
    participials and non-comparative -er words (clever, proper) alone."""
    if x in SUPPLETIVE_INFL:
        return True
    if x.endswith(("er", "est")):
        return any(b in adjforms for b in _deinflect(x))
    return False


def main():
    rng = np.random.default_rng(SEED)
    collisions = []           # (lexeme, kept_stratum, dropped_stratum)
    claimed = {}              # norm-key -> stratum (specificity order)
    rows = []                 # final sample rows

    def add(surface, stratum, extra=None):
        """Add a lexeme, deduping toward the FIRST (more specific) stratum."""
        k = norm(surface)
        if k in claimed:
            collisions.append((surface, claimed[k], stratum))
            return False
        claimed[k] = stratum
        rows.append({"lexeme": surface, "stratum": stratum, **(extra or {})})
        return True

    # ---- forced seed-lists first (most specific) -----------------------
    diag = yaml.safe_load(open(DIAG))
    boundary = [b.strip() for b in diag["boundary_set"]]
    for w in boundary:
        add(w, "boundary")

    # F1c determinatives (73, Reynolds, verbatim labels -> surface)
    det_labels = [l.strip() for l in open(DETS)
                  if l.strip() and not l.startswith("#")]
    assert len(det_labels) == 73, f"expected 73 dets, got {len(det_labels)}"
    for lab in det_labels:
        add(det_surface(lab), "determinative",
            {"reynolds_label": lab, "det_flag": "core2021"})
    # F1c amendment (2026-06-11, author-proposed, pm-approved): numeral extension.
    ext_labels = [l.strip() for l in open(DETS_EXT)
                  if l.strip() and not l.startswith("#")]
    for lab in ext_labels:
        add(det_surface(lab), "determinative",
            {"reynolds_label": lab, "det_flag": "extension2026"})

    # F1b prepositions (CGEL ch.7 full inventory; scope flag retained)
    with open(PREPS) as f:
        pr = csv.DictReader((ln for ln in f if not ln.startswith("#")))
        for r in pr:
            add(r["preposition"], "preposition", {"prep_scope": r["scope"]})

    # ---- SUBTLEX-derived strata (sampled; less specific) ---------------
    df = pd.read_csv(SUBTLEX, sep="\t",
                     usecols=["Spelling", "LogFreq(Zipf)", "DomPoS"],
                     dtype={"Spelling": str})
    df = df.dropna(subset=["Spelling", "LogFreq(Zipf)"])
    df["z"] = pd.to_numeric(df["LogFreq(Zipf)"], errors="coerce")
    df = df.dropna(subset=["z"])

    # F1a adjectives by Zipf band: shuffle, skip inflectional variants
    # (Decision 1) + dedup, take until ADJ_PER_BAND (random backfill from the
    # same band). This also resolves the earlier top-band imbalance.
    adj = df[df["DomPoS"] == "adjective"]
    adjforms = set(adj["Spelling"])
    band_pops, adj_band_acct = {}, {}
    for name, lo, hi in ADJ_BANDS:
        pool = adj[(adj["z"] >= lo) & (adj["z"] < hi)].reset_index(drop=True)
        band_pops[name] = int(len(pool))
        order = rng.permutation(len(pool)) if len(pool) else []
        taken = skip_infl = 0
        for j in order:
            if taken >= ADJ_PER_BAND:
                break
            r = pool.iloc[int(j)]
            if is_inflectional(r["Spelling"], adjforms):
                skip_infl += 1
                continue
            if add(r["Spelling"], "adjective",
                   {"zipf": round(float(r["z"]), 3), "zipf_band": name}):
                taken += 1
        adj_band_acct[name] = {"target": ADJ_PER_BAND, "taken": taken,
                               "skipped_inflectional": skip_infl,
                               "pool": band_pops[name]}
    short = [b for b in adj_band_acct if adj_band_acct[b]["taken"] < ADJ_PER_BAND]
    merged_note = (None if not short else
                   "under target after inflection-filter + backfill: "
                   + ", ".join(f"{b}={adj_band_acct[b]['taken']}" for b in short))

    # F1e category-blind: top BLIND_TOPN by Zipf, no PoS cond; same inflection
    # filter; shuffle-take BLIND_N with random backfill.
    top = df.sort_values("z", ascending=False).head(BLIND_TOPN).reset_index(
        drop=True)
    order = rng.permutation(len(top))
    taken = skip_infl = 0
    for j in order:
        if taken >= BLIND_N:
            break
        r = top.iloc[int(j)]
        if is_inflectional(r["Spelling"], adjforms):
            skip_infl += 1
            continue
        if add(r["Spelling"], "blind",
               {"zipf": round(float(r["z"]), 3), "dompos": r["DomPoS"]}):
            taken += 1
    blind_acct = {"target": BLIND_N, "taken": taken,
                  "skipped_inflectional": skip_infl}

    # ---- write deliverables -------------------------------------------
    os.makedirs(RESULTS, exist_ok=True)
    cols = ["lexeme", "stratum", "det_flag", "reynolds_label", "prep_scope",
            "zipf", "zipf_band", "dompos"]
    with open(os.path.join(RESULTS, "phase3_sample.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})

    strata_counts = {}
    det_flag_counts = {}
    surface_conversions = {}   # label -> surface (suffix strips + underscore->space)
    for r in rows:
        strata_counts[r["stratum"]] = strata_counts.get(r["stratum"], 0) + 1
        if r["stratum"] == "determinative":
            fl = r.get("det_flag", "")
            det_flag_counts[fl] = det_flag_counts.get(fl, 0) + 1
        lab = r.get("reynolds_label", "")
        if lab and lab != r["lexeme"]:
            surface_conversions[lab] = r["lexeme"]

    manifest = {
        "phase": 3, "step": "F4 sampling",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "git_rev": git_rev(), "versions": pipeline._versions(),
        "frames": {
            "subtlex_uk_txt": {"path": os.path.relpath(SUBTLEX, ROOT),
                               "sha256": sha256(SUBTLEX),
                               "zipf_col": "LogFreq(Zipf)", "pos_col": "DomPoS"},
            "reynolds_matrix": {"path": os.path.relpath(MATRIX, ROOT),
                                "sha256": sha256(MATRIX)},
            "prepositions": {"path": os.path.relpath(PREPS, ROOT),
                             "sha256": sha256(PREPS)},
            "determinatives": {"path": os.path.relpath(DETS, ROOT),
                               "sha256": sha256(DETS)},
            "determinatives_ext": {"path": os.path.relpath(DETS_EXT, ROOT),
                                   "sha256": sha256(DETS_EXT)},
        },
        "determinative_flag_counts": det_flag_counts,
        "determinative_surface_conversions": surface_conversions,
        "inflection_filter": {
            "rule": "exclude regular -er/-est of an attested DomPoS=adjective "
                    "base, plus the suppletive set; backfill randomly from the "
                    "same band/pool. -ed/-ing participials NOT filtered.",
            "suppletive_set": sorted(SUPPLETIVE_INFL),
            "applies_to": ["adjective", "blind"]},
        "adjective_band_populations": band_pops,
        "adjective_per_band_target": ADJ_PER_BAND,
        "adjective_band_underfill_note": merged_note,
        "adjective_band_accounting": adj_band_acct,
        "blind_accounting": blind_acct,
        "grid_size_note": (
            "Judgment grid ~ %d lexemes x 24 confirmed judgment items = %d "
            "judgment cells (+ corpus columns). F6 gold sample stays 600 cells "
            "as pre-registered = %.1f%% of judgment cells; logged per pm, not "
            "silently absorbed."
            % (len(rows), len(rows) * 24, 100 * 600 / (len(rows) * 24))),
        "strata_counts": strata_counts,
        "total_unique_lexemes": len(rows),
        "n_collisions": len(collisions),
        "collisions": [{"lexeme": l, "kept": k, "dropped": d}
                       for (l, k, d) in collisions],
    }
    with open(os.path.join(RESULTS, "phase3_sample_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print("Phase 3 sample drawn (seed %d). Total unique lexemes: %d"
          % (SEED, len(rows)))
    print("Strata:", strata_counts)
    print("Determinative flags:", det_flag_counts)
    print("Adjective bands (taken / skipped_inflectional / pool):")
    for b, a in adj_band_acct.items():
        print("   %-8s %d / %d / %d"
              % (b, a["taken"], a["skipped_inflectional"], a["pool"]))
    print("Blind: taken %d, skipped_inflectional %d"
          % (blind_acct["taken"], blind_acct["skipped_inflectional"]))
    print("Collisions (deduped toward more specific):", len(collisions))
    if merged_note:
        print("NOTE:", merged_note)


if __name__ == "__main__":
    main()
