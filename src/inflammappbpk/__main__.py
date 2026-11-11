"""Command-line baseline and whole-body simulations in explicitly documented units."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from inflammappbpk.compartments import LinearPK, exposure
from inflammappbpk.research_platform import Scenario, run_scenario
from inflammappbpk.simulation import Dose, simulate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    baseline = commands.add_parser(
        "baseline", help="One-compartment reference; amounts nmol, time h"
    )
    baseline.add_argument("--route", choices=["iv", "sc"], default="iv")
    baseline.add_argument("--dose-nmol", type=float, default=100.0)
    baseline.add_argument("--hours", type=float, default=48.0)
    baseline.add_argument("--output", type=Path, default=Path("results/baseline"))
    whole = commands.add_parser("whole", help="Uncalibrated whole-body research scenario")
    whole.add_argument("--config", type=Path)
    whole.add_argument("--output", type=Path, default=Path("results/whole"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.command == "baseline":
        if not np.isfinite(args.hours) or args.hours <= 0:
            parser.error("hours must be positive")
        model = LinearPK()
        time = np.linspace(0, args.hours, 241)
        result = simulate(model, time, [Dose(0, args.dose_nmol, args.route)])
        frame = pd.DataFrame(result.amounts.T, columns=result.names)
        frame.insert(0, "time_h", time)
        summary = dict(
            **model.descriptors(),
            **exposure(time, result.state("central") / model.vc),
            classification="reference linear model; generic parameters",
            route=args.route,
            dose_nmol=args.dose_nmol,
        )
    else:
        config = Scenario(**json.loads(args.config.read_text())) if args.config else Scenario()
        result = run_scenario(config)
        frame = result["curves"]
        summary = result["summary"]
        (args.output / "configuration.json").write_text(
            json.dumps(config.payload(), indent=2) + "\n"
        )
    frame.to_csv(args.output / "simulation.csv", index=False)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
