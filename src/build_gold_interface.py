"""Build the blind gold-coding interface (F6 / A4). Seed 26.

The gold coder (pm) sees ONLY randomized sentence strings -- no lexeme, item,
stratum, diagnostic, or judge output. A separate key (executor-only during
coding) maps presentation order back to cell_id for the post-commit rejoin.
Firewall (logged rule): the coder commits all 600 codes before any judge output
is visible; the commit hash is the evidence.

Run from repo root:  python src/build_gold_interface.py
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
SEED = 26
GOLD = os.path.join(RESULTS, "phase3_gold_sample.csv")


def main():
    gold = list(csv.DictReader(open(GOLD)))
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(gold)).tolist()

    # Blind interface: sentence strings only + a blank rating column.
    blind = os.path.join(RESULTS, "gold_coding_blind.csv")
    with open(blind, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["present_order", "sentence", "rating_1to7"])
        for pos, idx in enumerate(order, 1):
            w.writerow([pos, gold[idx]["sentence"], ""])

    # Key (executor-only during coding; cell mapping, NOT judge output).
    key = os.path.join(RESULTS, "gold_coding_key.csv")
    with open(key, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["present_order", "cell_id",
                                          "lexeme", "diagnostic", "stratum"])
        w.writeheader()
        for pos, idx in enumerate(order, 1):
            g = gold[idx]
            w.writerow({"present_order": pos, "cell_id": g["cell_id"],
                        "lexeme": g["lexeme"], "diagnostic": g["diagnostic"],
                        "stratum": g["stratum"]})

    print("Blind gold interface: %d sentences -> %s"
          % (len(gold), os.path.relpath(blind, ROOT)))
    print("Rejoin key -> %s (do not open while coding)"
          % os.path.relpath(key, ROOT))
    # sanity: blind file carries no identifying column
    hdr = open(blind).readline().strip()
    assert "lexeme" not in hdr and "diagnostic" not in hdr and \
        "stratum" not in hdr, "blind file leaks an identifying column!"
    print("Blind-file header check OK:", hdr)


if __name__ == "__main__":
    main()
