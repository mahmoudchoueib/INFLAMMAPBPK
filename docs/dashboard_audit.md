# Dashboard audit — 11 November 2026

## Outcome

The local dashboard opens with a reference plasma graph, using a server-rendered
PNG by default. Interactive Plotly charts remain available through **Chart
display**. The Run button is near the top of the sidebar form. Transport and
three-weight comparisons render when their page opens, without an additional
hidden action. The navigation contains 15 research pages plus **Data and system
status** and **User guide**.

The underlying model equations and reference scientific analyses were not changed.

## Checks completed

- **109 tests passed**, including conservation, parameter inference, all pages in
  both display modes, default chart visibility, nonzero target occupancy,
  rejected-input snapshot preservation, static image contents and the guide link.
- Ruff passed. Mypy passed for all source modules and `dashboard/app.py`.
- **34 live HTTP checks passed**: all 17 pages in both chart modes returned ready
  without runtime exceptions. The Run button also completed successfully.
- The live server's PNG was retrieved, verified and visually inspected. It
  contains the plasma curve, axes, units and legend.
- All four provenance tabs produced their corresponding tables. The Datasets
  table now reports current local presence alongside historical retrieval notes.
- The separate reference reproduction completed before the UI changes: all
  seven analysis stages, 669 sensitivity evaluations, Bayesian diagnostics,
  reference simulations, 15 PNG/SVG/PDF figure sets and Markdown/HTML/JSON reports.

## Dataset availability

All **three required source files** are present and match their pinned SHA-256:

| Input | Purpose |
| --- | --- |
| `data/raw/osp/source_7E3.json` | Public mouse 7E3 benchmark source. |
| `data/raw/osp/source_README.md` | Source attribution and model licence statement. |
| `data/benchmarks/human_summary_endpoints.csv` | Five published aggregate human endpoints from two trials. |

All **ten required processed/chart inputs** pass the readiness checks. These
include 174 mouse observations across 24 profiles, five human aggregate facts,
Sobol rankings, 8,000 posterior draws, posterior predictive data, synthetic model
comparisons and validation/evidence records. Required numeric chart values are
finite and the posterior diagnostic gate passed.

**Eighteen optional dataset-registry entries are not downloaded locally.** These
include historical literature and candidate-data records. They are explicitly
separated from the required benchmark; historical retrieval is not presented as
current presence. TAURUS expression matrices and independent human tissue data
remain unavailable. No missing biological observations were invented.

## Repeat the audit

Windows, from the checkout:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_dashboard.py
```

WSL2 Ubuntu: `make audit-dashboard`. The machine-readable result is written to
`results/quality/dashboard_audit.json`. The live-server verification from this
session is in `results/quality/dashboard_live_audit.json`. These generated records
are excluded from Git. The in-app status page checks the current checkout, so its
answers can change after files are added or removed.

## Verification limits

Brave UI automation remained paused after the computer-use Escape stop, including
the attempted resume. Browser-level clicks, layout and interactive hover behavior
were therefore not visually verified. Runtime navigation, both chart outputs,
image delivery and the PNG graph itself were checked independently.

One upstream SciPy runtime warning occurred during a stiff-solver test. That test
passed its numerical assertions; the live dashboard audit logged no exceptions.
The local host could not install WSL, so reproduction used the underlying Python
steps on Windows rather than the Linux Bash/Make entry points.

This is an operational audit, not clinical validation. Independent human tissue
observations remain zero, infliximab transfer is unvalidated and the central
tissue-prediction hypothesis remains inconclusive.
