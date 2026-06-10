"""Recovery tests backing GOLDEN.md.

The whole Phase 1 inference rests on these: if the machinery can't tell
planted-reflective from planted-network data at realistic n and p, no
conclusion about real data is licensed (PLAN.md T3).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import models  # noqa: E402
import synth   # noqa: E402

SEED = 7


def test_reflective_signature():
    d = synth.reflective(n=800, p=30, rank=1, seed=SEED)
    net = models.fit_network(d["X"])
    diag = models.structure_diagnostics(d["X"], net)
    # one latent dimension -> first eigenvalue dominates hard
    assert diag["eig_dominance"] > 3.0, diag
    cv = models.cellwise_cv(d["X"], rank=1, seed=SEED)
    # low-rank model should not lose badly on its home turf:
    # diff_mean > 0 means network better; demand it isn't decisively so
    assert cv["diff_mean"] < 2 * cv["diff_se"], cv


def test_network_signature():
    d = synth.network(n=800, p=30, edge_prob=0.12, seed=SEED)
    net = models.fit_network(d["X"])
    diag = models.structure_diagnostics(d["X"], net,
                                        true_graph=d["true_graph"])
    # no common cause -> no dominant first eigenvalue
    assert diag["eig_dominance"] < 3.0, diag
    # sparse graph recovered reasonably
    assert diag["edge_f1"] > 0.55, diag
    cv = models.cellwise_cv(d["X"], rank=1, seed=SEED)
    # rank-1 reflective model should lose decisively here
    assert cv["diff_mean"] > 2 * cv["diff_se"], cv


def test_projectibility_orders_items():
    d = synth.reflective(n=600, p=20, rank=1, seed=SEED)
    proj = models.projectibility(d["X"], seed=SEED)
    assert proj.max() > 0.01, "no item projects anything"
    # add a pure-noise item; it must rank near the bottom
    rng = np.random.default_rng(SEED)
    noise = rng.integers(0, 2, size=(d["X"].shape[0], 1))
    x2 = np.hstack([d["X"], noise])
    proj2 = models.projectibility(x2, seed=SEED)
    assert np.argsort(proj2)[0] == x2.shape[1] - 1 or \
        proj2[-1] < np.median(proj2), proj2


def test_misfit_flags_planted_outliers():
    # Power note (feeds PLAN.md section 4/T3): with p~24 items, partial
    # scrambles (~6 contradictory cells) give planted-vs-null z of about
    # 0.6 vs -0.2 -- separated in expectation but weak for individual
    # detection. Full-profile scrambles are reliably detected. Hence the
    # Phase 3 battery floor of ~40 items per lexeme.
    d = synth.reflective(n=600, p=24, rank=1, seed=SEED)
    x = d["X"].copy()
    rng = np.random.default_rng(SEED)
    planted = rng.choice(x.shape[0], size=12, replace=False)
    for i in planted:                      # full-profile scramble
        x[i] = rng.integers(0, 2, size=x.shape[1])
    misfit = models.row_misfit_lowrank(x, rank=1, seed=SEED)
    top = set(np.argsort(-misfit)[:60])
    hits = len(top & set(planted))
    assert hits >= 9, f"only {hits}/12 planted outliers in top decile"
