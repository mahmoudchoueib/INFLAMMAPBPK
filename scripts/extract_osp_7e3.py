"""Preserve and standardise published OSP 7E3 aggregate observations, without fitting."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from inflammappbpk.units import Q_

ROOT = Path(__file__).resolve().parents[1]


def extract(snapshot):
    rows = []
    for profile in snapshot["ObservedData"]:
        props = {p["Name"]: p["Value"] for p in profile["ExtendedProperties"]}
        grid = profile["BaseGrid"]
        for column in profile["Columns"]:
            if column["DataInfo"]["Origin"] != "Observation":
                continue
            times = np.asarray(grid["Values"], dtype=float)
            values = np.asarray(column["Values"], dtype=float)
            if len(times) != len(values):
                raise ValueError("Time/concentration lengths differ")
            if not np.isfinite(times).all() or not np.isfinite(values).all():
                raise ValueError("Nonfinite observations")
            if (values < 0).any() or (np.diff(times) < 0).any():
                raise ValueError("Negative concentrations or unsorted times")
            hours = Q_(times, grid["Unit"]).to("hour").magnitude
            nmol = Q_(values, column["Unit"]).to("nanomole/liter").magnitude
            related = column.get("RelatedColumns", [])
            if len(related) != 1:
                raise ValueError("Expected one reported error column; review source schema")
            error = related[0]
            if error["DataInfo"]["AuxiliaryType"] != "ArithmeticStdDev":
                raise ValueError("Unsupported uncertainty type; do not assume an SD")
            errors = np.asarray(error["Values"], dtype=float)
            if len(errors) != len(times) or not np.isfinite(errors).all() or (errors < 0).any():
                raise ValueError("Invalid uncertainty array")
            sd = Q_(errors, error["Unit"]).to("nanomole/liter").magnitude
            for index in range(len(times)):
                rows.append(
                    {
                        "profile": profile["Name"],
                        "point_index": index,
                        "species": props.get("Species", ""),
                        "molecule": props.get("Molecule", ""),
                        "source_sheet": props.get("Sheet", ""),
                        "organ": props.get("Organ", ""),
                        "compartment": props.get("Compartment", ""),
                        "study_id": props.get("Study Id", ""),
                        "time_original": times[index],
                        "time_unit_original": grid["Unit"],
                        "concentration_original": values[index],
                        "concentration_unit_original": column["Unit"],
                        "sd_original": errors[index],
                        "sd_unit_original": error["Unit"],
                        "time_h": hours[index],
                        "concentration_nmol_l": nmol[index],
                        "reported_sd_nmol_l": sd[index],
                        "uncertainty_flag": "reported_zero_do_not_treat_as_exact"
                        if sd[index] == 0
                        else "reported_sd",
                        "observation_level": "aggregate_from_OSP_snapshot_not_individual",
                    }
                )
    return rows


def main():
    source = ROOT / "data/raw/osp/source_7E3.json"
    rows = extract(json.loads(source.read_text()))
    target = ROOT / "data/processed/osp_7e3_observations.csv"
    with target.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_commit": "12f886989585472e26d5857364047ff2d68abbcd",
        "profiles": len({r["profile"] for r in rows}),
        "observations": len(rows),
        "gut_observations": sum(r["organ"] == "Gut" for r in rows),
        "zero_reported_sd": int(sum(r["reported_sd_nmol_l"] == 0 for r in rows)),
        "organs": sorted({r["organ"] for r in rows}),
        "processed_path": str(target.relative_to(ROOT)),
        "processed_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "eligible_for_independent_human_anti_TNF_validation": False,
        "licence_note": (
            "Source README states GPLv2 for model code; "
            "underlying observations require separate rights review"
        ),
    }
    (ROOT / "data/metadata/osp_7e3_extraction.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
