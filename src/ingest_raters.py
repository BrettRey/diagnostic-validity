"""Ingest external rater responses (rater_app/responses/*.json) and compute the
external check: is the judge-human compression judges-vs-HUMANS or judges-vs-Brett?

Joins each rater's ratings by cell_id to Brett's gold + both judges, and reports
per rater: agreement vs Brett (r, post-dichot kappa), vs each judge, the external
calibration curve (rater - gold by gold band), intra-rater test-retest (repeats),
and inter-rater agreement. No responses yet -> prints a clear nothing-to-do.

  python src/ingest_raters.py
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys

import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, os.path.dirname(__file__))
from analyze_phase3 import load_gold, load_judge  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESP = os.path.join(ROOT, "rater_app", "responses")


def kappa_z(a, b):
    """post-dichotomization kappa at within-set z>0 (a,b paired arrays)."""
    az = (a - a.mean()) / a.std() > 0
    bz = (b - b.mean()) / b.std() > 0
    return round(float(cohen_kappa_score(az.astype(int), bz.astype(int),
                                         labels=[0, 1])), 3)


def main():
    files = sorted(glob.glob(os.path.join(RESP, "*.json")))
    if not files:
        print("No rater files in rater_app/responses/. "
              "Drop returned .json files there and re-run.")
        return
    gold, _, _ = load_gold()
    fable, gpt = load_judge("fable"), load_judge("gpt")

    raters = {}
    for fp in files:
        d = json.load(open(fp))
        scored = {int(r["cell_id"]): int(r["rating"]) for r in d["responses"]
                  if r["type"] == "scored" and r.get("rating")}
        repeats = [(int(r["cell_id"]), int(r["rating"])) for r in d["responses"]
                   if r["type"] == "repeat" and r.get("rating")]
        raters[d["rater"]] = {"scored": scored, "repeats": repeats}

    out = {}
    for name, rd in raters.items():
        sc = rd["scored"]
        cells = [c for c in sc if c in gold]
        rr = np.array([sc[c] for c in cells])
        gg = np.array([gold[c] for c in cells])
        row = {"n": len(cells),
               "vs_brett_r": round(float(stats.pearsonr(rr, gg)[0]), 3),
               "vs_brett_kappa_z": kappa_z(rr, gg),
               "vs_brett_mean_resid": round(float((rr - gg).mean()), 3)}
        for j, jd in (("fable", fable), ("gpt", gpt)):
            cj = [c for c in sc if c in jd]
            r2 = np.array([sc[c] for c in cj])
            jj = np.array([jd[c] for c in cj])
            row[f"vs_{j}_r"] = round(float(stats.pearsonr(r2, jj)[0]), 3)
            row[f"vs_{j}_mean_resid_judge_minus_rater"] = round(
                float((jj - r2).mean()), 3)
        # external calibration: rater - gold by gold band
        band = {}
        for c in cells:
            band.setdefault(gold[c], []).append(sc[c] - gold[c])
        row["calib_rater_minus_gold_by_band"] = {
            str(k): round(float(np.mean(v)), 2) for k, v in sorted(band.items())}
        # intra-rater test-retest
        if rd["repeats"]:
            first = {c: sc[c] for c, _ in rd["repeats"] if c in sc}
            pairs = [(first[c], rv) for c, rv in rd["repeats"] if c in first]
            if len(pairs) > 2:
                a = np.array([p[0] for p in pairs])
                b = np.array([p[1] for p in pairs])
                row["test_retest_r"] = round(float(stats.pearsonr(a, b)[0]), 3)
        out[name] = row

    # inter-rater (shared cells, mean pairwise r)
    names = list(raters)
    inter = []
    for i in range(len(names)):
        for k in range(i + 1, len(names)):
            a, b = raters[names[i]]["scored"], raters[names[k]]["scored"]
            sh = [c for c in a if c in b]
            if len(sh) > 2:
                inter.append(round(float(stats.pearsonr(
                    np.array([a[c] for c in sh]),
                    np.array([b[c] for c in sh]))[0]), 3))
    summary = {"raters": out,
               "inter_rater_pairwise_r": inter,
               "n_raters": len(raters)}
    with open(os.path.join(ROOT, "results", "phase3_external_raters.json"),
              "w") as f:
        json.dump(summary, f, indent=2)
    for name, row in out.items():
        print(f"{name}: n={row['n']} vs_Brett r={row['vs_brett_r']} "
              f"kappa_z={row['vs_brett_kappa_z']} resid={row['vs_brett_mean_resid']:+.2f} "
              f"| vs_fable r={row['vs_fable_r']} vs_gpt r={row['vs_gpt_r']}")
        print(f"   calib (rater-gold by band): {row['calib_rater_minus_gold_by_band']}")
    print("inter-rater pairwise r:", inter or "(need >=2 raters)")
    print("KEY: if raters track Brett (resid ~0) and judges stay -0.8 below both,"
          " the compression is judges-vs-HUMANS. If raters sit with the judges,"
          " it's Brett-specific.")


if __name__ == "__main__":
    main()
