"""Check the files required by dashboard analyses against the current checkout."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ARTIFACTS = {
    "results/sensitivity/sobol_rankings.csv": (
        "Parameter sensitivity",
        ["metric", "parameter", "ST", "ST_conf"],
    ),
    "results/bayesian/summary.json": ("Bayesian uncertainty", ["primary"]),
    "results/bayesian/primary_draws.npz": ("Bayesian uncertainty", ["log_rate"]),
    "results/bayesian/posterior_predictive.csv": (
        "Bayesian uncertainty",
        ["time_h", "observed", "predicted_median"],
    ),
    "results/experiments/synthetic_A_to_E_comparison.csv": (
        "Model comparison",
        ["truth", "model", "heldout_plasma_mae_log"],
    ),
    "results/validation/human_summary_validation.csv": (
        "Experimental validation",
        ["endpoint", "predicted_over_observed"],
    ),
    "results/validation/cross_biologic_status.json": ("Experimental validation", ["status"]),
    "results/validation/evidence_gates.json": (
        "Project overview",
        ["independent_tissue_observations", "central_hypothesis_status"],
    ),
    "data/processed/osp_7e3_observations.csv": (
        "Mouse benchmark",
        ["time_h", "concentration_nmol_l"],
    ),
    "data/processed/chunk3_human_summary_endpoints.csv": (
        "Human aggregate benchmark",
        ["study_id", "role"],
    ),
}


def source_inventory(root: Path) -> pd.DataFrame:
    """Check required pinned sources; historical retrieval flags are not presence checks."""
    records = []
    manifest = json.loads((root / "configs/public_benchmark_manifest.json").read_text("utf-8"))
    for spec in manifest:
        path = root / spec["local_path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        status = "Verified" if digest == spec["sha256"] else "Missing"
        if digest and status != "Verified":
            status = "Checksum mismatch"
        records.append({"dataset": spec["id"], "status": status, "path": spec["local_path"]})
    return pd.DataFrame(records)


def artifact_inventory(root: Path) -> pd.DataFrame:
    """Check readability and required fields without treating model output as observations."""
    records = []
    for relative, (page, fields) in ARTIFACTS.items():
        path = root / relative
        status, detail, rows = "Missing", "Regenerate the stored analyses", 0
        if path.is_file():
            try:
                if path.suffix == ".csv":
                    frame = pd.read_csv(path)
                    rows = len(frame)
                    missing = set(fields) - set(frame.columns)
                    if missing or frame.empty:
                        raise ValueError(f"Missing fields: {sorted(missing)}; rows: {rows}")
                    numeric = frame[fields].select_dtypes(include="number").to_numpy()
                    if not np.isfinite(numeric).all():
                        raise ValueError("Non-finite numeric values")
                elif path.suffix == ".npz":
                    with np.load(path, allow_pickle=False) as arrays:
                        for field in fields:
                            values = arrays[field]
                            rows = values.size
                            if not rows or not np.isfinite(values).all():
                                raise ValueError("Empty or non-finite posterior draws")
                else:
                    data = json.loads(path.read_text("utf-8"))
                    for field in fields:
                        if field not in data:
                            raise ValueError(f"Missing field: {field}")
                    if "primary" in data and not data["primary"].get("diagnostics_thresholds_met"):
                        raise ValueError("Posterior diagnostics did not pass")
                status, detail = "Ready", "Readable; required fields present"
            except (ValueError, KeyError, OSError) as exc:
                status, detail = "Invalid", str(exc)
        records.append(
            {
                "page": page,
                "status": status,
                "rows_or_draws": rows,
                "path": relative,
                "detail": detail,
            }
        )
    return pd.DataFrame(records)


def optional_inventory(root: Path) -> pd.DataFrame:
    """Keep optional literature/atlas records separate from the required benchmark."""
    frame = pd.read_csv(root / "data/metadata/dataset_registry.csv").fillna("")
    required = set(source_inventory(root).path)
    frame = frame[~frame.local_path.isin(required)].copy()
    frame["local_status"] = frame.local_path.map(
        lambda relative: "Present" if (root / relative).is_file() else "Not downloaded"
    )
    return frame[["dataset_id", "local_status", "retrieval_status", "local_path", "description"]]
