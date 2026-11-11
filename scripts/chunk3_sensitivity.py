"""Bounded, reproducible sensitivity/identifiability experiments on an illustrative model."""

import ast
import hashlib
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sympy as sp
from SALib.analyze import morris as morris_analyze
from SALib.analyze import sobol as sobol_analyze
from SALib.sample import morris as morris_sample
from SALib.sample import sobol as sobol_sample

from inflammappbpk.inference.estimation import rank_diagnostics
from inflammappbpk.inference.sensitivity import METRICS, PARAMETERS, priority_worker, whole_forward

ROOT = Path(__file__).resolve().parents[1]


def atomic_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, sort_keys=True))
    temporary.replace(path)


def sensitivity():
    out = ROOT / "results/sensitivity"
    out.mkdir(exist_ok=True)
    ident = ROOT / "results/identifiability"
    ident.mkdir(exist_ok=True)
    problem = {
        "num_vars": 3,
        "names": PARAMETERS[:3],
        "bounds": np.log([[0.5, 2.0], [0.5, 4.0], [0.25, 4.0]]).tolist(),
    }
    # N=16 subset provides a stated convergence check; first-order and total effects only.
    sobol = sobol_sample.sample(problem, 128, calc_second_order=False, seed=922)
    lower = sobol_sample.sample(problem, 64, calc_second_order=False, seed=922)
    morris = morris_sample.sample(problem, 8, num_levels=4, seed=811)
    all_points = {tuple(p) for p in np.vstack([sobol, lower, morris])}
    cache = out / "forward_cache.json"
    files = sorted(
        [
            *(ROOT / "src/inflammappbpk/simulation").glob("*.py"),
            *(ROOT / "src/inflammappbpk/physiology").glob("*.py"),
            *(ROOT / "src/inflammappbpk/transport").glob("*.py"),
            *(ROOT / "src/inflammappbpk/fcrn").glob("*.py"),
            *(ROOT / "src/inflammappbpk/tmdd").glob("*.py"),
            ROOT / "src/inflammappbpk/inference/sensitivity.py",
        ]
    )
    identity = {
        str(p.relative_to(ROOT)): hashlib.sha256(
            ast.dump(ast.parse(p.read_text()), include_attributes=False).encode()
        ).hexdigest()
        for p in files
    }
    identity["_runtime"] = (
        f"{platform.python_version()} numpy={np.__version__} scipy={scipy.__version__}"
    )
    identity_path = out / "cache_identity.json"
    valid = identity_path.exists() and json.loads(identity_path.read_text()) == identity
    existing = json.loads(cache.read_text()) if cache.exists() and valid else []
    if not valid:
        atomic_json(cache, [])
    atomic_json(identity_path, identity)
    results = {tuple(r["theta"][:3]): r for r in existing}
    pending = sorted(all_points - set(results))
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i, result in enumerate(pool.map(priority_worker, pending, chunksize=1)):
            results[tuple(result["theta"][:3])] = result
            if i % 25 == 0:
                atomic_json(cache, list(results.values()))
                print(f"sensitivity: {i + 1}/{len(pending)} forward evaluations", flush=True)
    atomic_json(cache, list(results.values()))

    def values(points):
        return np.array([results[tuple(p)]["metrics"] for p in points])

    ys, yl, ym = values(sobol), values(lower), values(morris)
    rankings = []
    screening = []
    convergence = []
    for j, metric in enumerate(METRICS):
        s = sobol_analyze.analyze(problem, ys[:, j], calc_second_order=False, seed=41)
        small = sobol_analyze.analyze(problem, yl[:, j], calc_second_order=False, seed=41)
        m = morris_analyze.analyze(problem, morris, ym[:, j], num_levels=4, seed=41)
        for k, name in enumerate(problem["names"]):
            rankings.append(
                dict(
                    metric=metric,
                    parameter=name,
                    S1=s["S1"][k],
                    ST=s["ST"][k],
                    S1_conf=s["S1_conf"][k],
                    ST_conf=s["ST_conf"][k],
                    N=128,
                    scope="hypothetical ranges, exploratory low-N estimate",
                )
            )
            screening.append(
                dict(
                    metric=metric,
                    parameter=name,
                    mu_star=m["mu_star"][k],
                    sigma=m["sigma"][k],
                    trajectories=8,
                )
            )
            convergence.append(
                dict(
                    metric=metric,
                    parameter=name,
                    ST_N64=small["ST"][k],
                    ST_N128=s["ST"][k],
                    absolute_change=abs(s["ST"][k] - small["ST"][k]),
                )
            )
    pd.DataFrame(rankings).to_csv(out / "sobol_rankings.csv", index=False)
    pd.DataFrame(screening).to_csv(out / "morris_screening.csv", index=False)
    pd.DataFrame(convergence).to_csv(out / "sobol_convergence.csv", index=False)
    local = []
    plasma_columns = []
    joint_columns = []
    h = 0.01
    for k, name in enumerate(PARAMETERS):
        delta = np.zeros(5)
        delta[k] = h
        plus = whole_forward(delta)
        minus = whole_forward(-delta)
        elasticity = (np.log(plus["metrics"]) - np.log(minus["metrics"])) / (2 * h)
        for metric, value in zip(METRICS, elasticity):
            local.append(dict(metric=metric, parameter=name, log_elasticity=value))
        plasma_columns.append((np.log(plus["plasma"]) - np.log(minus["plasma"])) / (2 * h))
        joint_columns.append(
            (np.log(plus["plasma"] + plus["colon"]) - np.log(minus["plasma"] + minus["colon"]))
            / (2 * h)
        )
    pd.DataFrame(local).to_csv(out / "local_elasticities.csv", index=False)
    # These are design/sensitivity diagnostics; NOT identifiability estimates from real human data.
    diag = {
        "classification": "hypothetical design-level log sensitivities",
        "parameters": PARAMETERS,
        "coordinate_scaling": "log parameters versus log concentrations",
        "plasma_only": rank_diagnostics(np.column_stack(plasma_columns), 1e-3),
        "plasma_plus_free_colon": rank_diagnostics(np.column_stack(joint_columns), 1e-3),
        "step": h,
        "warning": "No experimental full-PBPK fit or structural identifiability proof",
    }
    (ident / "whole_body_sensitivity_rank.json").write_text(json.dumps(diag, indent=2) + "\n")
    # Analytic structural invariance for tractable submodels.
    v, cl, f, ka, dose = sp.symbols("v cl f ka dose", positive=True)
    iv = sp.Matrix([dose / v, cl / v]).jacobian([v, cl])
    sc = sp.Matrix([f * dose / v, cl / v, ka]).jacobian([v, cl, f, ka])
    structural = {
        "IV_one_compartment": {
            "observables": ["D/V", "CL/V"],
            "rank": iv.rank(),
            "determinant": str(sp.factor(iv.det())),
        },
        "SC_one_compartment_unknown_F": {
            "observables": ["FD/V", "CL/V", "ka"],
            "rank": sc.rank(),
            "parameters": ["V", "CL", "F", "ka"],
            "nullspace": [[str(z) for z in x] for x in sc.nullspace()],
            "invariance": (
                "(V, CL, F) -> a*(V, CL, F), within F bounds; absolute CL,V,F not "
                "separately identifiable"
            ),
            "additional_ambiguity": (
                "absorption versus elimination pole assignment may require prior or IV data"
            ),
        },
    }
    (ident / "structural_identifiability.json").write_text(json.dumps(structural, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    table = pd.DataFrame(rankings)
    for ax, metric in zip(axes, ["plasma_AUC_0_336", "colon_free_AUC_0_336"]):
        df = table[table.metric == metric].sort_values("ST")
        ax.barh(df.parameter, df.ST, xerr=df.ST_conf)
        ax.set(title=metric, xlabel="Sobol total effect (N=128, wide uncertainty)")
    fig.suptitle("Illustrative parameter ranges; sensitivity is not identifiability")
    fig.tight_layout()
    fig.savefig(out / "ranked_importance.png", dpi=150)
    plt.close(fig)
    metadata = {
        "classification": (
            "exploratory illustrative full-body sensitivities, not empirical disease effects"
        ),
        "problem": problem,
        "morris_trajectories": 8,
        "sobol_N": 128,
        "sobol_comparison_N": 64,
        "second_order": False,
        "forward_evaluations": len(all_points),
        "max_N64_N128_ST_change": float(pd.DataFrame(convergence).absolute_change.max()),
        "sampling_converged": False,
        "reason": "Low-N screening; convergence not established",
        "fixed_geometry": "Chunk 2 illustrative organs",
        "endpoint_caveats": (
            "Half-life is late-window apparent slope; flux/plasma is "
            "instantaneous, not NCA clearance"
        ),
    }
    (out / "design.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    sensitivity()
