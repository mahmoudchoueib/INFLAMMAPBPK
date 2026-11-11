# Final quality assurance — 11 November 2026

| Check | Executed outcome |
|---|---|
| Pre-change suite | 81 passed |
| Final main-checkout suite | 100 passed, zero failed/skipped |
| Clean-source full suite | 100 passed, zero failed/skipped |
| Static analysis | Ruff passed for src/tests/scripts/dashboard |
| Configured types | mypy passed for 34 source files |
| Numerical properties | Analytical references, mass/flow balances, target/FcRn limits, repeated events, BDF/Radau and tolerance checks |
| Dashboard integration | All 15 pages; simulation, transport comparison and infliximab opt-in gates passed |
| Real browser | Playwright 1.62.0 / Chromium 156; health, actual simulation and Plotly navigation passed, no frontend errors |
| Scientific exports | 15 figures, each PNG/SVG/PDF, checksummed; explicit missing-evidence figure for infliximab |
| Reports | Markdown/HTML/JSON with fits, sources, configuration and version hashes |
| Clean reproduction | Fresh virtual environment; 211 package compatibility check; no raw-paper/result copy or private data |

The clean check used a source export, **not a clone of an updated remote branch**.
It installed into that export, confirmed imports point to the new source, retrieved
pinned small public inputs and regenerated analyses/figures/reports. Verified
package-artifact caches were shared; source, data and result caches were not copied.
Clinical outputs matched within relative tolerance 1e-8, Sobol indices within
absolute tolerance 1e-5, and posterior rate quantiles within relative tolerance .02.
These are explicit reproducibility thresholds, not clinical accuracy tolerances.

Records: results/quality/clean_reproduction.json, clean_install.log,
clean_reproduce.log, browser_smoke.json and dashboard_browser.png. The source
archive is results/release/InflammaPBPK-source.zip. The QA server was stopped after
checks; `make dashboard` starts a new service on the normal port.

QA found and fixed finite terminal-half-life reporting at zero clearance and
inaccessible peripheral Vss reporting. Regression assertions were added. Form
interaction tests submit atomically, matching Streamlit semantics. No existing
test was removed to obtain success. An optional browser-harness import-order
failure was corrected and the full main workflow rerun successfully.

Numerical and software QA do not validate physiological assumptions. Hypothetical
whole-body defaults can generate slow elimination or delayed peaks inconsistent
with typical human summaries; the warning applies to defaults as well as changed
parameters. Do not tune residual clearance merely to make curves visually plausible
or add aggregate clearance on top of mechanistic catabolism without justification.
Independent domain/code review and actual assay-compatible tissue evidence remain
necessary before publication or predictive interpretation.
