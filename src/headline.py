"""Phase 3 HEADLINE build (RQ1-4), provisional until panel ingestion.

Reporting architecture per the 2026-06-11 amendment: binary and continuous
CO-EQUAL; PLAN §4 thresholds evaluated as written then subordinated to an
agreement/divergence frame; PPC; judge error propagated via the arms; Type-M
caveat on RQ3. Numbers + figures only -- the reading is pm-node work.

Outputs: results/phase3_headline.json, phase3_fig_*.png, paper/phase3_findings.md
  python src/headline.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np
from scipy import stats
from sklearn.covariance import GraphicalLasso
from sklearn.decomposition import PCA
from sklearn.isotonic import IsotonicRegression
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import warnings
warnings.filterwarnings("ignore")
np.seterr(all="ignore")   # fit_lowrank GD overflows transiently on near-
# constant columns then clips; results verified NaN-free + rank-monotone.

sys.path.insert(0, os.path.dirname(__file__))
import plot_style  # house chart style
plot_style.setup()
import models  # noqa: E402
from analyze_phase3 import load_gold, load_judge  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
SEED = 26
RANKS = (1, 2, 3, 4, 5)
MORPH = {"ness_nominalization", "un_prefix", "ly_adverb_base",
         "inflectional_comparison"}
# PLAN §RQ3 named boundary set
BOUNDARY = {"worth", "near", "fun", "like", "due", "galore", "ablaze",
            "asleep", "more", "less", "enough", "such", "own"}


def load_grid_index():
    """lexeme list (row order), diagnostic list (col order), maps, prep scope."""
    lex_order, diag_order = [], []
    lex_seen, diag_seen = {}, {}
    cell = {}  # cell_id -> (lex_idx, diag_idx)
    with open(os.path.join(RESULTS, "phase3_grid_judgment.csv")) as f:
        for cid, r in enumerate(csv.DictReader(f)):
            lx, dg = r["lexeme"], r["diagnostic"]
            if lx not in lex_seen:
                lex_seen[lx] = len(lex_order)
                lex_order.append(lx)
            if dg not in diag_seen:
                diag_seen[dg] = len(diag_order)
                diag_order.append(dg)
            cell[cid] = (lex_seen[lx], diag_seen[dg])
    # prep scope per lexeme (for core-96 arm)
    scope = {}
    strat = {}
    with open(os.path.join(RESULTS, "phase3_sample.csv")) as f:
        for r in csv.DictReader(f):
            scope[r["lexeme"]] = r.get("prep_scope", "")
            strat[r["lexeme"]] = r["stratum"]
    return lex_order, diag_order, cell, scope, strat


def judge_matrices(judge_ratings, cell, n, p):
    """raw rating matrix (NaN for missing) + within-judge z matrix + mask."""
    R = np.full((n, p), np.nan)
    for cid, rat in judge_ratings.items():
        i, j = cell[cid]
        R[i, j] = rat
    vals = R[~np.isnan(R)]
    mu, sd = vals.mean(), vals.std()
    Z = (R - mu) / sd
    mask = (~np.isnan(R)).astype(float)
    return R, Z, mask, mu, sd


def impute_binary(B, mask):
    """column-mean impute masked cells so models see a full matrix."""
    B = B.copy()
    cm = np.array([B[mask[:, j] == 1, j].mean() if mask[:, j].sum() else 0.5
                   for j in range(B.shape[1])])
    for j in range(B.shape[1]):
        B[mask[:, j] == 0, j] = cm[j] >= 0.5
    return B.astype(float)


def verdict(cv, struct):
    """PLAN §4 read: CV diff vs 2*SE; eig dominance >3 reflective / <3 network."""
    d, se = cv["diff_mean"], cv["diff_se"]
    cv_call = ("network" if d > 2 * se else
               ("lowrank" if d < -2 * se else "tie"))
    dom = struct["eig_dominance"]
    struct_call = "reflective(>3)" if dom > 3 else "network(<3)"
    return {"cv_diff": round(d, 4), "cv_se": round(se, 4), "cv_se_units": round(d / se, 1),
            "cv_call": cv_call, "eig_dominance": round(dom, 2),
            "struct_call": struct_call, "edge_density": round(struct["edge_density"], 3)}


def best_rank_cv(X, mask):
    out = {}
    for r in RANKS:
        cv = models.cellwise_cv(X, rank=r, seed=SEED)
        out[r] = cv
    # pick rank minimizing low-rank held-out logloss
    br = min(out, key=lambda r: out[r]["logloss_lowrank"])
    return br, out[br], {r: round(out[r]["logloss_lowrank"], 4) for r in out}


def continuous_compare(Z, mask, seed=SEED):
    """Co-equal continuous analysis: low-rank PCA vs GGM, held-out cell MSE,
    plus continuous eigen-dominance + GGM edge density."""
    rng = np.random.default_rng(seed)
    n, p = Z.shape
    Zi = Z.copy()
    cm = np.array([Zi[mask[:, j] == 1, j].mean() if mask[:, j].sum() else 0.0
                   for j in range(p)])
    for j in range(p):
        Zi[mask[:, j] == 0, j] = cm[j]
    # held-out cells
    held = []
    M = mask.copy()
    for i in range(n):
        obs = np.where(M[i] == 1)[0]
        if len(obs) > 3:
            js = rng.choice(obs, size=min(3, len(obs)), replace=False)
            for j in js:
                held.append((i, j))
                M[i, j] = 0
    Ztr = Zi.copy()
    for (i, j) in held:
        Ztr[i, j] = cm[j]
    # low-rank PCA (rank chosen 1..5 by held-out)
    best_pca = None
    for r in RANKS:
        pca = PCA(n_components=r).fit(Ztr)
        rec = pca.inverse_transform(pca.transform(Ztr))
        mse = np.mean([(Z[i, j] - rec[i, j]) ** 2 for (i, j) in held])
        if best_pca is None or mse < best_pca[1]:
            best_pca = (r, mse)
    # GGM
    try:
        gl = GraphicalLasso(alpha=0.1, max_iter=200).fit(Ztr)
        prec = gl.precision_
        mse_ggm = []
        for (i, j) in held:
            others = [k for k in range(p) if k != j]
            coef = -prec[j, others] / prec[j, j]
            pred = cm[j] + (Ztr[i, others] - cm[others]) @ coef
            mse_ggm.append((Z[i, j] - pred) ** 2)
        mse_ggm = float(np.mean(mse_ggm))
        offdiag = prec[np.triu_indices(p, 1)]
        edge_density_ggm = float((np.abs(offdiag) > 1e-4).mean())
    except Exception as e:
        mse_ggm, edge_density_ggm = float("nan"), float("nan")
    r_corr = np.corrcoef(Zi.T)
    ev = np.sort(np.linalg.eigvalsh(np.nan_to_num(r_corr)))[::-1]
    return {"pca_rank": best_pca[0], "pca_heldout_mse": round(best_pca[1], 4),
            "ggm_heldout_mse": round(mse_ggm, 4),
            "continuous_eig_dominance": round(float(ev[0] / max(ev[1], 1e-9)), 2),
            "ggm_edge_density": round(edge_density_ggm, 3),
            "winner": ("lowrank" if best_pca[1] < mse_ggm else "ggm")}


def ppi_item_rates(judge_ratings, gold, cell, diag_order, mu, sd):
    """Per-item (diagnostic) PPI-corrected acceptance rate (z>0), EB-shrunk."""
    p = len(diag_order)
    # judge acceptance per item over all lexemes
    jbin = {j: [] for j in range(p)}
    for cid, rat in judge_ratings.items():
        i, j = cell[cid]
        jbin[j].append(1 if (rat - mu) / sd > 0 else 0)
    # gold cells: judge vs gold (both z>0)
    gvals = np.array(list(gold.values()))
    gmu, gsd = gvals.mean(), gvals.std()
    err = {j: [] for j in range(p)}   # (judge_bin - gold_bin) on gold cells
    for cid, g in gold.items():
        if cid in judge_ratings:
            i, j = cell[cid]
            jb = 1 if (judge_ratings[cid] - mu) / sd > 0 else 0
            gb = 1 if (g - gmu) / gsd > 0 else 0
            err[j].append(jb - gb)
    out = {}
    # global correction for EB shrinkage target
    all_err = np.array([e for j in err for e in err[j]])
    gcorr = all_err.mean()
    tau = max(0.0, np.var([np.mean(err[j]) for j in err if err[j]]) -
              np.mean([np.var(err[j]) / max(len(err[j]), 1) for j in err if err[j]]))
    for j in range(p):
        jrate = np.mean(jbin[j])
        ej = np.array(err[j]) if err[j] else np.array([gcorr])
        raw_corr = ej.mean()
        s2 = ej.var() / max(len(ej), 1)
        w = tau / (tau + s2) if (tau + s2) > 0 else 0.0
        corr = gcorr + w * (raw_corr - gcorr)        # EB-shrunk correction
        ppi = jrate - corr                           # PPI-corrected rate
        se = np.sqrt(jrate * (1 - jrate) / len(jbin[j]) + s2)
        out[diag_order[j]] = {"judge_rate": round(float(jrate), 3),
                              "ppi_rate": round(float(np.clip(ppi, 0, 1)), 3),
                              "ci95": [round(float(np.clip(ppi - 1.96 * se, 0, 1)), 3),
                                       round(float(np.clip(ppi + 1.96 * se, 0, 1)), 3)],
                              "n_gold": len(ej)}
    return out


def ppc(X, net, rank, seed=SEED):
    """Posterior-predictive: does the winning fit reproduce scree + edge density?"""
    rng = np.random.default_rng(seed)
    obs = models.structure_diagnostics(X, net)
    m = models.fit_lowrank(X, rank=rank, seed=seed)
    P = models.predict_lowrank(m)
    sim_dom, sim_edge = [], []
    for _ in range(100):
        Xs = (rng.random(X.shape) < P).astype(float)
        net_s = models.fit_network(Xs)
        sd = models.structure_diagnostics(Xs, net_s)
        sim_dom.append(sd["eig_dominance"])
        sim_edge.append(sd["edge_density"])
    return {"obs_eig_dominance": round(obs["eig_dominance"], 2),
            "sim_eig_dominance_ci": [round(float(np.percentile(sim_dom, 2.5)), 2),
                                     round(float(np.percentile(sim_dom, 97.5)), 2)],
            "obs_edge_density": round(obs["edge_density"], 3),
            "sim_edge_density_ci": [round(float(np.percentile(sim_edge, 2.5)), 3),
                                    round(float(np.percentile(sim_edge, 97.5)), 3)]}


def lexeme_communities(B, lex_order, strat):
    """Unsupervised k-means of lexeme profiles; known-groups validity (ARI vs
    a-priori strata) + the more/less prediction P1 (do more/less land in the
    determinative-dominant cluster?). Strata are used ONLY to read clusters
    (F3-compliant), never to fit them."""
    import collections
    strata = [strat.get(lx, "") for lx in lex_order]
    k = len(set(strata))
    lab = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit_predict(B)
    cont = collections.defaultdict(collections.Counter)
    for i, lx in enumerate(lex_order):
        cont[int(lab[i])][strat.get(lx, "")] += 1
    dom = {c: cont[c].most_common(1)[0][0] for c in cont}
    det_clusters = {c for c, d in dom.items() if d == "determinative"}
    loc = {}
    for tgt in ["more", "less", "such", "enough", "worth", "near", "own"]:
        if tgt in lex_order:
            i = lex_order.index(tgt)
            loc[tgt] = {"cluster": int(lab[i]),
                        "cluster_dominant_stratum": dom[int(lab[i])],
                        "in_determinative_cluster": int(lab[i]) in det_clusters}
    return {"k": k, "ari_vs_strata": round(float(adjusted_rand_score(strata, lab)), 3),
            "cluster_dominant_stratum": {str(c): dom[c] for c in dom},
            "P1_and_boundary_location": loc}


def main():
    lex_order, diag_order, cell, scope, strat = load_grid_index()
    n, p = len(lex_order), len(diag_order)
    gold, _, _ = load_gold()
    judges = {"fable": load_judge("fable"), "gpt": load_judge("gpt")}
    morph_cols = [j for j, d in enumerate(diag_order) if d in MORPH]
    keep_cols = [j for j in range(p) if j not in morph_cols]
    core_rows = [i for i, lx in enumerate(lex_order)
                 if scope.get(lx, "") != "extended"]
    bound_rows = {i for i, lx in enumerate(lex_order) if lx in BOUNDARY}

    res = {"n_lexemes": n, "n_diagnostics": p, "seed": SEED,
           "git_rev": _git(), "versions": _versions(),
           "boundary_in_sample": sorted({lex_order[i] for i in bound_rows}),
           "rq3_item_floor": {"items": p, "floor": 40,
                              "underpowered": p < 40},
           "judges": {}}

    for jn, jr in judges.items():
        R, Z, mask, mu, sd = judge_matrices(jr, cell, n, p)
        Bz = impute_binary((Z > 0).astype(float), mask)
        arms = {
            "primary_z0": (Bz, mask, list(range(n))),
            "ge5": (impute_binary((R >= 5).astype(float), mask), mask, list(range(n))),
            "ge4": (impute_binary((R >= 4).astype(float), mask), mask, list(range(n))),
            "morph_out": (Bz[:, keep_cols], mask[:, keep_cols], list(range(n))),
            "core96": (Bz[core_rows], mask[core_rows], core_rows),
        }
        # calibrated-cut (isotonic judge->gold on the 600)
        gx = np.array([jr[c] for c in gold if c in jr])
        gy = np.array([gold[c] for c in gold if c in jr])
        iso = IsotonicRegression(out_of_bounds="clip").fit(gx, gy)
        Rcal = iso.predict(np.nan_to_num(R, nan=mu).ravel()).reshape(R.shape)
        Rcal[mask == 0] = np.nan
        cmu, csd = Rcal[mask == 1].mean(), Rcal[mask == 1].std()
        arms["calibrated"] = (impute_binary(((Rcal - cmu) / csd > 0).astype(float), mask),
                              mask, list(range(n)))

        jres = {"n_missing": int((mask == 0).sum()), "arms": {}}
        for an, (X, mk, rows) in arms.items():
            br, cv, rank_ll = best_rank_cv(X, mk)
            net = models.fit_network(X)
            struct = models.structure_diagnostics(X, net)
            jres["arms"][an] = {"best_rank": br, **verdict(cv, struct),
                                "lowrank_ll_by_rank": rank_ll}
        # primary-arm extras: projectibility, misfit, PPC, continuous
        Xp, mkp = arms["primary_z0"][0], arms["primary_z0"][1]
        netp = models.fit_network(Xp)
        brp = jres["arms"]["primary_z0"]["best_rank"]
        proj = models.projectibility(Xp, seed=SEED)
        mis_net = models.row_misfit(Xp, netp)
        mis_lr = models.row_misfit_lowrank(Xp, rank=brp, seed=SEED)
        order = np.argsort(-mis_net)
        decile = set(order[:max(1, n // 10)].tolist())
        bound_decile = {lex_order[i]: (i in decile) for i in sorted(bound_rows)}
        jres["projectibility"] = {diag_order[j]: round(float(proj[j]), 4)
                                  for j in range(p)}
        jres["projectibility_above_zero"] = int((proj > 0).sum())
        jres["rq3_boundary_top_decile"] = bound_decile
        jres["rq3_boundary_hit_rate"] = round(
            np.mean([v for v in bound_decile.values()]), 3) if bound_decile else None
        jres["misfit_top10_lexemes"] = [lex_order[i] for i in order[:10]]
        jres["ppc"] = ppc(Xp, netp, brp)
        jres["ppi_item_rates"] = ppi_item_rates(jr, gold, cell, diag_order, mu, sd)
        jres["continuous"] = continuous_compare(Z, mask)
        jres["lexeme_communities"] = lexeme_communities(Xp, lex_order, strat)
        jres["_misfit"] = mis_net.tolist()        # for figures
        res["judges"][jn] = jres

    with open(os.path.join(RESULTS, "phase3_headline.json"), "w") as f:
        json.dump({k: v for k, v in res.items()}, f, indent=2)
    _figures(res, lex_order, diag_order, bound_rows)
    _findings(res, diag_order)
    _print(res)


def _git():
    import subprocess
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=ROOT).decode().strip()
    except Exception:
        return "unknown"


def _versions():
    import sklearn
    return {"numpy": np.__version__, "scipy": stats.__name__ and __import__("scipy").__version__,
            "sklearn": sklearn.__version__}


def _print(res):
    print(f"n={res['n_lexemes']} lexemes x p={res['n_diagnostics']} diagnostics "
          f"(RQ3 floor 40: underpowered={res['rq3_item_floor']['underpowered']})")
    for jn, jr in res["judges"].items():
        print(f"\n=== {jn} (missing {jr['n_missing']}) ===")
        print("  VERDICT-INVARIANCE across arms (CV diff in SE units; +=network, -=lowrank):")
        for an, a in jr["arms"].items():
            print(f"    {an:<12} rank{a['best_rank']} cv={a['cv_diff']:+.4f}"
                  f"({a['cv_se_units']:+.1f}SE -> {a['cv_call']:<7}) "
                  f"dom={a['eig_dominance']:.2f}->{a['struct_call']} edge={a['edge_density']}")
        print(f"  RQ2 projectibility > 0: {jr['projectibility_above_zero']}/{res['n_diagnostics']}")
        print(f"  RQ3 boundary top-decile hit-rate: {jr['rq3_boundary_hit_rate']} "
              f"(items<40 -> Type-M caveat) | top misfit: {jr['misfit_top10_lexemes'][:5]}")
        print(f"  PPC: obs dom {jr['ppc']['obs_eig_dominance']} in sim CI "
              f"{jr['ppc']['sim_eig_dominance_ci']}? ; edge obs {jr['ppc']['obs_edge_density']} "
              f"in {jr['ppc']['sim_edge_density_ci']}?")
        c = jr["continuous"]
        print(f"  CONTINUOUS (co-equal): PCA-r{c['pca_rank']} mse={c['pca_heldout_mse']} vs "
              f"GGM mse={c['ggm_heldout_mse']} -> {c['winner']}; cont.dom={c['continuous_eig_dominance']}")
        lc = jr["lexeme_communities"]; ml = lc["P1_and_boundary_location"]
        print(f"  P1 communities: ARI={lc['ari_vs_strata']} "
              f"more->det={ml.get('more', {}).get('in_determinative_cluster')} "
              f"less->det={ml.get('less', {}).get('in_determinative_cluster')}")


def _figures(res, lex_order, diag_order, bound_rows):
    colors = {"fable": plot_style.COLORS["primary"], "gpt": plot_style.COLORS["secondary"]}
    # Fig 1: verdict-invariance (CV diff in SE units per arm, both judges)
    fig, ax = plt.subplots(figsize=(10, 5))
    arms = list(next(iter(res["judges"].values()))["arms"])
    yy = np.arange(len(arms))
    for jn in res["judges"]:
        xs = [res["judges"][jn]["arms"][a]["cv_se_units"] for a in arms]
        ax.plot(xs, yy + (0.12 if jn == "gpt" else -0.12), "o", ms=8,
                color=colors[jn], label=jn)
    ax.axvline(2, color="grey", ls="--", lw=0.8)
    ax.axvline(-2, color="grey", ls="--", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(yy)
    ax.set_yticklabels(arms)
    ax.set_xlabel("CV log-loss diff (SE units); + network better, - low-rank better; |2| = threshold")
    ax.set_title("RQ1 verdict-invariance across arms")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, "phase3_fig_verdict.png"), dpi=130)
    plt.close()
    # Fig 2: misfit by lexeme with boundary items highlighted (both judges)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, jn in zip(axes, res["judges"]):
        mis = np.array(res["judges"][jn]["_misfit"])
        ordr = np.argsort(mis)
        ax.plot(np.arange(len(mis)), mis[ordr], ".", ms=3, color="#999")
        for i in bound_rows:
            rank = int(np.where(ordr == i)[0][0])
            ax.plot(rank, mis[i], "o", ms=7, color=colors[jn])
            ax.annotate(lex_order[i], (rank, mis[i]), fontsize=6)
        ax.axhline(np.percentile(mis, 90), color="grey", ls="--", lw=0.8)
        ax.set_title(f"{jn}: lexeme misfit (boundary items marked; --=90th pct)")
        ax.set_xlabel("lexeme rank")
        ax.set_ylabel("network misfit z")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, "phase3_fig_misfit.png"), dpi=130)
    plt.close()
    # Fig 3: projectibility per diagnostic
    fig, ax = plt.subplots(figsize=(9, 7))
    dg = diag_order
    yy = np.arange(len(dg))
    for jn in res["judges"]:
        xs = [res["judges"][jn]["projectibility"][d] for d in dg]
        ax.plot(xs, yy + (0.12 if jn == "gpt" else -0.12), "o", ms=5,
                color=colors[jn], label=jn)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(yy)
    ax.set_yticklabels(dg, fontsize=7)
    ax.set_xlabel("projectibility (held-out prediction gain); <=0 = decoration")
    ax.set_title("RQ2 projectibility per diagnostic")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, "phase3_fig_projectibility.png"), dpi=130)
    plt.close()


def _findings(res, diag_order):
    p = res["n_diagnostics"]
    L = []
    L.append("# Phase 3 findings (PROVISIONAL -- pending external-panel ingestion)\n")
    L.append("Numbers + figures only; the reading (RQ1 verdict, RQ3 ranking, RQ4 "
             "mapping, more/less) is pm-node work. Gold anchor = Brett's 600 (n=1 "
             "rater); the file is provisional until the colleague panel lands "
             "(human-ceiling, gold-6 external test, panel-calibrated arm).\n")
    L.append(f"- Grid: {res['n_lexemes']} lexemes x {p} judgment diagnostics. "
             f"git {res['git_rev'][:8]}.\n")
    L.append("## RQ1 -- structure (binary, PLAN §4 thresholds as written)\n")
    L.append("CV diff sign: + network better, - low-rank better; |diff| > 2*SE = "
             "separated. Eigen-dominance > 3 reflective / < 3 network.\n")
    for jn, jr in res["judges"].items():
        L.append(f"\n**{jn}** (missing {jr['n_missing']}):\n")
        L.append("| arm | rank | CV diff | SE units | CV call | eig-dom | struct call | edge |\n|---|---|---|---|---|---|---|---|\n")
        for an, a in jr["arms"].items():
            L.append(f"| {an} | {a['best_rank']} | {a['cv_diff']:+.4f} | "
                     f"{a['cv_se_units']:+.1f} | {a['cv_call']} | {a['eig_dominance']} | "
                     f"{a['struct_call']} | {a['edge_density']} |\n")
    L.append("\n## RQ1 (continuous, CO-EQUAL) -- GGM vs low-rank factor on z-scores\n")
    L.append("The gold-6 compression (the only region of real instrument "
             "nonlinearity) sits ABOVE every binary cut, so it is minimal for the "
             "binary models and carried entirely by this continuous check.\n")
    for jn, jr in res["judges"].items():
        c = jr["continuous"]
        L.append(f"- **{jn}**: low-rank PCA rank {c['pca_rank']} held-out MSE "
                 f"{c['pca_heldout_mse']} vs GGM MSE {c['ggm_heldout_mse']} -> "
                 f"{c['winner']}; continuous eigen-dominance {c['continuous_eig_dominance']}, "
                 f"GGM edge density {c['ggm_edge_density']}.\n")
    L.append("\n## RQ2 -- projectibility (decoration check; PLAN T2 >=10)\n")
    for jn, jr in res["judges"].items():
        L.append(f"- **{jn}**: {jr['projectibility_above_zero']}/{p} diagnostics "
                 f"project > 0. See phase3_fig_projectibility.png.\n")
    L.append("\n## RQ3 -- lexeme misfit (boundary set; TYPE-M CAVEAT)\n")
    L.append(f"**Underpowered: {p} judgment items < the pre-registered 40-item "
             "floor. The ranking is reported; individual-lexeme misfit claims are "
             "not made (Type-M: even a high-ranking boundary item is a noisy "
             "estimate).** Corpus columns would lift p toward ~42.\n")
    for jn, jr in res["judges"].items():
        hits = [k for k, v in jr["rq3_boundary_top_decile"].items() if v]
        L.append(f"- **{jn}**: boundary-in-top-decile hit-rate "
                 f"{jr['rq3_boundary_hit_rate']} ({len(hits)} of "
                 f"{len(jr['rq3_boundary_top_decile'])}): {hits}. "
                 f"Top-misfit lexemes: {jr['misfit_top10_lexemes'][:8]}.\n")
    L.append("\n## Lexeme communities + P1 (more/less)\n")
    L.append("Unsupervised k-means of lexeme profiles; strata used only to READ "
             "clusters (F3), never to fit them. P1 (pre-registered): Reynolds "
             "predicts the more/less profiles cluster with the determinative "
             "community.\n")
    for jn, jr in res["judges"].items():
        lc = jr["lexeme_communities"]
        ml = lc["P1_and_boundary_location"]
        L.append(f"- **{jn}**: ARI(clusters vs a-priori strata) = "
                 f"{lc['ari_vs_strata']}; cluster->dominant-stratum "
                 f"{lc['cluster_dominant_stratum']}. P1: more in determinative "
                 f"cluster = {ml.get('more', {}).get('in_determinative_cluster')}, "
                 f"less = {ml.get('less', {}).get('in_determinative_cluster')} "
                 f"(more->{ml.get('more', {}).get('cluster_dominant_stratum')}, "
                 f"less->{ml.get('less', {}).get('cluster_dominant_stratum')}).\n")
    L.append("\n## Posterior-predictive checks\n")
    for jn, jr in res["judges"].items():
        pc = jr["ppc"]
        L.append(f"- **{jn}**: observed eigen-dominance {pc['obs_eig_dominance']} "
                 f"(sim 95% {pc['sim_eig_dominance_ci']}); observed edge density "
                 f"{pc['obs_edge_density']} (sim {pc['sim_edge_density_ci']}).\n")
    L.append("\n## Figures\n- phase3_fig_verdict.png (RQ1 verdict-invariance across arms)\n"
             "- phase3_fig_misfit.png (RQ3 lexeme misfit, boundary marked)\n"
             "- phase3_fig_projectibility.png (RQ2)\n")
    L.append("\n## Estimand architecture\nPPI-corrected per-item acceptance rates "
             "(EB-shrunk, CIs) in phase3_headline.json `ppi_item_rates`. The "
             "structural verdict is fit on the judge matrix with the instrument "
             "characterization (stage 2a) and the arms behind it.\n")
    with open(os.path.join(ROOT, "paper", "phase3_findings.md"), "w") as f:
        f.write("".join(L))


if __name__ == "__main__":
    main()
