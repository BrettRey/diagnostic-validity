"""Measurement models and comparison machinery.

Model A (reflective): rank-r logistic matrix factorization,
    logit P(X) = U V' + 1 b', fit by masked gradient descent.
Model B (network): node-wise l1-penalized logistic regression
    (eLasso-style pseudo-likelihood), symmetrized by AND-rule.

Comparison is three-pronged (PLAN.md section 2):
  1. cell-wise cross-validated log-loss,
  2. effective parameter counts,
  3. structure diagnostics: eigenvalue dominance of the association
     matrix, estimated edge density, and (when truth is known in
     synthetic tests) edge-recovery F1.

Also: projectibility scores per item and per-row misfit.
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _logloss(y, p, eps=1e-9):
    p = np.clip(p, eps, 1 - eps)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


# ----------------------------------------------------------------- Model A
def fit_lowrank(X: np.ndarray, rank: int = 1, mask: np.ndarray | None = None,
                l2: float = 1e-2, lr: float = 0.05, n_iter: int = 600,
                seed: int = 0) -> dict:
    """Masked rank-r logistic factorization. mask: 1 = observed."""
    rng = np.random.default_rng(seed)
    n, p = X.shape
    m = np.ones_like(X, dtype=float) if mask is None else mask.astype(float)
    u = rng.normal(scale=0.1, size=(n, rank))
    v = rng.normal(scale=0.1, size=(p, rank))
    b = np.zeros(p)
    for _ in range(n_iter):
        z = u @ v.T + b
        g = (_sigmoid(z) - X) * m            # n x p
        gu = g @ v / p + l2 * u
        gv = g.T @ u / n + l2 * v
        gb = g.mean(axis=0)
        u -= lr * gu
        v -= lr * gv
        b -= lr * gb
    return {"U": u, "V": v, "b": b, "rank": rank,
            "n_params": rank * (n + p) + p}


def predict_lowrank(model: dict) -> np.ndarray:
    return _sigmoid(model["U"] @ model["V"].T + model["b"])


# ----------------------------------------------------------------- Model B
C_GRID = (0.05, 0.1, 0.2, 0.4)


def _l1_logistic(C: float) -> LogisticRegression:
    return LogisticRegression(penalty="l1", C=C, solver="liblinear",
                              max_iter=2000)


def fit_network(X: np.ndarray, C: float | None = None) -> dict:
    """Node-wise l1 logistic (eLasso-style). Per-node penalty chosen by
    BIC over C_GRID unless C is given. Symmetrized weights."""
    n, p = X.shape
    w = np.zeros((p, p))
    b = np.zeros(p)
    grid = (C,) if C is not None else C_GRID
    for j in range(p):
        idx = [k for k in range(p) if k != j]
        y = X[:, j]
        if y.min() == y.max():            # degenerate column
            b[j] = 20.0 if y.min() == 1 else -20.0
            continue
        best = None
        for c in grid:
            clf = _l1_logistic(c).fit(X[:, idx], y)
            pr = np.clip(clf.predict_proba(X[:, idx])[:, 1], 1e-9, 1 - 1e-9)
            ll = float((y * np.log(pr) + (1 - y) * np.log(1 - pr)).sum())
            k = int((np.abs(clf.coef_[0]) > 1e-8).sum()) + 1
            bic = -2 * ll + k * np.log(n)
            if best is None or bic < best[0]:
                best = (bic, clf)
        clf = best[1]
        w[j, idx] = clf.coef_[0]
        b[j] = clf.intercept_[0]
    w_sym = np.where(np.abs(w) < np.abs(w.T), w, w.T)   # AND-ish rule
    w_sym = (w_sym + w_sym.T) / 2.0
    np.fill_diagonal(w_sym, 0.0)
    n_edges = int((np.abs(np.triu(w_sym, 1)) > 1e-8).sum())
    return {"W": w_sym, "b": b, "n_params": n_edges + p,
            "edge_density": n_edges / (p * (p - 1) / 2)}


def predict_network_cell(model: dict, x_row: np.ndarray, j: int) -> float:
    z = float(np.delete(x_row, j) @ np.delete(model["W"][j], j) + model["b"][j])
    return float(_sigmoid(z))


# ------------------------------------------------------------- comparison
def cellwise_cv(X: np.ndarray, rank: int = 1, n_folds: int = 5,
                cells_per_row: int = 3, C: float = 0.3,
                seed: int = 0) -> dict:
    """Hold out `cells_per_row` random cells per row per fold; compare
    held-out log-loss of Model A (masked fit) and Model B (node-wise fit
    on rows with the target cell observed; held-out predictors imputed
    with column means -- documented scaffold limitation)."""
    rng = np.random.default_rng(seed)
    n, p = X.shape
    col_mean = X.mean(axis=0)
    ll_a, ll_b = [], []
    for fold in range(n_folds):
        mask = np.ones((n, p))
        held = []
        for i in range(n):
            js = rng.choice(p, size=cells_per_row, replace=False)
            mask[i, js] = 0.0
            held.extend((i, j) for j in js)
        # Model A on masked data
        ma = fit_lowrank(X * mask, rank=rank, mask=mask, seed=fold)
        pa = predict_lowrank(ma)
        # Model B on rows as-is but trained per node excluding rows where
        # the node itself is held out
        mb_models = {}
        for j in range(p):
            rows = mask[:, j] == 1.0
            y = X[rows, j]
            idx = [k for k in range(p) if k != j]
            xr = X[np.ix_(rows, idx)].astype(float)
            # impute predictors held out in those rows
            mr = mask[np.ix_(rows, idx)]
            xr = xr * mr + col_mean[idx] * (1 - mr)
            if y.min() == y.max():
                mb_models[j] = ("const", float(y.min()))
                continue
            clf = _l1_logistic(C).fit(xr, y)
            mb_models[j] = ("clf", clf, idx)
        for (i, j) in held:
            ll_a.append(_logloss(X[i, j], pa[i, j]))
            mj = mb_models[j]
            if mj[0] == "const":
                pb = 0.999 if mj[1] == 1 else 0.001
            else:
                _, clf, idx = mj
                xr = X[i, idx].astype(float)
                mr = mask[i, idx]
                xr = xr * mr + col_mean[idx] * (1 - mr)
                pb = clf.predict_proba(xr.reshape(1, -1))[0, 1]
            ll_b.append(_logloss(X[i, j], pb))
    ll_a, ll_b = np.array(ll_a), np.array(ll_b)
    d = ll_a - ll_b                       # >0 means network better
    return {"logloss_lowrank": float(ll_a.mean()),
            "logloss_network": float(ll_b.mean()),
            "diff_mean": float(d.mean()),
            "diff_se": float(d.std(ddof=1) / np.sqrt(len(d)))}


def structure_diagnostics(X: np.ndarray, net: dict,
                          true_graph: np.ndarray | None = None) -> dict:
    """Eigen dominance of the (Pearson, phi) correlation matrix; edge
    density; optional edge-recovery F1 against a known graph."""
    r = np.corrcoef(X.T)
    r = np.nan_to_num(r, nan=0.0)
    ev = np.sort(np.linalg.eigvalsh(r))[::-1]
    out = {"eig_dominance": float(ev[0] / max(ev[1], 1e-9)),
           "top_eigenvalue": float(ev[0]),
           "edge_density": net["edge_density"]}
    if true_graph is not None:
        est = (np.abs(np.triu(net["W"], 1)) > 1e-8).astype(int)
        tru = np.triu(true_graph, 1)
        tp = int((est & tru).sum())
        fp = int((est & (1 - tru)).sum())
        fn = int(((1 - est) & tru).sum())
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        out["edge_f1"] = float(2 * prec * rec / max(prec + rec, 1e-9))
    return out


# ------------------------------------------------- item-level quantities
def projectibility(X: np.ndarray, C: float = 0.3, seed: int = 0,
                   test_frac: float = 0.3) -> np.ndarray:
    """Per-item projectibility: mean held-out log-loss improvement, over
    all other items, from observing this item (vs marginal baseline).
    Crude but estimand-faithful: what does knowing this diagnostic let
    you predict?"""
    rng = np.random.default_rng(seed)
    n, p = X.shape
    test = rng.random(n) < test_frac
    train = ~test
    base = X[train].mean(axis=0)
    scores = np.zeros(p)
    for j in range(p):
        gains = []
        for k in range(p):
            if k == j:
                continue
            y_tr, y_te = X[train, k], X[test, k]
            if y_tr.min() == y_tr.max():
                continue
            clf = LogisticRegression(max_iter=1000)
            clf.fit(X[train, j].reshape(-1, 1), y_tr)
            p1 = clf.predict_proba(X[test, j].reshape(-1, 1))[:, 1]
            gain = _logloss(y_te, np.full_like(p1, base[k])).mean() \
                - _logloss(y_te, p1).mean()
            gains.append(gain)
        scores[j] = float(np.mean(gains)) if gains else 0.0
    return scores


def _personfit_z(X: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Standardized person-fit z per row given predicted prob matrix P."""
    pr = np.clip(P, 1e-6, 1 - 1e-6)
    ll = np.where(X == 1, -np.log(pr), -np.log(1 - pr))
    h = -(pr * np.log(pr) + (1 - pr) * np.log(1 - pr))
    e2 = pr * np.log(pr) ** 2 + (1 - pr) * np.log(1 - pr) ** 2
    var = np.maximum(e2 - h ** 2, 1e-12)
    return (ll - h).sum(axis=1) / np.sqrt(var.sum(axis=1))


def row_misfit_lowrank(X: np.ndarray, rank: int = 1, seed: int = 0) -> np.ndarray:
    """Person-fit z under the rank-r reflective model. The rank
    constraint can't bend around a self-contradictory profile, so
    scrambled/boundary rows surface here even when conditional (network)
    predictions adapt to them. Report alongside row_misfit; PLAN.md RQ3
    uses the winning model's statistic but both are computed."""
    m = fit_lowrank(X, rank=rank, seed=seed)
    return _personfit_z(X, predict_lowrank(m))


def row_misfit(X: np.ndarray, net: dict) -> np.ndarray:
    """Per-row (lexeme) standardized misfit, person-fit style.

    For each cell, the model predicts p; the observed log-loss has known
    expectation (the entropy H(p)) and variance under the model. The row
    statistic is z = sum(ll - H) / sqrt(sum var): how much less
    predictable this profile is than the model says it should be. This
    deconfounds 'atypical' from merely 'intermediate' profiles (raw
    log-loss ranks high-entropy rows first, which is wrong for boundary
    detection)."""
    n, p = X.shape
    out = np.zeros(n)
    for i in range(n):
        num, var = 0.0, 0.0
        for j in range(p):
            pr = np.clip(predict_network_cell(net, X[i], j), 1e-6, 1 - 1e-6)
            ll = -np.log(pr) if X[i, j] == 1 else -np.log(1 - pr)
            h = -(pr * np.log(pr) + (1 - pr) * np.log(1 - pr))
            e2 = pr * np.log(pr) ** 2 + (1 - pr) * np.log(1 - pr) ** 2
            num += ll - h
            var += max(e2 - h ** 2, 1e-12)
        out[i] = num / np.sqrt(var)
    return out
