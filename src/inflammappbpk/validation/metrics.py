"""Predefined positive-concentration metrics and paired cluster bootstrap."""

import numpy as np


def performance(observed, predicted):
    y, p = np.asarray(observed, float), np.asarray(predicted, float)
    if y.shape != p.shape or not y.size or not np.isfinite(y).all() or not np.isfinite(p).all():
        raise ValueError("Aligned finite nonempty observations required")
    if (y <= 0).any() or (p <= 0).any():
        raise ValueError("Positive values required; BLQ needs censoring")
    d = np.log(p) - np.log(y)
    return {
        "n": int(y.size),
        "mae_log": float(np.mean(abs(d))),
        "rmse_log": float(np.sqrt(np.mean(d * d))),
        "geometric_bias": float(np.exp(np.mean(d))),
        "mean_absolute_fold_error": float(np.exp(np.mean(abs(d)))),
    }


def paired_improvement(observed, reference, candidate, clusters, *, seed=42, draws=2000):
    arrays = [np.asarray(v) for v in [observed, reference, candidate, clusters]]
    y, a, b, g = arrays
    performance(y, a)
    performance(y, b)
    if g.shape != y.shape:
        raise ValueError("Cluster IDs must align")
    ids = np.unique(g)
    difference = abs(np.log(a / y)) - abs(np.log(b / y))
    means = np.array([difference[g == key].mean() for key in ids])
    if len(ids) < 2:
        return {
            "mean_log_error_improvement": float(means.mean()),
            "ci95": None,
            "independent_clusters": len(ids),
            "reason": "Fewer than two independent clusters",
        }
    rng = np.random.default_rng(seed)
    bootstrap = rng.choice(means, size=(draws, len(ids)), replace=True).mean(axis=1)
    return {
        "mean_log_error_improvement": float(means.mean()),
        "ci95": np.quantile(bootstrap, [0.025, 0.975]).tolist(),
        "independent_clusters": len(ids),
        "estimand": "equal-cluster-weight paired log MAE reduction",
    }
