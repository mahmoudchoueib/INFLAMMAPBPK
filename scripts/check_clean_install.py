"""Fresh source-export installation and end-to-end public benchmark verification."""

import json
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def export_source(destination):
    ignored = {
        ".git",
        ".venv",
        ".bootstrap",
        ".cache",
        ".config",
        ".local",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".coverage",
        "htmlcov",
        "dist",
        "build",
    }

    def ignore(path, names):
        relative = Path(path).relative_to(ROOT)
        if str(relative) in ["results", "data/raw", "data/processed", "data/external_validation"]:
            return [n for n in names if n != ".gitkeep"]
        return [
            n
            for n in names
            if n in ignored
            or n.endswith(".egg-info")
            or n == ".env"
            or (n.startswith(".env.") and n != ".env.example")
        ]

    shutil.copytree(ROOT, destination, ignore=ignore)


def run():
    out = ROOT / "results/quality"
    out.mkdir(exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="inflammappbpk-clean-"))
    target = temporary / "source"
    export_source(target)
    env = os.environ.copy()
    for name in [
        "VIRTUAL_ENV",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "MPLCONFIGDIR",
        "ARVIZ_DATA",
        "IPYTHONDIR",
        "JUPYTER_DATA_DIR",
        "JUPYTER_RUNTIME_DIR",
    ]:
        env.pop(name, None)
    # Shared package artifacts are verified by uv; source/data/result state is absent.
    env["UV_CACHE_DIR"] = os.environ.get("UV_CACHE_DIR", str(ROOT / ".cache/uv"))
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["OMP_NUM_THREADS"] = "1"
    record = {
        "started_at_utc": datetime.now(UTC).isoformat(),
        "source_export": str(target),
        "raw_papers_copied": False,
        "private_data_required": False,
        "generated_results_copied": False,
        "scope": "clean source export, not a remote GitHub publication or remote clone test",
    }
    try:
        with (out / "clean_install.log").open("w") as log:
            subprocess.run(
                ["bash", "scripts/install.sh"],
                cwd=target,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        with (out / "clean_reproduce.log").open("w") as log:
            subprocess.run(
                ["make", "reproduce"],
                cwd=target,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        code = "import inflammappbpk; print(inflammappbpk.__file__)"
        location = subprocess.check_output(
            [str(target / ".venv/bin/python"), "-c", code], cwd=target, env=env, text=True
        ).strip()
        if not location.startswith(str(target)):
            raise AssertionError("Installed package refers to original source")
        actual = json.loads((target / "results/calibration/human_apparent_pk.json").read_text())
        expected = json.loads((ROOT / "results/calibration/human_apparent_pk.json").read_text())
        for key in ["CL_over_F_L_h", "V_over_F_L", "Cmax_ng_mL", "AUC_inf_ng_h_mL"]:
            np.testing.assert_allclose(actual[key], expected[key], rtol=1e-8)
        actual_s = pd.read_csv(target / "results/sensitivity/sobol_rankings.csv").sort_values(
            ["metric", "parameter"]
        )
        expected_s = pd.read_csv(ROOT / "results/sensitivity/sobol_rankings.csv").sort_values(
            ["metric", "parameter"]
        )
        np.testing.assert_allclose(
            actual_s[["S1", "ST"]], expected_s[["S1", "ST"]], atol=1e-5, rtol=0
        )
        actual_b = json.loads((target / "results/bayesian/summary.json").read_text())
        expected_b = json.loads((ROOT / "results/bayesian/summary.json").read_text())
        np.testing.assert_allclose(
            actual_b["primary"]["rate_h_median_CI95"],
            expected_b["primary"]["rate_h_median_CI95"],
            rtol=0.02,
        )
        if not actual_b["primary"]["diagnostics_thresholds_met"]:
            raise AssertionError("Clean posterior diagnostics failed")
        record.update(
            status="passed",
            installed_package=location,
            clinical_relative_tolerance=1e-8,
            sobol_absolute_tolerance=1e-5,
            posterior_quantile_relative_tolerance=0.02,
            figures=len(json.loads((target / "results/figures/manifest.json").read_text())),
        )
        # Retain a reviewable completed source bundle, excluding generated inputs/results.
        release = ROOT / "results/release"
        release.mkdir(exist_ok=True)
        bundle = temporary / "bundle"
        export_source(bundle)
        archive = shutil.make_archive(str(release / "InflammaPBPK-source"), "zip", root_dir=bundle)
        record["source_archive"] = str(Path(archive).relative_to(ROOT))
    except Exception as exc:
        record.update(status="failed", error=str(exc))
        raise
    finally:
        record["finished_at_utc"] = datetime.now(UTC).isoformat()
        (out / "clean_reproduction.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    run()
