"""Integration checks for generated scientific artifacts and the supported CLI."""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_baseline_cli_in_separate_directory(tmp_path):
    output = tmp_path / "baseline"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "inflammappbpk",
            "baseline",
            "--route",
            "iv",
            "--dose-nmol",
            "100",
            "--hours",
            "48",
            "--output",
            str(output),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    table = pd.read_csv(output / "simulation.csv")
    assert np.allclose(
        table[["central", "peripheral", "depot", "eliminated"]].sum(axis=1), 100, atol=1e-8
    )
    assert np.allclose(table.central, 100 * np.exp(-0.015 / 3 * table.time_h), rtol=1e-6)


def test_public_summary_fixture_integrity_and_disjoint_trials():
    manifest = json.loads((ROOT / "configs/public_benchmark_manifest.json").read_text())
    spec = next(s for s in manifest if s["id"] == "human_aggregate_facts")
    path = ROOT / spec["local_path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == spec["sha256"]
    frame = pd.read_csv(path)
    assert len(frame[frame.role == "calibration"]) == 2
    assert len(frame[frame.role == "validation"]) == 3
    assert not set(frame[frame.role == "calibration"].study_id) & set(
        frame[frame.role == "validation"].study_id
    )
    assert frame.patient_id.isna().all()


def test_figure_formats_and_integrity():
    path = ROOT / "results/figures/manifest.json"
    if not path.exists():
        pytest.skip("Generate scientific artifacts with make report first")
    manifest = json.loads(path.read_text())
    assert len(manifest) == 15
    for figure in manifest:
        assert {Path(f["path"]).suffix for f in figure["exports"]} == {".png", ".svg", ".pdf"}
        for item in figure["exports"]:
            file = ROOT / item["path"]
            payload = file.read_bytes()
            assert len(payload) > 500
            assert hashlib.sha256(payload).hexdigest() == item["sha256"]
            if file.suffix == ".svg":
                assert ET.fromstring(payload).tag.endswith("svg")
            if file.suffix == ".pdf":
                assert payload.startswith(b"%PDF")
    assert "evidence-gap" in manifest[13]["classification"].lower()


def test_report_has_provenance_and_preserves_zero_tissue_count():
    path = ROOT / "results/report/research_report.json"
    if not path.exists():
        pytest.skip("Generate analysis report with make report first")
    report = json.loads(path.read_text())
    assert report["evidence_gates"]["independent_tissue_observations"] == 0
    assert report["evidence_gates"]["infliximab_validated"] is False
    assert len(report["source_tree_sha256"]) == 64
    assert len(report["parameter_registry_sha256"]) == 64
    assert len(report["figures"]) == 15
    assert (ROOT / "results/report/research_report.html").exists()
