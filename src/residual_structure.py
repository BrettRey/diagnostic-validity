"""Phase 3 stage 2a -- residual-structure analysis (Gelman-style), the gate
before the headline measurement-model run.

The judges are ~0.8 pts stricter than the human gold. PPI removes a GLOBAL
offset from population estimates, but a judge-error term STRUCTURED BY ITEM or
STRATUM would distort the fitted network cell-by-cell (phantom edges). So:
partial-pool the judge-gold residual by item and by stratum (empirical Bayes,
since 25 cells/item is too few to trust raw means -- the Gelman move), put
uncertainty on everything, draw the secret-weapon / calibration / binned-residual
graphs, and read off the pre-stated outcome (i global / ii item-structured /
iii stratum-structured). Also the operative number: post-dichotomization judge-
vs-gold agreement at the pre-registered cuts.

  python src/residual_structure.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from analyze_phase3 import load_gold, load_judge  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")


def grid_map():
    """cell_id -> (diagnostic, stratum)."""
    m = {}
    with open(os.path.join(RESULTS, "phase3_grid_judgment.csv")) as f:
        for i, r in enumerate(csv.DictReader(f)):
            m[i] = (r["diagnostic"], r["stratum"])
    return m


def eb(groups):
    """Empirical-Bayes partial pooling of group residual means.
    Returns per-group (raw_mean, shrunk_mean, post_sd, n) + (grand, tau)."""
    keys = list(groups)
    mean = {k: float(np.mean(groups[k])) for k in keys}
    n = {k: len(groups[k]) for k in keys}
    wvar = {k: (float(np.var(groups[k], ddof=1)) if n[k] > 1 else 0.0)
            for k in keys}
    grand = float(np.mean(np.concatenate([groups[k] for k in keys])))
    gm = np.array([mean[k] for k in keys])
    se2 = np.array([wvar[k] / max(n[k], 1) for k in keys])
    tau2 = max(0.0, float(np.var(gm, ddof=1)) - float(np.mean(se2)))
    out = {}
    for k in keys:
        s2 = wvar[k] / max(n[k], 1)
        w = tau2 / (tau2 + s2) if (tau2 + s2) > 0 else 0.0
        shrunk = grand + w * (mean[k] - grand)
        post_sd = float(np.sqrt(1.0 / (1.0 / tau2 + 1.0 / s2))) if (tau2 > 0 and s2 > 0) \
            else (np.sqrt(s2) if tau2 == 0 else np.sqrt(tau2))
        out[k] = {"raw": round(mean[k], 3), "shrunk": round(shrunk, 3),
                  "post_sd": round(post_sd, 3), "n": n[k]}
    return out, round(grand, 3), round(float(np.sqrt(tau2)), 3)


def dich_kappa(gjudge, ggold, judge_all):
    """Binary judge-vs-gold agreement at the pre-registered cuts."""
    out = {}
    g = np.array([ggold[c] for c in ggold])
    j = np.array([gjudge[c] for c in ggold if c in gjudge])
    gc = np.array([c for c in ggold if c in gjudge])
    gg = np.array([ggold[c] for c in gc])
    jj = np.array([gjudge[c] for c in gc])
    # within-judge z>0: standardize over the judge's FULL distribution / gold's own
    jall = np.array(list(judge_all.values()))
    jz = (jj - jall.mean()) / jall.std()
    gz = (gg - g.mean()) / g.std()
    for name, jb, gb in [("z>0", jz > 0, gz > 0),
                         ("raw>=5", jj >= 5, gg >= 5),
                         ("raw>=4", jj >= 4, gg >= 4)]:
        jb, gb = jb.astype(int), gb.astype(int)
        out[name] = {
            "kappa": round(float(cohen_kappa_score(gb, jb, labels=[0, 1])), 3),
            "misclass_pct": round(100 * float(np.mean(jb != gb)), 1),
            "gold_accept_pct": round(100 * float(gb.mean()), 1),
            "judge_accept_pct": round(100 * float(jb.mean()), 1)}
    return out


def main():
    gold, _, _ = load_gold()
    gm = grid_map()
    judges = {"fable": load_judge("fable"), "gpt": load_judge("gpt")}
    res = {"global_offset": {}, "by_item": {}, "by_stratum": {},
           "by_gold_band": {}, "post_dichot": {}, "variance_sd": {}}

    # ---- residuals per judge ----
    perjudge_resid = {}
    for j, jd in judges.items():
        cells = [c for c in gold if c in jd]
        d = {c: jd[c] - gold[c] for c in cells}
        perjudge_resid[j] = d
        arr = np.array(list(d.values()))
        ci = stats.t.interval(0.95, len(arr) - 1, loc=arr.mean(),
                              scale=stats.sem(arr))
        res["global_offset"][j] = {"mean": round(float(arr.mean()), 3),
                                   "ci95": [round(ci[0], 3), round(ci[1], 3)],
                                   "sd": round(float(arr.std()), 3), "n": len(arr)}
        # by item (diagnostic)
        gi = {}
        for c, v in d.items():
            gi.setdefault(gm[c][0], []).append(v)
        gi = {k: np.array(v) for k, v in gi.items()}
        item_eb, grand_i, tau_item = eb(gi)
        res["by_item"][j] = item_eb
        # by stratum
        gs = {}
        for c, v in d.items():
            gs.setdefault(gm[c][1], []).append(v)
        gs = {k: np.array(v) for k, v in gs.items()}
        strat_eb, grand_s, tau_strat = eb(gs)
        res["by_stratum"][j] = strat_eb
        res["variance_sd"][j] = {"global": res["global_offset"][j]["mean"],
                                 "tau_item": tau_item, "tau_stratum": tau_strat}
        # by gold band (calibration / binned residual)
        gb = {}
        for c, v in d.items():
            gb.setdefault(gold[c], []).append(v)
        res["by_gold_band"][j] = {str(k): {"mean_resid": round(float(np.mean(v)), 3),
                                  "n": len(v), "mean_judge": round(float(np.mean(v)) + k, 3)}
                                  for k, v in sorted(gb.items())}
        # post-dichotomization
        res["post_dichot"][j] = dich_kappa(jd, gold, jd)

    # ---- pre-stated outcome read ----
    tau_i = max(res["variance_sd"][j]["tau_item"] for j in judges)
    tau_s = max(res["variance_sd"][j]["tau_stratum"] for j in judges)
    # stratum effects: do any strata separate from the global offset by >1 post_sd?
    sep = {}
    for j in judges:
        for s, e in res["by_stratum"][j].items():
            z = abs(e["shrunk"] - res["global_offset"][j]["mean"]) / max(e["post_sd"], 1e-6)
            if z > 2:
                sep.setdefault(j, []).append((s, e["shrunk"], round(z, 1)))
    res["outcome"] = {"tau_item_max": tau_i, "tau_stratum_max": tau_s,
                      "strata_separating_2sd": sep,
                      "read": ("iii_stratum_structured" if sep else
                               ("ii_item_structured" if tau_i > 0.4 else
                                "i_global_offset"))}

    with open(os.path.join(RESULTS, "phase3_residual_structure.json"), "w") as f:
        json.dump(res, f, indent=2)

    # ---- figures (Gelman: graphs, dotplots+intervals, small multiples) ----
    _fig_secret(res, judges)
    _fig_calibration(res, judges)

    # ---- console summary ----
    print("GLOBAL OFFSET (judge-gold; negative = judge stricter / you more permissive):")
    for j in judges:
        g = res["global_offset"][j]
        print(f"  {j}: {g['mean']:+.2f}  95%CI[{g['ci95'][0]:+.2f},{g['ci95'][1]:+.2f}]  "
              f"tau_item={res['variance_sd'][j]['tau_item']}  tau_stratum={res['variance_sd'][j]['tau_stratum']}")
    print("\nPER-STRATUM residual (shrunk +/- post_sd):")
    for j in judges:
        print(f"  {j}:", {s: f"{e['shrunk']:+.2f}+/-{e['post_sd']:.2f}"
                          for s, e in res["by_stratum"][j].items()})
    print("\nPOST-DICHOTOMIZATION judge-vs-gold (the operative binary number):")
    for j in judges:
        for cut, d in res["post_dichot"][j].items():
            print(f"  {j} {cut:<7}: kappa={d['kappa']:.3f} misclass={d['misclass_pct']:.1f}% "
                  f"(gold accept {d['gold_accept_pct']:.0f}%, judge {d['judge_accept_pct']:.0f}%)")
    print("\nOUTCOME read:", res["outcome"]["read"],
          "| tau_item_max", tau_i, "| tau_stratum_max", tau_s,
          "| strata separating >2sd:", sep or "none")


def _fig_secret(res, judges):
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    colors = {"fable": "#1f77b4", "gpt": "#d62728"}
    # left: per-item, ordered by fable shrunk residual
    items = sorted(res["by_item"]["fable"],
                   key=lambda k: res["by_item"]["fable"][k]["shrunk"])
    y = np.arange(len(items))
    ax = axes[0]
    for j in judges:
        xs = [res["by_item"][j][k]["shrunk"] for k in items]
        es = [1.96 * res["by_item"][j][k]["post_sd"] for k in items]
        off = -0.15 if j == "fable" else 0.15
        ax.errorbar(xs, y + off, xerr=es, fmt="o", ms=4, color=colors[j],
                    label=j, capsize=2, lw=1)
    ax.axvline(0, color="k", lw=0.8)
    for j in judges:
        ax.axvline(res["global_offset"][j]["mean"], color=colors[j], ls="--", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(items, fontsize=7)
    ax.set_xlabel("judge - gold residual (shrunk, 95% CI)")
    ax.set_title("Per-item residuals (secret weapon)\ndashed = each judge's global offset")
    ax.legend(fontsize=8)
    # right: per-stratum
    ax = axes[1]
    strata = ["boundary", "determinative", "preposition", "adjective", "blind"]
    strata = [s for s in strata if s in res["by_stratum"]["fable"]]
    y = np.arange(len(strata))
    for j in judges:
        xs = [res["by_stratum"][j][s]["shrunk"] for s in strata]
        es = [1.96 * res["by_stratum"][j][s]["post_sd"] for s in strata]
        off = -0.1 if j == "fable" else 0.1
        ax.errorbar(xs, y + off, xerr=es, fmt="s", ms=7, color=colors[j],
                    label=j, capsize=3, lw=1.5)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(strata)
    ax.set_xlabel("judge - gold residual (shrunk, 95% CI)")
    ax.set_title("Per-stratum residuals\n(structure here = category-correlated error)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    p = os.path.join(RESULTS, "phase3_fig_residual_structure.png")
    plt.savefig(p, dpi=130)
    plt.close()
    print("wrote", os.path.relpath(p, ROOT))


def _fig_calibration(res, judges):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    colors = {"fable": "#1f77b4", "gpt": "#d62728"}
    ax = axes[0]
    for j in judges:
        bands = res["by_gold_band"][j]
        xs = [int(k) for k in bands]
        ys = [bands[k]["mean_judge"] for k in bands]
        ax.plot(xs, ys, "o-", color=colors[j], label=j)
    ax.plot([1, 7], [1, 7], "k--", lw=0.8, label="y=x (perfect)")
    ax.set_xlabel("your gold rating")
    ax.set_ylabel("mean judge rating")
    ax.set_title("Calibration (below diagonal = judge stricter)")
    ax.legend(fontsize=8)
    ax = axes[1]
    for j in judges:
        bands = res["by_gold_band"][j]
        xs = [int(k) for k in bands]
        ys = [bands[k]["mean_resid"] for k in bands]
        ax.plot(xs, ys, "o-", color=colors[j], label=j)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("your gold rating")
    ax.set_ylabel("mean residual (judge - gold)")
    ax.set_title("Binned residuals by gold band")
    ax.legend(fontsize=8)
    plt.tight_layout()
    p = os.path.join(RESULTS, "phase3_fig_calibration.png")
    plt.savefig(p, dpi=130)
    plt.close()
    print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
