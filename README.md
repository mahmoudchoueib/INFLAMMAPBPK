# InflammaPBPK

An executable **exploratory** anti-TNF pharmacokinetic research platform with
baseline, minimal and whole-body PBPK, numerical tests, a 17-page Streamlit
workspace, inference tools and reproducible scientific reports.

**Scientific verdict:** disease-informed tissue prediction improvement is
inconclusive. There are zero usable independent human tissue observations and no
validated infliximab transfer. A limited held-out healthy-trial summary comparison
underpredicts AUC_inf 20.1%, Cmax 15.5%, and AUC_0_336 12.4%. The numerical tests
are not clinical validation. See [final verdict](research/final_report.md),
[scientific findings](research/scientific_findings.md), and
[critical review](research/independent_review.md).

## Install and run

Python 3.12, Bash and Make are required. From the completed source checkout:

```bash
bash scripts/install.sh
source scripts/environment.sh
make reproduce
make dashboard
```

The installer uses frozen uv.lock dependencies (reference uv 0.13.5). Without uv,
it bootstraps pinned uv in a local environment. CPU is sufficient. No private data
or GPU is required for the public benchmark. Caches use writable project-local
paths without modifying HOME or proxy/TLS settings.

For the dashboard in Windows PowerShell, see the
[Windows installation commands](docs/installation.md#dashboard-on-windows-powershell).

`make reproduce` obtains the small immutable OSP source, verifies audited public
summary facts, runs supported analyses and simulations, exports 15 figure sets as
PNG/SVG/PDF, builds Markdown/HTML/JSON reports and runs the full tests/static checks.
A cold sensitivity run can take several minutes. `make dashboard` starts Streamlit
on loopback. It does not deploy or publish anything.

## Separate workflows

```bash
make check
make data
make baseline
make whole
make analysis
make examples
make figures
make report
make dashboard-smoke
make audit-dashboard
python -m inflammappbpk baseline --route sc --dose-nmol 100 --hours 336
python -m inflammappbpk whole --output results/my_scenario
```

After analyses exist, `python scripts/generate_figures.py` and
`python scripts/build_report.py` regenerate presentation artifacts directly.
The generated report is `results/report/research_report.html`; machine-readable
provenance is in the adjacent JSON. The infliximab figure is explicitly an
evidence-gap panel, not an invented validation plot.

## Repository

- `src/inflammappbpk/`: ODEs, transport, FcRn/TMDD, inference, observation models,
  validated scenario inputs and CLI.
- `dashboard/app.py`: Streamlit/Plotly application with 15 evidence-aware sections.
- The dashboard also includes a user guide, data readiness checks, and PNG graphs
  that work without the interactive chart renderer. A reference graph loads automatically.
- `configs/`: frozen analysis choices, source pins and control provenance.
- `data/benchmarks/`: attributed public aggregate facts; no patient-level records.
- `data/metadata/`: dataset/parameter registries and missingness/provenance.
- `scripts/`: acquisition, analysis, figures, reports and clean-install QA.
- `tests/`: unit, numerical, integration and dashboard tests.
- `research/`: literature review, novelty audit, manuscript and scientific verdict.
- `docs/`: equations, assumptions, installation and dashboard guide.
- `results/`: generated, ignored artifacts retained locally and reproducible by code.

See [installation](docs/installation.md), [architecture](docs/architecture.md),
[mathematics](docs/mathematical_model.md), [inference methods](docs/inference_and_validation.md),
[validation](docs/validation.md), [dashboard guide](docs/dashboard_guide.md),
[manuscript](research/manuscript.md), and [current status](PROJECT_STATUS.md).

The [dashboard audit](docs/dashboard_audit.md) records dataset availability, chart
checks and verification limits. Open **User guide** or **Data and system status**
inside the dashboard for usage instructions and the current local file checks.

Whole-body geometry, most kinetics and disease modifiers are assumed. The UI's
weight grid is not a fitted population distribution; its mouse Bayesian panel is
not a human posterior. Infliximab requires explicit acknowledgement and IV route;
it uses a generic scaffold rather than molecule-specific validated parameters.

Generated results and virtual environments are excluded from Git. Article/source
rights and the project's software release licence require author review before a
public release.
