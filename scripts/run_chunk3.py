"""Execute all feasible Chunk 3 analyses; evidence gates prevent unsupported validation claims."""

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    "chunk3_curate.py",
    "chunk3_calibrate.py",
    "chunk3_bayesian.py",
    "chunk3_sensitivity.py",
    "chunk3_whole_profile.py",
    "chunk3_experiments.py",
    "chunk3_report.py",
]


def run():
    for name in [
        "calibration",
        "validation",
        "sensitivity",
        "identifiability",
        "bayesian",
        "experiments",
    ]:
        (ROOT / "results" / name).mkdir(exist_ok=True)
    manifest = {
        "started_at_utc": datetime.now(UTC).isoformat(),
        "steps": [],
        "clinical_scope": (
            "one held-out healthy-study aggregate comparison; zero independent tissue observations"
        ),
    }
    path = ROOT / "results/chunk3_run_manifest.json"
    try:
        for step in STEPS:
            before_hash = hashlib.sha256((ROOT / "scripts" / step).read_bytes()).hexdigest()
            print("Executing " + step, flush=True)
            log = ROOT / "results" / ("chunk3_" + step.removesuffix(".py") + ".log")
            with log.open("w") as stream:
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / step)],
                    cwd=ROOT,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
            manifest["steps"].append(
                {
                    "script": step,
                    "exit_code": result.returncode,
                    "executed_script_sha256": before_hash,
                    "log": str(log.relative_to(ROOT)),
                }
            )
            if hashlib.sha256((ROOT / "scripts" / step).read_bytes()).hexdigest() != before_hash:
                raise RuntimeError(f"Analysis source changed during execution: {step}")
            if result.returncode:
                raise RuntimeError(f"{step} failed; inspect {log}")
        manifest["status"] = "executed_with_scientific_limitations"
    except Exception:
        manifest["status"] = "failed"
        raise
    finally:
        manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
        manifest["input_hashes"] = {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / "data/raw/chunk3").glob("*")
            if p.is_file()
        }
        manifest["script_hashes"] = {
            step: hashlib.sha256((ROOT / "scripts" / step).read_bytes()).hexdigest()
            for step in STEPS
        }
        path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    run()
