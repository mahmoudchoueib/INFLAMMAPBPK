"""Bounded WLS/likelihood and true nuisance-reoptimised profiles. No automatic physiology fit."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares, minimize


@dataclass
class Estimate:
    parameters: np.ndarray
    objective: float
    success: bool
    message: str
    residuals: np.ndarray
    jacobian: np.ndarray
    evaluations: int


def _vectors(y, sigma):
    y = np.asarray(y, dtype=float)
    sigma = np.broadcast_to(np.asarray(sigma, dtype=float), y.shape)
    if y.ndim != 1 or not len(y) or not np.isfinite(y).all():
        raise ValueError("Finite nonempty observation vector required")
    if not np.isfinite(sigma).all() or (sigma <= 0).any():
        raise ValueError("Positive finite observation uncertainties required")
    return y, sigma


def weighted_fit(predict, y, sigma, initial, bounds, *, log_error=False, max_nfev=300):
    y, sigma = _vectors(y, sigma)
    if log_error and (y <= 0).any():
        raise ValueError(
            "Positive concentrations needed for log error; use a censored likelihood for BLQ"
        )

    def residual(theta):
        prediction = np.asarray(predict(theta))
        if prediction.shape != y.shape or not np.isfinite(prediction).all():
            raise ValueError("Invalid forward prediction")
        if log_error:
            if (prediction <= 0).any():
                raise ValueError("Nonpositive log prediction")
            return (np.log(prediction) - np.log(y)) / sigma
        return (prediction - y) / sigma

    result = least_squares(
        residual, initial, bounds=bounds, max_nfev=max_nfev, ftol=1e-10, xtol=1e-10, gtol=1e-10
    )
    return Estimate(
        result.x,
        float(np.dot(result.fun, result.fun)),
        bool(result.success),
        result.message,
        result.fun,
        result.jac,
        int(result.nfev),
    )


def lognormal_nll(prediction, y, sigma):
    y, sigma = _vectors(y, sigma)
    p = np.asarray(prediction, dtype=float)
    if p.shape != y.shape or not np.isfinite(p).all() or (p <= 0).any() or (y <= 0).any():
        raise ValueError("Lognormal likelihood requires positive finite observations/predictions")
    r = (np.log(y) - np.log(p)) / sigma
    return float(np.sum(0.5 * r * r + np.log(sigma) + np.log(y) + 0.5 * np.log(2 * np.pi)))


def maximum_likelihood(objective, initial, bounds):
    return minimize(
        objective,
        initial,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-7},
    )


def profile_likelihood(objective, optimum, bounds, index, grid):
    """Fix one parameter, reoptimise all others at every grid value, multiple starts."""
    optimum = np.asarray(optimum, dtype=float)
    free = [i for i in range(len(optimum)) if i != index]
    rows = []
    for value in grid:
        if not bounds[index][0] <= value <= bounds[index][1]:
            raise ValueError("Profile point outside parameter bounds")

        def combine(v):
            theta = optimum.copy()
            theta[index] = value
            theta[free] = v
            return theta

        if not free:
            value_nll = float(objective(combine([])))
            rows.append(
                {
                    "fixed": float(value),
                    "nll": value_nll,
                    "success": bool(np.isfinite(value_nll)),
                    "parameters": combine([]).tolist(),
                }
            )
            continue
        starts = [optimum[free], np.array([(bounds[i][0] + bounds[i][1]) / 2 for i in free])]
        results = [
            maximum_likelihood(lambda x: objective(combine(x)), s, [bounds[i] for i in free])
            for s in starts
        ]
        good = [r for r in results if r.success and np.isfinite(r.fun)]
        if not good:
            rows.append({"fixed": float(value), "nll": None, "success": False})
            continue
        best = min(good, key=lambda r: r.fun)
        rows.append(
            {
                "fixed": float(value),
                "nll": float(best.fun),
                "success": True,
                "parameters": combine(best.x).tolist(),
            }
        )
    return rows


def sensitivity_matrix(predict, theta, step=1e-3):
    """Central finite differences in caller-specified coordinates; caller labels scaling."""
    theta = np.asarray(theta, dtype=float)
    columns = []
    for j in range(len(theta)):
        delta = np.zeros(len(theta))
        delta[j] = step
        columns.append(
            (np.asarray(predict(theta + delta)) - np.asarray(predict(theta - delta))) / (2 * step)
        )
    return np.column_stack(columns)


def rank_diagnostics(matrix, relative_tolerance=1e-6):
    j = np.asarray(matrix, dtype=float)
    if j.ndim != 2 or not np.isfinite(j).all():
        raise ValueError("Finite sensitivity matrix needed")
    _, s, vt = np.linalg.svd(j, full_matrices=False)
    rank = int(np.sum(s > relative_tolerance * s[0])) if s.size and s[0] > 0 else 0
    corr = None
    if rank == j.shape[1]:
        covariance = np.linalg.inv(j.T @ j)
        scale = np.sqrt(np.diag(covariance))
        corr = (covariance / np.outer(scale, scale)).tolist()
    return {
        "singular_values": s.tolist(),
        "rank": rank,
        "columns": j.shape[1],
        "relative_tolerance": relative_tolerance,
        "local_parameter_correlation": corr,
        "weakest_direction": vt[-1].tolist() if len(vt) else [],
    }


def aicc(nll, k, n):
    return float(2 * nll + 2 * k + 2 * k * (k + 1) / (n - k - 1)) if n > k + 1 else None
