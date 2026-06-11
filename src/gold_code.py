"""Gold-coding interface (F6 / A4). One sentence at a time, no back button.

Run interactively in YOUR terminal:

    python src/gold_code.py

Protocol (pm, pre-registered 2026-06-11):
- ~20-item WARM-UP from non-gold grid cells (ratings discarded; anchors scale).
- 600 gold cells + ~30 randomly repeated gold cells (test-retest reliability;
  repeats stripped before PPI), gold+repeats shuffled together; warm-up first.
- One pass, no revisiting. Rate the percept: first response, 5-10 s, "could a
  native speaker say this?" No lookups (no corpus/dictionary/CGEL).
- Flags are keystrokes, never adjustments to the integer: append 'v' (your
  Canadian vs BrE intuition genuinely diverges) and/or 'u' (unsure).
- Sessions: quit with 'q' anytime; re-run to resume. Each run is a session;
  session id + per-item UTC timestamps are logged (session-effect check later).

FIREWALL: do not open any judge output (results/phase3_ratings_*.csv) or
agreement statistic until your 600 are committed. The instruction you read is
the SAME frozen prompt the judges saw (A4 construct invariant). Do not open
results/gold_coding_order.json (the cell mapping) while coding.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import run_judges  # for the frozen PROMPT (single source of truth)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
SEED = 26
N_WARMUP = 20
N_REPEAT = 30
GOLD = os.path.join(RESULTS, "phase3_gold_sample.csv")
GRID = os.path.join(RESULTS, "phase3_grid_judgment.csv")
ORDER = os.path.join(RESULTS, "gold_coding_order.json")
RESP = os.path.join(RESULTS, "gold_coding_responses.csv")


def build_order():
    gold = list(csv.DictReader(open(GOLD)))
    gold_ids = [int(g["cell_id"]) for g in gold]
    grid = [r["sentence"] for r in csv.DictReader(open(GRID))]
    rng = np.random.default_rng(SEED)
    nongold = [i for i in range(len(grid)) if i not in set(gold_ids)]
    warm = rng.choice(nongold, N_WARMUP, replace=False).tolist()
    rep = rng.choice(gold_ids, N_REPEAT, replace=False).tolist()
    items = [{"type": "warmup", "cell_id": int(c), "sentence": grid[c]}
             for c in warm]
    scored = [{"type": "gold", "cell_id": int(g["cell_id"]),
               "sentence": g["sentence"]} for g in gold]
    scored += [{"type": "repeat", "cell_id": int(c), "sentence": grid[c]}
               for c in rep]
    scored = [scored[i] for i in rng.permutation(len(scored)).tolist()]
    order = items + scored
    for pos, it in enumerate(order, 1):
        it["present_pos"] = pos
    json.dump(order, open(ORDER, "w"), indent=1)
    return order


def main():
    order = build_order() if not os.path.exists(ORDER) else json.load(open(ORDER))
    n_scored = sum(1 for it in order if it["type"] != "warmup")

    answered, sessions = set(), []
    if os.path.exists(RESP):
        for r in csv.DictReader(open(RESP)):
            answered.add(int(r["present_pos"]))
            sessions.append(int(r["session"]))
    session = (max(sessions) + 1) if sessions else 1

    new = not os.path.exists(RESP)
    fh = open(RESP, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=["present_pos", "type", "rating",
                                       "variety", "unsure", "timestamp",
                                       "session"])
    if new:
        w.writeheader()
        fh.flush()

    os.system("clear")
    print("=" * 72)
    print("GOLD CODING -- instruction (verbatim, the same prompt the judges saw):\n")
    print(run_judges.PROMPT.replace("\n\nSentence: {sentence}",
                                    "\n\n[then one sentence is shown; reply 1-7]"))
    print("=" * 72)
    print(f"\nSession {session}.  {len(answered)}/{len(order)} items done "
          f"({N_WARMUP} warm-up, then {n_scored} scored).")
    print("Rate 1-7. Append 'v' (variety divergence) or 'u' (unsure). 'q' pauses.")
    print("First response, 5-10 s, 'could a native speaker say this?' No lookups.\n")
    try:
        input("Press Enter to begin...")
    except EOFError:
        pass

    for it in order:
        if it["present_pos"] in answered:
            continue
        os.system("clear")
        if it["type"] == "warmup":
            print(f"WARM-UP {it['present_pos']}/{N_WARMUP}  (not scored)\n")
        else:
            print(f"item {it['present_pos'] - N_WARMUP}/{n_scored}\n")
        print("    " + it["sentence"] + "\n")
        while True:
            try:
                raw = input("    rating 1-7 (+v/+u, q=pause): ").strip().lower()
            except EOFError:
                fh.close()
                return
            if raw == "q":
                fh.close()
                print("\nPaused. Re-run `python src/gold_code.py` to resume.")
                return
            digits = [c for c in raw if c in "1234567"]
            if len(digits) != 1:
                print("    -> enter exactly one digit 1-7 (optionally +v/+u)")
                continue
            rating = int(digits[0])
            break
        w.writerow({"present_pos": it["present_pos"], "type": it["type"],
                    "rating": rating, "variety": int("v" in raw),
                    "unsure": int("u" in raw),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session": session})
        fh.flush()
    fh.close()
    os.system("clear")
    print("ALL %d items coded. Now COMMIT the responses (the firewall evidence):"
          % len(order))
    print("    git add results/gold_coding_responses.csv && git commit -m "
          "'gold codes committed'")
    print("Then tell the executor. Do not open judge output before that commit.")


if __name__ == "__main__":
    main()
