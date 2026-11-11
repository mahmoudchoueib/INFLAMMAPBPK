"""Build portable Markdown/HTML analysis reports with dataset, parameter and software provenance."""

import hashlib
import html
import importlib.metadata
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from inflammappbpk.research_platform import Scenario

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def build():
    out = ROOT / "results/report"
    out.mkdir(exist_ok=True)
    manifest = load("results/chunk3_run_manifest.json")
    if manifest["status"] != "executed_with_scientific_limitations" or any(
        s["exit_code"] for s in manifest["steps"]
    ):
        raise RuntimeError("Cannot report a successful analysis from a failed run manifest")
    figs = load("results/figures/manifest.json")
    for figure in figs:
        for file in figure["exports"]:
            if sha(ROOT / file["path"]) != file["sha256"]:
                raise ValueError("Figure checksum mismatch")
    validation = pd.read_csv(ROOT / "results/validation/human_summary_validation.csv")
    versions = {
        name: importlib.metadata.version(name)
        for name in [
            "inflammappbpk",
            "numpy",
            "scipy",
            "pandas",
            "matplotlib",
            "streamlit",
            "plotly",
            "numpyro",
            "jax",
            "SALib",
        ]
    }
    source_files = sorted(
        [*(ROOT / "src").rglob("*.py"), ROOT / "pyproject.toml", ROOT / "uv.lock"]
    )
    source_hash = hashlib.sha256(
        "".join(str(p.relative_to(ROOT)) + sha(p) for p in source_files).encode()
    ).hexdigest()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True)
    provenance = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "software_versions": versions,
        "source_tree_sha256": source_hash,
        "git_revision": commit.stdout.strip() if commit.returncode == 0 else None,
        "git_revision_note": (
            "Current source hash is authoritative for uncommitted or exported source"
        ),
        "parameter_registry_sha256": sha(ROOT / "data/metadata/parameter_registry.csv"),
        "lock_sha256": sha(ROOT / "uv.lock"),
        "default_configuration": Scenario().payload(),
        "dataset_sources": load("data/metadata/chunk3_sources.json"),
        "public_benchmark_manifest": load("configs/public_benchmark_manifest.json"),
        "analysis_configuration": load("configs/chunk3_analysis.json"),
        "fit_statistics": {
            "human": load("results/calibration/human_apparent_pk.json"),
            "mouse": load("results/calibration/mouse_terminal_mle.json"),
        },
        "validation": load("results/validation/summary.json"),
        "bayesian": load("results/bayesian/summary.json"),
        "evidence_gates": load("results/validation/evidence_gates.json"),
        "figures": figs,
        "scientific_verdict": (
            "Inconclusive disease-physiology benefit; not publication-ready as a validation study"
        ),
    }
    (out / "research_report.json").write_text(
        json.dumps(provenance, indent=2, allow_nan=False) + "\n"
    )
    findings = (ROOT / "research/scientific_findings.md").read_text()
    md = "# InflammaPBPK analysis report\n\n"
    md += "**Exploratory platform; disease-informed improvement is unproven.**\n\n"
    md += "Source tree SHA-256: `" + source_hash + "`\n\n"
    md += "Parameter version (SHA-256): `" + provenance["parameter_registry_sha256"] + "`\n\n"
    md += "## Aggregate held-out comparison\n\n"
    md += "| Endpoint | Observed | Predicted | Relative error |\n|---|---:|---:|---:|\n"
    for r in validation.itertuples():
        md += (
            f"| {r.endpoint} ({r.unit}) | {r.value:g} | {r.predicted:g} | "
            f"{r.relative_error_percent:.1f}% |\n"
        )
    md += (
        "\nOne healthy trial, three correlated summaries; zero "
        "usable independent human tissue observations.\n\n"
    )
    md += "## Scientific findings\n\n" + findings + "\n\n## Figure registry\n\n"
    for f in figs:
        md += f"- [{f['id']}](../figures/{f['id']}.pdf): {f['classification']}\n"
    md += (
        "\n## Reproduction\n\nRun `make reproduce` from the "
        "completed source tree. Machine-readable provenance is "
        "in research_report.json.\n"
    )
    (out / "research_report.md").write_text(md)
    table = validation[
        ["endpoint", "value", "predicted", "relative_error_percent", "unit"]
    ].to_html(index=False, escape=True)
    document = """<!doctype html><html lang="en">
<meta charset="utf-8"><title>InflammaPBPK research report</title>
<style>
body{font-family:system-ui,sans-serif;max-width:1100px;
margin:3rem auto;line-height:1.6;color:#182736}
table{border-collapse:collapse}
td,th{padding:.5rem;border:1px solid #ccd3dc}
img{max-width:100%}
pre{white-space:pre-wrap;background:#f2f5f8;padding:1rem}
section{margin:2rem 0}
</style>
<h1>InflammaPBPK research report</h1>
<p><strong>Exploratory; disease-informed superiority remains inconclusive.</strong></p>"""
    document += "<h2>Held-out healthy-trial summary comparison</h2>" + table
    document += "<h2>Evidence and caveats</h2><pre>" + html.escape(findings) + "</pre>"
    document += (
        "<h2>Software and parameter provenance</h2><pre>"
        + html.escape(
            json.dumps(
                {
                    k: provenance[k]
                    for k in [
                        "python",
                        "software_versions",
                        "source_tree_sha256",
                        "parameter_registry_sha256",
                        "git_revision",
                    ]
                },
                indent=2,
            )
        )
        + "</pre>"
    )
    for f in figs:
        document += (
            "<section><h2>"
            + html.escape(f["id"])
            + "</h2><p>"
            + html.escape(f["classification"])
            + "</p>"
        )
        document += (
            '<img alt="'
            + html.escape(f["classification"], quote=True)
            + '" src="../figures/'
            + f["id"]
            + '.svg"></section>'
        )
    document += "</html>"
    (out / "research_report.html").write_text(document)
    print("Exported Markdown, HTML and machine-readable JSON report")


if __name__ == "__main__":
    build()
