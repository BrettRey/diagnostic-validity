"""Phase 3 robustness: a STRUCTURELESS NULL for the headline verdict.

GELMAN NEGATIVE CONTROL. EXPLORATORY -- NOT pre-registered. PLAN.md §4 T3 covers
only the POSITIVE control (synthetic recovery: the method finds planted structure
when it is there). This is the missing other half: destroy the grid's
cross-diagnostic structure and re-run the headline statistics, so the real result
is read as EXCESS over a null with no structure to find.

Two nulls, per judge, on the primary arm (within-judge z>0):
  (a) column permutation -- shuffle each diagnostic's OBSERVED values across
      lexemes, independently per column. Preserves each diagnostic's acceptance
      rate exactly; destroys every cross-diagnostic dependency the models exploit.
  (b) random Bernoulli -- independent draws matched to each diagnostic's rate.

Statistics (identical code path to headline.py):
  - eig_dominance : ratio of the first two eigenvalues of the diagnostic
                    correlation matrix (PLAN's >3 reflective / <3 network).
  - cv_se_units   : network minus reflective held-out log-loss gap, in SE units.
  - edge_density  : sparse-network edge fraction.

For each, reports observed value, null mean + 95% band, and the observed value's
percentile in the null. The reflective rank is held fixed at the observed best
for the null draws (the procedure is held constant; this gives the reflective
model its best shot on structureless data, so it is conservative for "network
wins").

  python src/verdict_null.py          # full: eig N=1000, cv/edge N=200 (slow)
  python src/verdict_null.py --quick  # eig only, fast
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import warnings
warnings.filterwarnings("ignore")
np.seterr(all="ignore")

sys.path.insert(0, os.path.dirname(__file__))
import plot_style  # noqa: E402
plot_style.setup()
import models  # noqa: E402
from analyze_phase3 import load_judge  # noqa: E402
from headline import (load_grid_index, judge_matrices, impute_binary,  # noqa: E402
                      best_rank_cv, RESULTS, ROOT, SEED)

N_EIG = 1000
N_FIT = 200
JUDGES = ("fable", "gpt")


def eig_dominance(X):
    r = np.nan_to_num(np.corrcoef(X.T), nan=0.0)
    ev = np.sort(np.linalg.eigvalsh(r))[::-1]
    return float(ev[0] / max(ev[1], 1e-9))


def cv_se_units(X, rank):
    cv = models.cellwise_cv(X, rank=rank, n_folds=3, seed=SEED)
    return float(cv["diff_mean"] / cv["diff_se"]) if cv["diff_se"] > 0 else 0.0


def edge_density(X):
    return float(models.fit_network(X)["edge_density"])


def col_permute(Bobs, mask, rng):
    """Shuffle each column's observed entries among its observed rows."""
    Bp = Bobs.copy()
    p = Bobs.shape[1]
    for j in range(p):
        obs = np.where(mask[:, j] == 1)[0]
        if obs.size > 1:
            Bp[obs, j] = Bobs[rng.permutation(obs), j]
    return Bp


def col_bernoulli(rate, mask, rng):
    """Independent Bernoulli per column at the observed acceptance rate."""
    n, p = mask.shape
    B = np.zeros((n, p))
    for j in range(p):
        B[:, j] = (rng.random(n) < rate[j]).astype(float)
    return B


def _summ(obs, null):
    null = np.asarray(null, float)
    return {"obs": round(float(obs), 3),
            "null_mean": round(float(null.mean()), 3),
            "null_ci": [round(float(np.percentile(null, 2.5)), 3),
                        round(float(np.percentile(null, 97.5)), 3)],
            "obs_pctile_in_null": round(float((null < obs).mean() * 100), 1),
            "obs_minus_null_mean": round(float(obs - null.mean()), 3)}


def main(quick=False):
    lex, diag, cell, scope, strat = load_grid_index()
    n, p = len(lex), len(diag)
    out = {"n_lexemes": n, "n_diagnostics": p, "arm": "primary_z0",
           "n_eig": N_EIG, "n_fit": (0 if quick else N_FIT),
           "status": "EXPLORATORY structureless null; NOT pre-registered "
                     "(PLAN T3 = planted-structure positive control only).",
           "judges": {}}
    draws = {}
    for jn in JUDGES:
        jr = load_judge(jn)
        _, Z, mask, _, _ = judge_matrices(jr, cell, n, p)
        Bobs = (Z > 0).astype(float)
        Bz = impute_binary(Bobs, mask)
        rate = np.array([Bobs[mask[:, j] == 1, j].mean() if mask[:, j].sum() else 0.5
                         for j in range(p)])
        obs_eig = eig_dominance(Bz)
        rng = np.random.default_rng(SEED)
        perm_eig = np.array([eig_dominance(impute_binary(col_permute(Bobs, mask, rng), mask))
                             for _ in range(N_EIG)])
        bern_eig = np.array([eig_dominance(impute_binary(col_bernoulli(rate, mask, rng), mask))
                             for _ in range(N_EIG)])
        jres = {"observed": {"eig_dominance": round(obs_eig, 3)},
                "perm_null": {"eig_dominance": _summ(obs_eig, perm_eig)},
                "bern_null": {"eig_dominance": _summ(obs_eig, bern_eig)}}
        draws[jn] = {"eig_dominance": {"perm": perm_eig, "bern": bern_eig}}
        print(f"[{jn}] eig_dominance obs={obs_eig:.2f}  "
              f"shuffle-null {perm_eig.mean():.2f} "
              f"[{np.percentile(perm_eig, 2.5):.2f},{np.percentile(perm_eig, 97.5):.2f}]  "
              f"random-null {bern_eig.mean():.2f}  "
              f"obs>{(perm_eig < obs_eig).mean() * 100:.1f}% of shuffle null")

        if not quick:
            br, _, _ = best_rank_cv(Bz, mask)
            obs_cv, obs_edge = cv_se_units(Bz, br), edge_density(Bz)
            jres["observed"].update({"cv_se_units": round(obs_cv, 2),
                                     "edge_density": round(obs_edge, 3),
                                     "best_rank": br})
            rng2 = np.random.default_rng(SEED + 1)
            pc, pe, bc, be = [], [], [], []
            for _ in range(N_FIT):
                Xp = impute_binary(col_permute(Bobs, mask, rng2), mask)
                pc.append(cv_se_units(Xp, br)); pe.append(edge_density(Xp))
                Xb = impute_binary(col_bernoulli(rate, mask, rng2), mask)
                bc.append(cv_se_units(Xb, br)); be.append(edge_density(Xb))
            jres["perm_null"]["cv_se_units"] = _summ(obs_cv, pc)
            jres["perm_null"]["edge_density"] = _summ(obs_edge, pe)
            jres["bern_null"]["cv_se_units"] = _summ(obs_cv, bc)
            jres["bern_null"]["edge_density"] = _summ(obs_edge, be)
            draws[jn]["cv_se_units"] = {"perm": np.array(pc), "bern": np.array(bc)}
            draws[jn]["edge_density"] = {"perm": np.array(pe), "bern": np.array(be)}
            print(f"[{jn}] cv_se_units obs={obs_cv:.1f}  shuffle-null "
                  f"{np.mean(pc):.2f} [{np.percentile(pc, 2.5):.2f},{np.percentile(pc, 97.5):.2f}]")
            print(f"[{jn}] edge_density obs={obs_edge:.3f}  shuffle-null "
                  f"{np.mean(pe):.3f} [{np.percentile(pe, 2.5):.3f},{np.percentile(pe, 97.5):.3f}]")
        out["judges"][jn] = jres

    suffix = "_quick" if quick else ""
    with open(os.path.join(RESULTS, f"phase3_verdict_null{suffix}.json"), "w") as f:
        json.dump(out, f, indent=2)
    if not quick:
        _figure(draws, out)
    print("wrote", f"results/phase3_verdict_null{suffix}.json")


def _figure(draws, out):
    specs = [("eig_dominance", "eigenvalue dominance (ev1/ev2)", 3.0),
             ("cv_se_units", "network - reflective gap (SE units)", 2.0),
             ("edge_density", "network edge density", None)]
    judges = list(out["judges"])
    C = plot_style.COLORS
    fig, axes = plt.subplots(len(judges), len(specs), figsize=(13, 7))
    for ri, jn in enumerate(judges):
        for ci, (key, lab, thr) in enumerate(specs):
            ax = axes[ri, ci]
            d = draws[jn].get(key)
            if d is None:
                ax.set_visible(False)
                continue
            obs = out["judges"][jn]["observed"][key]
            ax.hist(d["perm"], bins=30, color=C["primary"], alpha=0.55)
            ax.hist(d["bern"], bins=30, histtype="step", color=C["dark"], lw=1.0)
            top = ax.get_ylim()[1]
            ax.axvline(obs, color=C["secondary"], lw=2.2)
            ax.annotate("observed", (obs, top * 0.82), color=C["secondary"],
                        fontsize=8, ha="right", rotation=90, va="top")
            if thr is not None:
                ax.axvline(thr, color="grey", ls="--", lw=1.0)
                ax.annotate(f"threshold {thr:g}", (thr, top * 0.55), color="grey",
                            fontsize=7, ha="right", rotation=90, va="top")
            if ri == 0:
                ax.set_title(lab, fontsize=9)
            if ci == 0:
                ax.set_ylabel(f"{jn}\ncount", fontsize=9)
    # one legend, top-left panel: filled = shuffle, step = random
    h_perm = plt.Rectangle((0, 0), 1, 1, color=C["primary"], alpha=0.55)
    h_bern = plt.Line2D([0], [0], color=C["dark"], lw=1.0)
    h_obs = plt.Line2D([0], [0], color=C["secondary"], lw=2.2)
    axes[0, 0].legend([h_perm, h_bern, h_obs],
                      ["shuffle null", "random null", "observed"], fontsize=7)
    fig.suptitle("Structureless null for the headline verdict: observed value vs "
                 "a grid with its cross-diagnostic structure destroyed", fontsize=10)
    plt.tight_layout()
    p = os.path.join(RESULTS, "phase3_fig_verdict_null.png")
    plt.savefig(p, dpi=300)
    plt.close()
    print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
