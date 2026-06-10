"""End-to-end pipeline: matrix in, structured results out.

Phase 0: runs on synthetic data (--demo reflective|network).
Phase 1: point --input at a dichotomized MegaAcceptability matrix
(rows = verbs, cols = frames, CSV with header row of item ids and an
index column of lexemes). The executor wires the fetch/dichotomization
step in Phase 1; this file should not need to change.

Outputs (results/<tag>/):
  comparison.json   CV log-loss A vs B, diffs, SEs, structure diagnostics
  items.csv         per-item projectibility (+ loading/edge summaries)
  rows.csv          per-lexeme misfit, ranked
  manifest.json     data hash, seed, params, code state
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import models   # noqa: E402
import synth    # noqa: E402


def _versions() -> dict:
    """Library versions for the manifest. This bug class (sklearn changing
    liblinear's l1_ratio handling across versions) is why every run records
    its environment -- see GOLDEN.md."""
    import sklearn
    v = {"python": platform.python_version(),
         "numpy": np.__version__,
         "scikit_learn": sklearn.__version__}
    try:
        import pandas as _pd
        v["pandas"] = _pd.__version__
    except Exception:
        v["pandas"] = None
    return v


def run(X: np.ndarray, lexemes, items, tag: str, outdir: str,
        rank: int = 1, C: float = 0.3, seed: int = 0,
        true_graph=None) -> dict:
    os.makedirs(os.path.join(outdir, tag), exist_ok=True)
    cv = models.cellwise_cv(X, rank=rank, C=C, seed=seed)
    net = models.fit_network(X)          # per-node BIC over C_GRID
    diag = models.structure_diagnostics(X, net, true_graph=true_graph)
    proj = models.projectibility(X, C=C, seed=seed)
    misfit = models.row_misfit(X, net)

    comparison = {"cv": cv, "structure": diag,
                  "n": int(X.shape[0]), "p": int(X.shape[1]),
                  "rank": rank, "C": C}
    with open(os.path.join(outdir, tag, "comparison.json"), "w") as f:
        json.dump(comparison, f, indent=2)

    order = np.argsort(-proj)
    with open(os.path.join(outdir, tag, "items.csv"), "w") as f:
        f.write("item,projectibility\n")
        for j in order:
            f.write(f"{items[j]},{proj[j]:.6f}\n")

    order = np.argsort(-misfit)
    with open(os.path.join(outdir, tag, "rows.csv"), "w") as f:
        f.write("lexeme,misfit\n")
        for i in order:
            f.write(f"{lexemes[i]},{misfit[i]:.6f}\n")

    manifest = {
        "tag": tag,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_sha256": hashlib.sha256(X.tobytes()).hexdigest(),
        "seed": seed, "rank": rank, "C": C,
        "shape": list(X.shape),
        "versions": _versions(),
    }
    with open(os.path.join(outdir, tag, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return comparison


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", choices=["reflective", "network"])
    ap.add_argument("--input", help="CSV: index col = lexeme, cols = items")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--rank", type=int, default=1)
    ap.add_argument("--C", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--outdir", default=os.path.join(
        os.path.dirname(__file__), "..", "results"))
    args = ap.parse_args()

    if args.demo:
        gen = synth.reflective if args.demo == "reflective" else synth.network
        d = gen(seed=args.seed)
        X = d["X"]
        lexemes = [f"lex{i:04d}" for i in range(X.shape[0])]
        items = [f"item{j:02d}" for j in range(X.shape[1])]
        tag = args.tag or f"demo_{args.demo}_seed{args.seed}"
        comp = run(X, lexemes, items, tag, args.outdir, rank=args.rank,
                   C=args.C, seed=args.seed, true_graph=d["true_graph"])
    elif args.input:
        rows = [ln.rstrip("\n").split(",") for ln in open(args.input)]
        items = rows[0][1:]
        lexemes = [r[0] for r in rows[1:]]
        X = np.array([[int(v) for v in r[1:]] for r in rows[1:]])
        assert set(np.unique(X)) <= {0, 1}, "input must be dichotomized 0/1"
        tag = args.tag or "run"
        comp = run(X, lexemes, items, tag, args.outdir, rank=args.rank,
                   C=args.C, seed=args.seed)
    else:
        ap.error("need --demo or --input")
    print(json.dumps(comp, indent=2))


if __name__ == "__main__":
    main()
