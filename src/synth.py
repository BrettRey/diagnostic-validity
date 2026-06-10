"""Synthetic lexeme x diagnostic matrices with planted structure.

Two generators:
  - reflective(): low-rank latent-trait (2PL-style) data. One (or few)
    latent dimensions cause all items. Statistical signature of an
    essence/reflective construct.
  - network(): sparse pairwise (Ising) data via Gibbs sampling. Items
    mutually constrain each other with no common cause. Statistical
    signature of a maintained cluster.

Used by tests/ to establish that src/models.py discriminates the two
regimes at realistic n, p, and base rates. Golden numbers in GOLDEN.md.
"""
from __future__ import annotations

import numpy as np


def reflective(n: int = 800, p: int = 30, rank: int = 1,
               discrimination: float = 2.0, seed: int = 0) -> dict:
    """Low-rank latent-trait binary data (2PL-style).

    P(x_ij = 1) = sigmoid(a_j . theta_i + b_j)
    """
    rng = np.random.default_rng(seed)
    theta = rng.normal(size=(n, rank))
    a = rng.normal(loc=discrimination, scale=0.4, size=(p, rank))
    a *= rng.choice([1.0, 1.0, 1.0, -1.0], size=(p, rank))  # mostly aligned
    b = rng.normal(scale=0.8, size=p)
    logits = theta @ a.T + b
    x = (rng.random((n, p)) < 1.0 / (1.0 + np.exp(-logits))).astype(int)
    return {"X": x, "kind": "reflective", "rank": rank,
            "true_graph": None}


def network(n: int = 800, p: int = 30, edge_prob: float = 0.12,
            coupling: float = 1.4, n_gibbs: int = 400, seed: int = 0) -> dict:
    """Sparse Ising data via Gibbs sampling.

    Symmetric weight matrix W with ~edge_prob density, couplings of
    magnitude ~coupling (mixed sign, mostly positive), thresholds ~0.
    """
    rng = np.random.default_rng(seed)
    w = np.zeros((p, p))
    iu = np.triu_indices(p, k=1)
    mask = rng.random(len(iu[0])) < edge_prob
    signs = rng.choice([1.0, 1.0, 1.0, -1.0], size=mask.sum())
    vals = rng.normal(loc=coupling, scale=0.25, size=mask.sum()) * signs
    w[iu[0][mask], iu[1][mask]] = vals
    w = w + w.T
    # centre thresholds so activation hovers near 0.5 instead of saturating
    b = -w.sum(axis=1) / 2.0 + rng.normal(scale=0.3, size=p)

    x = rng.integers(0, 2, size=(n, p)).astype(float)
    for _ in range(n_gibbs):
        j = rng.integers(0, p)
        logits = x @ w[:, j] + b[j]
        x[:, j] = (rng.random(n) < 1.0 / (1.0 + np.exp(-logits))).astype(float)
    # finish with a full sweep per node for better mixing
    for j in range(p):
        logits = x @ w[:, j] + b[j]
        x[:, j] = (rng.random(n) < 1.0 / (1.0 + np.exp(-logits))).astype(float)
    return {"X": x.astype(int), "kind": "network",
            "true_graph": (np.abs(w) > 1e-9).astype(int)}
