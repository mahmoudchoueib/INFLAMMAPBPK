"""Exercise dependencies on synthetic data. Outputs are not PBPK validation."""

import importlib
import importlib.metadata as metadata
import json
import platform
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = {
    "checked_at_utc": datetime.now(UTC).isoformat(),
    "python": sys.version,
    "platform": platform.platform(),
    "checks": {},
    "imports": {},
    "versions": {},
}


def check(name, operation):
    try:
        detail = operation()
        report["checks"][name] = {"status": "passed", "detail": detail}
    except Exception:
        report["checks"][name] = {"status": "failed", "error": traceback.format_exc()}


modules = [
    "numpy",
    "scipy",
    "scipy.optimize",
    "pandas",
    "matplotlib",
    "pint",
    "pydantic",
    "sympy",
    "lmfit",
    "arviz",
    "numpyro",
    "jax",
    "diffrax",
    "SALib",
    "pyarrow",
    "duckdb",
    "openpyxl",
    "requests",
    "httpx",
    "bs4",
    "lxml",
    "scanpy",
    "anndata",
    "mygene",
    "Bio",
    "plotly",
    "streamlit",
    "kaleido",
    "pytest",
    "pytest_cov",
    "ruff",
    "mypy",
    "pre_commit",
    "jupyterlab",
    "ipykernel",
    "pymupdf",
    "pypdf",
    "inflammappbpk",
]
for name in modules:
    try:
        importlib.import_module(name)
        report["imports"][name] = "passed"
    except Exception:
        report["imports"][name] = traceback.format_exc()
for dist in metadata.distributions():
    report["versions"][dist.metadata["Name"]] = dist.version


def jax_diffrax():
    import diffrax as dfx
    import jax
    import jax.numpy as jnp
    import numpy as np

    jax.config.update("jax_enable_x64", True)

    def solve(rate):
        term = dfx.ODETerm(lambda t, y, args: -args * y)
        sol = dfx.diffeqsolve(
            term,
            dfx.Tsit5(),
            t0=0,
            t1=1,
            dt0=0.01,
            y0=jnp.array(1.0),
            args=rate,
            stepsize_controller=dfx.PIDController(rtol=1e-8, atol=1e-10),
        )
        return sol.ys[-1]

    value = float(solve(2.0))
    gradient = float(jax.grad(solve)(2.0))
    np.testing.assert_allclose([value, gradient], [np.exp(-2), -np.exp(-2)], rtol=1e-6)
    term = dfx.ODETerm(lambda t, y, args: -1000 * (y - jnp.cos(t)) - jnp.sin(t))
    stiff = dfx.diffeqsolve(
        term,
        dfx.Kvaerno5(),
        t0=0,
        t1=1,
        dt0=1e-4,
        y0=jnp.array(1.0),
        stepsize_controller=dfx.PIDController(rtol=1e-7, atol=1e-9),
        max_steps=10000,
    )
    np.testing.assert_allclose(float(stiff.ys[-1]), np.cos(1), atol=1e-6)
    return {
        "devices": [str(d) for d in jax.devices()],
        "x64": jax.config.x64_enabled,
        "exponential": value,
        "gradient": gradient,
        "stiff_final": float(stiff.ys[-1]),
    }


def numpyro_sampler():
    import jax
    import numpy as np
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import MCMC, NUTS

    def model():
        mean = numpyro.sample("mean", dist.Normal(0, 1))
        numpyro.sample("y", dist.Normal(mean, 1), obs=0.5)

    sampler = MCMC(NUTS(model), num_warmup=30, num_samples=40, progress_bar=False)
    sampler.run(jax.random.PRNGKey(42))
    samples = np.asarray(sampler.get_samples()["mean"])
    assert samples.shape == (40,) and np.isfinite(samples).all()
    return "40 synthetic posterior draws; execution check only, no convergence claim"


def bioinformatics():
    import anndata
    import numpy as np
    import scanpy as sc

    data = anndata.AnnData(np.array([[1.0, 2.0, 3.0], [4.0, 0.0, 6.0], [2.0, 3.0, 1.0]]))
    sc.pp.normalize_total(data, target_sum=10000)
    sc.pp.log1p(data)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "synthetic.h5ad"
        data.write_h5ad(path)
        assert anndata.read_h5ad(path).shape == (3, 3)
    return "synthetic AnnData preprocessing and H5AD round trip"


def data_tools():
    import duckdb
    import pandas as pd

    data = pd.DataFrame({"x": [1.0, 2.0]})
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "synthetic.parquet"
        data.to_parquet(path)
        assert (
            duckdb.connect()
            .execute("select sum(x) from read_parquet(?)", [str(path)])
            .fetchone()[0]
            == 3
        )
    return "Arrow Parquet and DuckDB round trip"


def matplotlib_and_html():
    import matplotlib
    import plotly.graph_objects as go

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with tempfile.TemporaryDirectory() as directory:
        plt.plot([0, 1], [1, 0])
        plt.savefig(Path(directory) / "synthetic.png")
        plt.close()
        go.Figure(go.Scatter(x=[0, 1], y=[1, 0])).write_html(Path(directory) / "plotly.html")
        assert (Path(directory) / "synthetic.png").stat().st_size > 100
        assert (Path(directory) / "plotly.html").stat().st_size > 100
    return "Matplotlib PNG and Plotly HTML artifacts verified"


def kaleido_png():
    import kaleido
    import plotly.graph_objects as go

    payload = kaleido.calc_fig_sync(
        go.Figure(go.Scatter(x=[0, 1], y=[1, 0])),
        opts={"format": "png"},
        kopts={"mathjax": False, "timeout": 30},
    )
    assert payload[:8] == b"\x89PNG\r\n\x1a\n"
    return f"PNG signature verified, {len(payload)} bytes"


check("jax_diffrax_numerics", jax_diffrax)
check("numpyro_sampler", numpyro_sampler)
check("bioinformatics", bioinformatics)
check("data_tools", data_tools)
check("matplotlib_and_plotly_html", matplotlib_and_html)
check("kaleido_png", kaleido_png)
path = ROOT / "docs" / "environment_check.json"
path.write_text(json.dumps(report, indent=2) + "\n")
failures = [name for name, value in report["checks"].items() if value["status"] != "passed"]
failures += [name for name, value in report["imports"].items() if value != "passed"]
print(
    json.dumps(
        {"imports": len(modules), "checks": report["checks"], "failures": failures}, indent=2
    )
)
sys.exit(bool(failures))
