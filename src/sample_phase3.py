"""Phase 3 lexeme sampler (F1-F4). One script, one commit, seed 26.

Draws the Phase 3 lexeme sample per the pre-registration (DECISIONS.md
F1-F7, amended): adjectives in SUBTLEX-UK Zipf bands, a category-blind
stratum, plus the forced category seed-lists (prepositions, the 73 Reynolds
determinatives, the boundary set). Dedups toward the more specific stratum
and logs collisions. Emits the sample CSV + a manifest (frame hashes, seed,
band populations, collisions, git rev). NO instantiation here (F5-gated).

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
DIAG = os.path.join(ROOT, "diagnostics.yaml")

# F1(a) amended bands (Zipf); 55 adjectives per band.
ADJ_BANDS = [("zipf>=5", 5.0, 99.0), ("4-5", 4.0, 5.0),
             ("3-4", 3.0, 4.0), ("2-3", 2.0, 3.0)]
ADJ_PER_BAND = 55
BLIND_TOPN = 10000
BLIND_N = 60


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
        rows.append({"lexeme": surface, "stratum": stratum,
                     **(extra or {})})
        return True

    # ---- forced seed-lists first (most specific) -----------------------
    # F1d boundary set (most specific; forced inclusion)
    diag = yaml.safe_load(open(DIAG))
    boundary = [b.strip() for b in diag["boundary_set"]]
    for w in boundary:
        add(w, "boundary")

    # F1c determinatives (73, Reynolds, verbatim labels -> surface)
    det_labels = [l.strip() for l in open(DETS)
                  if l.strip() and not l.startswith("#")]
    assert len(det_labels) == 73, f"expected 73 dets, got {len(det_labels)}"
    for lab in det_labels:
        add(det_surface(lab), "determinative", {"reynolds_label": lab})

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

    # F1a adjectives by Zipf band
    adj = df[df["DomPoS"] == "adjective"]
    band_pops = {}
    band_draws = {}
    for name, lo, hi in ADJ_BANDS:
        pool = adj[(adj["z"] >= lo) & (adj["z"] < hi)]
        band_pops[name] = int(len(pool))
        n = min(ADJ_PER_BAND, len(pool))
        idx = rng.choice(len(pool), size=n, replace=False) if n else []
        band_draws[name] = [pool.iloc[i] for i in idx]
    # merge note if the bottom band underfills (F2 amendment)
    merged_note = None
    if band_pops[ADJ_BANDS[-1][0]] < ADJ_PER_BAND:
        merged_note = (f"bottom band '2-3' has only {band_pops['2-3']} "
                       f"adjectives (<{ADJ_PER_BAND}); took all. Per F2, this "
                       f"is the logged merge/underfill, not a silent cap.")
    adj_band_acct = {}
    for name, _, _ in ADJ_BANDS:
        drawn = len(band_draws[name])
        surv = 0
        for r in band_draws[name]:
            if add(r["Spelling"], "adjective",
                   {"zipf": round(float(r["z"]), 3), "zipf_band": name}):
                surv += 1
        adj_band_acct[name] = {"drawn": drawn, "survived": surv,
                               "lost_to_more_specific": drawn - surv}

    # F1e category-blind: 60 from the top BLIND_TOPN by Zipf, no PoS cond.
    top = df.sort_values("z", ascending=False).head(BLIND_TOPN)
    bidx = rng.choice(len(top), size=BLIND_N, replace=False)
    blind_added = 0
    for i in bidx:
        r = top.iloc[i]
        if add(r["Spelling"], "blind",
               {"zipf": round(float(r["z"]), 3), "dompos": r["DomPoS"]}):
            blind_added += 1

    # ---- write deliverables -------------------------------------------
    os.makedirs(RESULTS, exist_ok=True)
    cols = ["lexeme", "stratum", "reynolds_label", "prep_scope",
            "zipf", "zipf_band", "dompos"]
    with open(os.path.join(RESULTS, "phase3_sample.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})

    strata_counts = {}
    for r in rows:
        strata_counts[r["stratum"]] = strata_counts.get(r["stratum"], 0) + 1

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
        },
        "adjective_band_populations": band_pops,
        "adjective_per_band_target": ADJ_PER_BAND,
        "adjective_band_underfill_note": merged_note,
        "adjective_band_accounting": adj_band_acct,
        "grid_size_note": (
            "Judgment grid ~ %d lexemes x 24 confirmed judgment items "
            "(+ ~18 corpus columns) ~ 22k cells. F6 gold sample stays 600 "
            "cells as pre-registered -- a thinner sampling fraction (~2.7%%) "
            "against this grid than against the ~450-lexeme planning estimate; "
            "noted per pm (ruling a, keep full 522), not silently absorbed."
            % len(rows)),
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
    print("Adjective band populations (available):", band_pops)
    print("Collisions (deduped toward more specific):", len(collisions))
    for c in collisions:
        print("   ", c[0], ":", c[2], "->", c[1])
    if merged_note:
        print("NOTE:", merged_note)


if __name__ == "__main__":
    main()
