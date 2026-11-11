# Installation and reproducibility

Reference environment: Python **3.12**, uv **0.13.5**, Linux x86_64 and CPU. All
transitive versions and artifact hashes are frozen in uv.lock; requirements.txt
is an export. GPU support is not required or verified. Bash and GNU Make are used
by the workflow. Chromium is optional for browser QA. The modelling/scientific
figures do not require a desktop browser or Kaleido.

From the completed source checkout (or the supplied source archive):

```bash
bash scripts/install.sh
source scripts/environment.sh
make reproduce
make dashboard
```

The installer uses an available uv, or bootstraps pinned uv in a local .bootstrap
virtual environment with python3.12. It runs frozen installation with all extras
and development dependencies, then checks compatibility. It does not alter lockfiles.
If uv is installed manually, use version 0.13.5. Do not install into system Python.
Caches/configuration default to writable checkout-local directories, preserving
HOME, existing XDG choices, inherited proxy variables and TLS certificate trust.
After installation, source scripts/environment.sh in each shell.

An ordinary clone workflow, **once these working-tree changes have been committed
and made available on the selected branch**, is:

```bash
git clone https://github.com/mahmoudchoueib/INFLAMMAPBPK.git
cd INFLAMMAPBPK
bash scripts/install.sh
make reproduce
make dashboard
```

A clean source-export installation is separately tested and its result recorded
under results/quality. Generated results are excluded from Git.

## Dashboard on Windows PowerShell

WSL2 Ubuntu is the reference environment for the full Bash/Make workflow. To run
the dashboard directly on Windows, install Python 3.12 and run the following from
the repository directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Wait for both install commands to finish successfully before launching Streamlit.
Open the local URL printed in the terminal (normally http://localhost:8501).
Virtual environment activation is optional when using these explicit paths.
Press Ctrl+C in the server terminal to stop the dashboard. Generated analysis
panels require running the reproduction workflow in WSL2 Ubuntu.

## Public inputs

`make data` downloads only two small files from an immutable OSP Git commit: the
7E3 snapshot and source README. SHA-256 is checked before saving and checked again
before use. It then extracts the 174 aggregate records, preserving units and
uncertainty flags. The source model states GPLv2; underlying third-party
measurement/report rights are documented separately. No patient-level data are
redistributed or required.

The five human NCA summary facts are versioned in
`data/benchmarks/human_summary_endpoints.csv`, attributed to source tables and
checked against the public benchmark manifest. These are aggregate factual
summaries, not reconstructed participants or a redistributed article/figure.
Archived source URLs and original retrieval hashes remain in metadata. Raw
publisher HTML is optional for numerical reproduction: HTML navigation and article
versions can change. `python scripts/chunk3_curate.py --verify-sources` performs
strict optional raw-source verification and stops on a mismatch; it never silently
changes a source pin. Article metadata/rights should be consulted for reuse beyond
these attributed factual benchmarks. TAURUS matrices and private biopsy data are
not prerequisites for reproducing the supported results.

Internet access is required for packages and the pinned raw.githubusercontent.com
files. Current cloud policy blocks Zenodo metadata; optional TAURUS work remains
unexecuted. Source settings are not modified by any reproducibility command.

## Separate commands

```bash
make check                 # all tests, Ruff, configured mypy
make data                  # permitted small public inputs and extraction
make baseline              # generic IV one-compartment reference
make whole                 # default exploratory whole-body model
make analysis              # seven-step Chunk 3 analyses, including diagnostics
make examples              # four source-regimen exploratory scenarios
make figures               # analysis/examples + 15 PNG/SVG/PDF figure sets
make report                # above + Markdown/HTML/JSON report
make dashboard-smoke       # Streamlit AppTest checks
```

`make reproduce` executes the complete dependency graph serially. A cold global
sensitivity run evaluates 669 distinct global/Morris points using at most four
workers; expect several minutes and a few GB of memory. Reuse requires semantic
model-source and Python/NumPy/SciPy identities to match. Bayesian seeds and all
analysis choices are in configs/chunk3_analysis.json. Generated outputs are ignored
by Git and may be regenerated; source/configuration and audited facts must be kept.

## Optional browser QA

The locked Streamlit AppTest suite is included in `make check`. A separate
real-browser harness is `scripts/browser_smoke.py`. It requires Chromium at
/usr/bin/chromium and Playwright 1.62.0; it is an optional QA tool, not a modelling
runtime dependency. This session used the available managed browser tools without
modifying the dependency lock. In a separate QA environment you can run:

```bash
python3.12 -m venv /tmp/inflammappbpk-browser-qa
uv pip install --python /tmp/inflammappbpk-browser-qa/bin/python playwright==1.62.0
# Start a test server in another shell:
bash scripts/run_dashboard.sh --server.port 8765
# Then run the optional harness:
/tmp/inflammappbpk-browser-qa/bin/python scripts/browser_smoke.py
```

The harness checks health, submits an actual simulation, navigates to a rendered
Plotly chart, captures frontend errors and saves a screenshot/JSON QA record.
