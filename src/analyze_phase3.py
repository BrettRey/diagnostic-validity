"""Phase 3 analysis -- stage 1: assemble dataset + reliability/agreement.

Firewall lifted (gold committed). Joins gold codes to cell_ids via the pinned
order, strips the warm-up, separates the test-retest repeats, dedups each judge
(keep status==ok per cell_id), and reports the standalone reliability numbers:
intra-rater test-retest, judge-vs-gold accuracy, inter-judge agreement. (PPI
correction + the measurement-model comparison are stage 2.)

  python src/analyze_phase3.py
"""
from __future__ import annotations

import csv
import json
import os

import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")


def load_judge(judge):
    """{cell_id: rating} keeping status==ok (Fable log has re-run dups)."""
    best = {}
    with open(os.path.join(RESULTS, f"phase3_ratings_{judge}.csv")) as f:
        for r in csv.DictReader(f):
            if r["status"] == "ok" and r["rating"]:
                best[int(r["cell_id"])] = int(r["rating"])
    return best


def load_gold():
    order = {int(it["present_pos"]): it
             for it in json.load(open(os.path.join(RESULTS,
                                 "gold_coding_order.json")))}
    gold, repeat, flags = {}, {}, {"variety": 0, "unsure": 0, "warmup": 0}
    with open(os.path.join(RESULTS, "gold_coding_responses.csv")) as f:
        for r in csv.DictReader(f):
            it = order[int(r["present_pos"])]
            cid, typ, rating = it["cell_id"], it["type"], int(r["rating"])
            flags["variety"] += int(r["variety"])
            flags["unsure"] += int(r["unsure"])
            if typ == "gold":
                gold[cid] = rating
            elif typ == "repeat":
                repeat[cid] = rating
            else:
                flags["warmup"] += 1
    return gold, repeat, flags


def agree(x, y, label):
    x, y = np.array(x), np.array(y)
    n = len(x)
    out = {
        "label": label, "n": n,
        "pearson_r": round(float(stats.pearsonr(x, y)[0]), 3),
        "spearman_r": round(float(stats.spearmanr(x, y)[0]), 3),
        "quadratic_kappa": round(float(cohen_kappa_score(
            x, y, weights="quadratic", labels=list(range(1, 8)))), 3),
        "exact_pct": round(100 * float(np.mean(x == y)), 1),
        "within1_pct": round(100 * float(np.mean(np.abs(x - y) <= 1)), 1),
        "mean_abs_err": round(float(np.mean(np.abs(x - y))), 2),
    }
    return out


def main():
    gold, repeat, flags = load_gold()
    fable, gpt = load_judge("fable"), load_judge("gpt")
    print("gold cells: %d | repeats: %d | flags: %s"
          % (len(gold), len(repeat), flags))
    print("judge ok cells: fable %d, gpt %d (of 12840)"
          % (len(fable), len(gpt)))

    results = {"counts": {"gold": len(gold), "repeats": len(repeat),
                          "fable_ok": len(fable), "gpt_ok": len(gpt),
                          "flags": flags}, "agreement": {}}

    # intra-rater test-retest (the 30 repeats: gold rating vs repeat rating)
    rt = [(gold[c], repeat[c]) for c in repeat if c in gold]
    results["agreement"]["test_retest"] = agree(
        [a for a, _ in rt], [b for _, b in rt], "intra-rater test-retest")

    # judge vs gold (on the 600 gold cells the judge rated)
    for j, jd in (("fable", fable), ("gpt", gpt)):
        cells = [c for c in gold if c in jd]
        results["agreement"][f"{j}_vs_gold"] = agree(
            [gold[c] for c in cells], [jd[c] for c in cells], f"{j} vs gold")

    # inter-judge (all cells both rated)
    shared = [c for c in fable if c in gpt]
    results["agreement"]["fable_vs_gpt"] = agree(
        [fable[c] for c in shared], [gpt[c] for c in shared], "fable vs gpt")

    with open(os.path.join(RESULTS, "phase3_reliability.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\n%-26s %5s %7s %7s %6s %6s %7s" %
          ("comparison", "n", "pears", "spear", "qkap", "exact", "within1"))
    for k in ("test_retest", "fable_vs_gold", "gpt_vs_gold", "fable_vs_gpt"):
        a = results["agreement"][k]
        print("%-26s %5d %7.3f %7.3f %6.3f %5.1f%% %6.1f%%" %
              (a["label"], a["n"], a["pearson_r"], a["spearman_r"],
               a["quadratic_kappa"], a["exact_pct"], a["within1_pct"]))


if __name__ == "__main__":
    main()
