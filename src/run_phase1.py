"""Phase 1 driver: MegaAcceptability v2 -> measurement-model comparison.

Implements the pre-registration logged in DECISIONS.md (2026-06-10):
  - primary slice: past tense only, native speakers, participant z-scores,
    cell = mean z across raters, dichotomize z-bar > 0;
  - sensitivity grid (same primary slice unless noted): z-bar > 0.25;
    raw mean >= 4; raw mean >= 4.5; plus an all-tense-pooled arm at z-bar > 0;
  - exclude verbs with any missing cell in the analyzed slice;
  - flag frames with post-dichotomization base rate outside [0.02, 0.98];
  - continuous check: eigen spectrum of the undichotomized z-bar matrix.

Emits structured outputs only (CSV + a factual findings.md), no
interpretation -- that is pm-node work (PLAN.md sections 5-6). Reuses the
golden-tested estimators in models.py; does not modify them.

Run from the repo root:  python src/run_phase1.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import models     # noqa: E402  (golden-tested estimators)
import pipeline   # noqa: E402  (for _versions, run)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "data", "mega-acceptability-v2",
                   "mega-acceptability-v2.tsv")
RESULTS = os.path.join(ROOT, "results")
RUNDIR = os.path.join(RESULTS, "pilot_runs")          # gitignored
SEED = 7
RANK_SWEEP = (1, 2, 3, 4, 5)
GRID_RANK = 1                 # fixed Model-A complexity for verdict invariance


def git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        return "unknown"


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load() -> pd.DataFrame:
    df = pd.read_csv(TSV, sep="\t")
    n_raw = len(df)
    df = df.dropna(subset=["response"]).copy()
    df["response"] = df["response"].astype(float)
    df = df[df["nativeenglish"] == True].copy()        # noqa: E712
    return df, n_raw


def continuous_matrix(df: pd.DataFrame, tenses, normalize: str):
    """verbs x frames continuous cell values (NaN where a cell has no data
    in the slice). normalize: 'z' (participant z-scores then mean) or 'raw'
    (mean response). Returns (pivot_df, n_responses_used, n_dropped_z)."""
    d = df[df["tense"].isin(tenses)].copy()
    n_in = len(d)
    n_dropped = 0
    if normalize == "z":
        g = d.groupby("participant")["response"]
        d["val"] = (d["response"] - g.transform("mean")) / g.transform("std")
        before = len(d)
        d = d.dropna(subset=["val"])      # single-response / constant raters
        n_dropped = before - len(d)
    else:
        d["val"] = d["response"]
    piv = d.pivot_table(index="verb", columns="frame", values="val",
                        aggfunc="mean")
    return piv, n_in, n_dropped


def dichotomize(cont: np.ndarray, rule: tuple) -> np.ndarray:
    kind, thr = rule
    if kind == "z":          # z-bar > thr
        return (cont > thr).astype(int)
    if kind == "raw_ge":     # raw mean >= thr
        return (cont >= thr).astype(int)
    raise ValueError(rule)


def build_arm(df, tenses, normalize, rule):
    piv, n_in, n_dropped = continuous_matrix(df, tenses, normalize)
    n_verbs_full = piv.shape[0]
    complete = piv.dropna(axis=0, how="any")           # pre-reg 6 exclusion
    excluded = n_verbs_full - complete.shape[0]
    cont = complete.values.astype(float)
    X = dichotomize(cont, rule)
    return {
        "X": X, "cont": cont,
        "verbs": list(complete.index), "frames": list(complete.columns),
        "n_verbs": complete.shape[0], "n_verbs_excluded": excluded,
        "n_verbs_in_slice": n_verbs_full,
        "n_frames": complete.shape[1],
        "n_responses_used": n_in, "n_z_dropped": n_dropped,
        "base_rate": float(X.mean()),
    }


def eig_band(dom: float) -> str:
    if dom > 3.0:
        return ">3 (dominant)"
    if dom < 1.5:
        return "<1.5 (no dominance)"
    return "1.5-3 (intermediate)"


def eig_spectrum(M: np.ndarray, k: int = 10):
    r = np.corrcoef(M.T)
    r = np.nan_to_num(r, nan=0.0)
    ev = np.sort(np.linalg.eigvalsh(r))[::-1]
    return ev[:k]


def analyse_arm(arm, rank, label):
    X = arm["X"]
    cv = models.cellwise_cv(X, rank=rank, seed=SEED)
    net = models.fit_network(X)
    diag = models.structure_diagnostics(X, net)
    dom = diag["eig_dominance"]
    diff, se = cv["diff_mean"], cv["diff_se"]
    return {
        "arm": label,
        "n_verbs": arm["n_verbs"], "n_verbs_excluded": arm["n_verbs_excluded"],
        "n_frames": arm["n_frames"], "base_rate": round(arm["base_rate"], 4),
        "rankA": rank,
        "logloss_lowrank": round(cv["logloss_lowrank"], 6),
        "logloss_network": round(cv["logloss_network"], 6),
        "diff_mean": round(diff, 6), "diff_se": round(se, 6),
        "network_better": bool(diff > 0),
        "significant_2se": bool(abs(diff) > 2 * se),
        "eig_dominance": round(dom, 4), "eig_band": eig_band(dom),
        "edge_density": round(diag["edge_density"], 4),
        "top_eigenvalue": round(diag["top_eigenvalue"], 4),
    }


def main():
    os.makedirs(RUNDIR, exist_ok=True)
    df, n_raw = load()
    global_frames = sorted(df["frame"].unique())
    n_verbs_full = df["verb"].nunique()

    arms_spec = [
        ("primary_past_z0",      ["past"],
         "z",   ("z", 0.0)),
        ("sens_past_z025",       ["past"],
         "z",   ("z", 0.25)),
        ("sens_past_raw4",       ["past"],
         "raw", ("raw_ge", 4.0)),
        ("sens_past_raw45",      ["past"],
         "raw", ("raw_ge", 4.5)),
        ("sens_alltense_z0",     ["past", "present", "past_progressive"],
         "z",   ("z", 0.0)),
    ]
    arms = {name: build_arm(df, tenses, norm, rule)
            for (name, tenses, norm, rule) in arms_spec}

    # ---- primary arm: rank sweep + full estimands -----------------------
    primary = arms["primary_past_z0"]
    Xp = primary["X"]
    rank_curve = []
    for r in RANK_SWEEP:
        cv = models.cellwise_cv(Xp, rank=r, seed=SEED)
        rank_curve.append({"rank": r,
                           "logloss_lowrank": round(cv["logloss_lowrank"], 6),
                           "logloss_network": round(cv["logloss_network"], 6),
                           "diff_mean": round(cv["diff_mean"], 6),
                           "diff_se": round(cv["diff_se"], 6)})
    best_rank = min(rank_curve, key=lambda x: x["logloss_lowrank"])["rank"]

    proj = models.projectibility(Xp, seed=SEED)
    net_p = models.fit_network(Xp)
    misfit = models.row_misfit(Xp, net_p)
    spec_dich = eig_spectrum(Xp)
    spec_cont = eig_spectrum(primary["cont"])
    base_rates_frame = Xp.mean(axis=0)
    degenerate = [(primary["frames"][j], round(float(base_rates_frame[j]), 4))
                  for j in range(len(primary["frames"]))
                  if base_rates_frame[j] < 0.02 or base_rates_frame[j] > 0.98]

    # ---- all arms: comparison at fixed GRID_RANK for verdict invariance -
    grid_rows = [analyse_arm(arms[name], GRID_RANK, name)
                 for (name, *_rest) in arms_spec]
    # primary headline also at best CV rank
    headline = analyse_arm(primary, best_rank, "primary_past_z0@bestrank")

    verdict_signs = {r["arm"]: r["network_better"] for r in grid_rows}
    verdict_bands = {r["arm"]: r["eig_band"] for r in grid_rows}
    sign_invariant = len(set(verdict_signs.values())) == 1
    band_invariant = len(set(verdict_bands.values())) == 1

    # ---- write per-arm full runs (gitignored) via pipeline.run ----------
    for name in arms:
        a = arms[name]
        pipeline.run(a["X"], a["verbs"], a["frames"], name, RUNDIR,
                     rank=best_rank, seed=SEED)

    # ---- committed deliverables ----------------------------------------
    # comparison.csv (one row per arm at GRID_RANK + headline best-rank row)
    comp_cols = ["arm", "n_verbs", "n_verbs_excluded", "n_frames",
                 "base_rate", "rankA", "logloss_lowrank", "logloss_network",
                 "diff_mean", "diff_se", "network_better", "significant_2se",
                 "eig_dominance", "eig_band", "edge_density", "top_eigenvalue"]
    with open(os.path.join(RESULTS, "pilot_comparison.csv"), "w") as f:
        f.write(",".join(comp_cols) + "\n")
        for row in grid_rows + [headline]:
            f.write(",".join(str(row[c]) for c in comp_cols) + "\n")

    order = np.argsort(-proj)
    with open(os.path.join(RESULTS, "pilot_projectibility.csv"), "w") as f:
        f.write("frame,projectibility\n")
        for j in order:
            f.write(f"{primary['frames'][j]},{proj[j]:.6f}\n")

    order = np.argsort(-misfit)
    with open(os.path.join(RESULTS, "pilot_misfit.csv"), "w") as f:
        f.write("verb,misfit\n")
        for i in order:
            f.write(f"{primary['verbs'][i]},{misfit[i]:.6f}\n")

    manifest = {
        "phase": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": "MegaAcceptability v2 (megaattitude.io)",
        "dataset_file": os.path.relpath(TSV, ROOT),
        "dataset_sha256": file_sha256(TSV),
        "n_judgments_raw": int(n_raw),
        "n_judgments_native_nonNA": int(len(df)),
        "seed": SEED, "grid_rank": GRID_RANK, "best_rank_primary": best_rank,
        "git_rev": git_rev(), "versions": pipeline._versions(),
        "n_verbs_full_dataset": int(n_verbs_full),
        "n_frames_full_dataset": len(global_frames),
        "arms": {name: {"slice": spec[1], "normalize": spec[2],
                        "rule": list(spec[3]),
                        "n_verbs": arms[name]["n_verbs"],
                        "n_verbs_in_slice": arms[name]["n_verbs_in_slice"],
                        "n_verbs_excluded": arms[name]["n_verbs_excluded"],
                        "n_frames": arms[name]["n_frames"],
                        "frames_absent": sorted(set(global_frames) -
                                                set(arms[name]["frames"])),
                        "base_rate": round(arms[name]["base_rate"], 4)}
                 for name, spec in zip(arms, arms_spec)},
        "verdict_sign_invariant": sign_invariant,
        "verdict_band_invariant": band_invariant,
    }
    with open(os.path.join(RESULTS, "pilot_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    write_findings(manifest, grid_rows, headline, rank_curve, best_rank,
                   spec_dich, spec_cont, proj, misfit, primary, degenerate,
                   sign_invariant, band_invariant)
    print("Phase 1 complete. best_rank=%d sign_invariant=%s band_invariant=%s"
          % (best_rank, sign_invariant, band_invariant))


def write_findings(manifest, grid_rows, headline, rank_curve, best_rank,
                   spec_dich, spec_cont, proj, misfit, primary, degenerate,
                   sign_invariant, band_invariant):
    L = []
    w = L.append
    w("# Phase 1 findings -- MegaAcceptability v2 reanalysis\n")
    w("Structured outputs only; interpretation and the PLAN.md §4 "
      "go/no-go call are pm-node work (Phase 2). All numbers trace to "
      "`results/pilot_*` and `results/pilot_runs/` under the manifest below.\n")
    w("## Provenance\n")
    w(f"- Dataset: {manifest['dataset']}, file `{manifest['dataset_file']}`")
    w(f"- SHA-256: `{manifest['dataset_sha256']}`")
    w(f"- Judgments: {manifest['n_judgments_raw']:,} raw; "
      f"{manifest['n_judgments_native_nonNA']:,} after dropping 10 NA and "
      f"non-native raters (native filter effect is negligible: see DECISIONS).")
    w(f"- Seed {manifest['seed']}; git `{manifest['git_rev'][:10]}`; "
      f"versions {manifest['versions']}.")
    w(f"- Pre-registration: DECISIONS.md 2026-06-10. Primary slice = past "
      f"tense, native, participant z-scores, cell = mean z, dichotomize "
      f"z-bar > 0.\n")

    w("## Slice composition\n")
    w(f"- Full dataset (native, non-NA): {manifest['n_verbs_full_dataset']} "
      f"verbs, {manifest['n_frames_full_dataset']} frames.")
    for name, a in manifest["arms"].items():
        absent = a["frames_absent"]
        lost = manifest["n_verbs_full_dataset"] - a["n_verbs_in_slice"]
        line = (f"- {name}: {a['n_verbs']} verbs x {a['n_frames']} frames "
                f"(slice contained {a['n_verbs_in_slice']} verbs; "
                f"{a['n_verbs_excluded']} excluded for partial missing cells; "
                f"{lost} absent from slice entirely).")
        if absent:
            line += f" Frames absent from this slice: {absent}."
        w(line)
    w("")

    w("## Model comparison by arm (Model A low-rank vs Model B network)\n")
    w("`diff_mean` > 0 means the network predicts held-out cells better; "
      f"`network_better` is its sign. Grid arms use fixed rank "
      f"{manifest['grid_rank']} for a like-for-like verdict; the final row is "
      f"the primary arm at its best CV rank ({best_rank}).\n")
    cols = ["arm", "n_verbs", "base_rate", "rankA", "logloss_lowrank",
            "logloss_network", "diff_mean", "diff_se", "network_better",
            "significant_2se", "eig_dominance", "eig_band", "edge_density"]
    w("| " + " | ".join(cols) + " |")
    w("|" + "|".join(["---"] * len(cols)) + "|")
    for row in grid_rows + [headline]:
        w("| " + " | ".join(str(row[c]) for c in cols) + " |")
    w("")
    w(f"- Pre-registered robustness criterion (DECISIONS 4): verdict sign "
      f"invariant across grid = **{sign_invariant}**; eigen-dominance band "
      f"invariant = **{band_invariant}**. If either is False, "
      f"threshold-dependence is itself the result (no arm promoted).")
    w(f"- Excluded verbs (any missing cell in slice) per arm: " +
      ", ".join(f"{r['arm']}={r['n_verbs_excluded']}" for r in grid_rows) +
      ".\n")

    w("## Model A rank sweep (primary arm)\n")
    w("Residual structure check: does held-out prediction improve past one "
      "latent dimension? (Calibration note, DECISIONS 2026-06-10.)\n")
    w("| rank | logloss_lowrank | logloss_network | diff_mean | diff_se |")
    w("|---|---|---|---|---|")
    for rc in rank_curve:
        w(f"| {rc['rank']} | {rc['logloss_lowrank']} | "
          f"{rc['logloss_network']} | {rc['diff_mean']} | {rc['diff_se']} |")
    w("")

    w("## Eigenvalue spectra (primary arm)\n")
    w("Pre-reg 5 continuous check + residual-structure spectrum. First 10 "
      "eigenvalues of the cell correlation matrix.\n")
    w("- Undichotomized z-bar matrix: " +
      ", ".join(f"{v:.3f}" for v in spec_cont))
    w("- Dichotomized 0/1 matrix:    " +
      ", ".join(f"{v:.3f}" for v in spec_dich) + "\n")

    w("## Projectibility (primary arm)\n")
    n_pos = int((proj > 0.01).sum())
    w(f"- Frames with projectibility > 0.01: {n_pos} of {len(proj)} "
      f"(PLAN §4 T2 reference is ≥ 10; formal significance/bootstrap "
      f"deferred to pm-node). Full ranking: `results/pilot_projectibility.csv`.")
    top = np.argsort(-proj)[:8]
    bot = np.argsort(proj)[:5]
    w("- Top frames: " +
      "; ".join(f"{primary['frames'][j]} ({proj[j]:.3f})" for j in top))
    w("- Bottom frames: " +
      "; ".join(f"{primary['frames'][j]} ({proj[j]:.3f})" for j in bot) + "\n")

    w("## Per-verb misfit (primary arm)\n")
    w("Standardized network misfit; full ranking in `results/pilot_misfit.csv`.")
    top = np.argsort(-misfit)[:15]
    w("- Highest-misfit verbs: " +
      "; ".join(f"{primary['verbs'][i]} ({misfit[i]:.2f})" for i in top) + "\n")

    w("## Frame flags\n")
    if degenerate:
        w("Frames with post-dichotomization base rate outside [0.02, 0.98] "
          "(kept, flagged; pre-reg 6):")
        for fr, br in degenerate:
            w(f"- {fr}: base rate {br}")
    else:
        w("No frame has a primary-arm base rate outside [0.02, 0.98].")
    w("")

    with open(os.path.join(RESULTS, "pilot_findings.md"), "w") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
