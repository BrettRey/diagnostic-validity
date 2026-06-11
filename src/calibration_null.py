"""Phase 3 stage 2a, catches 1 & 2 -- de-artifact the calibration finding
before it becomes an instrument-characterization claim.

CATCH 1: plotting (judge-gold) vs gold mechanically produces a negative slope
(floor at gold=1, regression-to-the-mean through the middle) even for a judge
that is gold + symmetric noise. So (a) Bland-Altman: residual vs the MEAN of
judge & gold (kills the mechanical slope), and (b) a fake-data null: judges =
gold + noise rank-mapped to the observed judge marginal, matched to the observed
correlation; run the identical frown; the instrument claim is the EXCESS of the
real frown over the null band.

CATCH 2: morphology items live disproportionately in the gold 4-6 zone, so
tau_item may be the one compression curve refracted through item difficulty.
Re-pool item effects CONDITIONAL on gold level (subtract the curve first). If
conditional tau_item survives -> outcome (ii) stands, morphology-out arm. If it
collapses -> one nonlinearity, and the better arm is a calibrated cut.

  python src/calibration_null.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import plot_style  # house chart style
plot_style.setup()
from analyze_phase3 import load_gold, load_judge  # noqa: E402
from residual_structure import grid_map, eb  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
SEED = 26
B = 1000


def qmap(cont, marginal):
    """Rank-map a continuous vector onto the empirical marginal (preserves it)."""
    out = np.empty_like(cont, dtype=float)
    out[np.argsort(cont, kind="stable")] = np.sort(marginal)
    return out


def fit_sigma(g, target_r, marginal, rng):
    """sigma s.t. corr(rankmap(gold+noise), gold) ~ observed r."""
    best = None
    for s in np.linspace(0.05, 4.0, 60):
        rr = np.mean([stats.pearsonr(qmap(g + rng.normal(0, s, g.size),
                                          marginal), g)[0] for _ in range(8)])
        if best is None or abs(rr - target_r) < best[1]:
            best = (s, abs(rr - target_r), rr)
    return best[0], best[2]


def main():
    gold, _, _ = load_gold()
    gm = grid_map()
    judges = {"fable": load_judge("fable"), "gpt": load_judge("gpt")}
    out = {}
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    for col, (j, jd) in enumerate(judges.items()):
        rng = np.random.default_rng(SEED)
        cells = [c for c in gold if c in jd]
        g = np.array([gold[c] for c in cells], float)
        v = np.array([jd[c] for c in cells], float)
        resid = v - g
        r = float(stats.pearsonr(v, g)[0])
        levels = sorted(set(g.tolist()))

        # ---- CATCH 1: fake-data null ----
        sigma, got_r = fit_sigma(g, r, v, rng)
        real = {L: float((v[g == L] - L).mean()) for L in levels}
        fake = {L: [] for L in levels}
        for _ in range(B):
            fk = qmap(g + rng.normal(0, sigma, g.size), v)
            for L in levels:
                fake[L].append(float((fk[g == L] - L).mean()))
        null_mid = {L: float(np.mean(fake[L])) for L in levels}
        null_lo = {L: float(np.percentile(fake[L], 2.5)) for L in levels}
        null_hi = {L: float(np.percentile(fake[L], 97.5)) for L in levels}
        excess = {L: round(real[L] - null_mid[L], 2) for L in levels}
        surv = {L: (real[L] < null_lo[L] or real[L] > null_hi[L]) for L in levels}

        # ---- CATCH 2: conditional item effects ----
        adj = np.array([resid[i] - real[g[i]] for i in range(len(g))])
        gi_u, gi_c = {}, {}
        for i, c in enumerate(cells):
            gi_u.setdefault(gm[c][0], []).append(resid[i])
            gi_c.setdefault(gm[c][0], []).append(adj[i])
        eb_u, _, tau_u = eb({k: np.array(x) for k, x in gi_u.items()})
        eb_c, _, tau_c = eb({k: np.array(x) for k, x in gi_c.items()})
        # morphology items: do they survive curve-conditioning?
        morph = ["ness_nominalization", "un_prefix", "ly_adverb_base",
                 "inflectional_comparison"]
        morph_cond = {m: eb_c.get(m, {}).get("shrunk") for m in morph}

        out[j] = {
            "r": round(r, 3), "sigma": round(sigma, 2), "null_r": round(got_r, 3),
            "real_frown": {str(L): round(real[L], 2) for L in levels},
            "null_mid": {str(L): round(null_mid[L], 2) for L in levels},
            "null_ci": {str(L): [round(null_lo[L], 2), round(null_hi[L], 2)]
                        for L in levels},
            "excess_over_null": {str(L): excess[L] for L in levels},
            "real_outside_null_band": {str(L): bool(surv[L]) for L in levels},
            "tau_item_unconditional": tau_u,
            "tau_item_conditional_on_gold": tau_c,
            "morphology_item_effect_conditional": morph_cond,
        }

        # ---- figures ----
        ax = axes[0, col]
        xs = levels
        ax.plot(xs, [real[L] for L in xs], "o-", color=plot_style.COLORS["primary"], lw=2,
                label="real frown")
        ax.plot(xs, [null_mid[L] for L in xs], "s--", color="grey",
                label="mechanical null (mean)")
        ax.fill_between(xs, [null_lo[L] for L in xs], [null_hi[L] for L in xs],
                        color="grey", alpha=0.25, label="null 95%")
        ax.axhline(0, color="k", lw=0.6)
        ax.set_title(f"{j}: real frown vs mechanical null\n(excess = instrument claim)")
        ax.set_xlabel("your gold rating")
        ax.set_ylabel("mean residual (judge - gold)")
        ax.legend(fontsize=8)
        # Bland-Altman
        ax = axes[1, col]
        m = (v + g) / 2
        ax.scatter(m + rng.normal(0, 0.05, m.size), resid + rng.normal(0, 0.05, resid.size),
                   s=6, alpha=0.3, color=plot_style.COLORS["primary"])
        bs = stats.linregress(m, resid)
        xx = np.array([m.min(), m.max()])
        ax.plot(xx, bs.intercept + bs.slope * xx, "-", color=plot_style.COLORS["secondary"], lw=2,
                label=f"slope={bs.slope:+.2f} (p={bs.pvalue:.1e})")
        ax.axhline(resid.mean(), color="k", ls="--", lw=0.8,
                   label=f"mean={resid.mean():+.2f}")
        ax.set_title(f"{j}: Bland-Altman (residual vs mean)\nflat = pure offset; slope = real")
        ax.set_xlabel("(judge + gold)/2")
        ax.set_ylabel("judge - gold")
        ax.legend(fontsize=8)
        out[j]["bland_altman_slope"] = round(float(bs.slope), 3)
        out[j]["bland_altman_p"] = float(bs.pvalue)

    plt.tight_layout()
    p = os.path.join(RESULTS, "phase3_fig_calibration_null.png")
    plt.savefig(p, dpi=300)
    plt.close()
    with open(os.path.join(RESULTS, "phase3_calibration_null.json"), "w") as f:
        json.dump(out, f, indent=2)

    # ---- console ----
    for j in judges:
        o = out[j]
        print(f"\n=== {j} (r={o['r']}, null sigma={o['sigma']}, null_r={o['null_r']}) ===")
        print("  gold | real | null_mid [95%] | excess | outside_null?")
        for L in ["1", "2", "3", "4", "5", "6", "7"]:
            if L in o["real_frown"]:
                print(f"   {L}   | {o['real_frown'][L]:+.2f} | {o['null_mid'][L]:+.2f} "
                      f"[{o['null_ci'][L][0]:+.2f},{o['null_ci'][L][1]:+.2f}] | "
                      f"{o['excess_over_null'][L]:+.2f} | {o['real_outside_null_band'][L]}")
        print(f"  Bland-Altman slope={o['bland_altman_slope']:+.3f} (p={o['bland_altman_p']:.1e})")
        print(f"  tau_item: unconditional={o['tau_item_unconditional']} -> "
              f"conditional-on-gold={o['tau_item_conditional_on_gold']}")
        print(f"  morphology items (conditional shrunk effect): {o['morphology_item_effect_conditional']}")
    print("\nwrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
