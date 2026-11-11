# Chunk 1 status — 10 November 2026

**Partially complete; development core verified, required research work blocked.**
Chunk 2 has not started. The repository initially contained only its title README;
the user's supplied Chunk 1 brief authorised the new project files and tests.

## Completed and verified

- Python 3.12.14 `.venv`; compatible core/data/document, inference, bioinformatics,
  visualisation and engineering dependencies installed in stages. CPU execution
  verified; no exposed GPU device/driver detected. NumPyro is the sole Bayesian
  stack. Exact versions and artifact hashes are in `uv.lock`, `requirements.txt`,
  and `docs/environment_check.json` (runtime evidence).
- Standard src package and all requested mechanism/workflow directories; manifests,
  ignores, example environment variables, README, pre-commit configuration and
  writable-cache activation. All thirteen mechanism namespaces are placeholders,
  explicitly not scientific implementations.
- Installer executed successfully twice, including the complete repeat run with
  frozen dependencies. `uv pip check` reports **211 packages compatible**.
- `pytest -q`: **33 passed, 0 failed, 0 skipped**. Includes stiff Robertson ODE,
  conservation/reference endpoint, dimensional conversions, all module imports,
  working-directory-independent paths, directory structure, concentration versus
  SD unit separation, and rejection of invalid observation schemas/units.
- Ruff passed; mypy passed for 16 source files; pre-commit configuration validated.
- Expanded dependency check: **38 imports passed; five functional checks passed**:
  JAX/Diffrax CPU integration, stiff implicit integration and analytic gradient;
  NumPyro synthetic sampling; Scanpy/AnnData H5AD round trip; Arrow/DuckDB round
  trip; Matplotlib PNG and Plotly HTML output.
- **One expanded check failed:** Kaleido PNG rendering. Managed Chromium blocks
  file URLs, which Kaleido requires. Both 1.5.0 and a tested 1.1.0 hit that policy;
  the lock retains 1.5.0. This is a diagnosed optional export limitation. The
  checker preserves the failure and exits nonzero; it is not reported as passing.
- Seven bounded, commit-pinned OSP artifacts acquired and hashed. Extracted **174
  aggregate mouse 7E3 observations from 24 profiles**, including **13 gut values**,
  to `data/processed/osp_7e3_observations.csv`. Preserved original values/units and
  added standard units; **96 reported zero SDs** are flagged, not imputed.
  Source/output hashes and row/unit counts were checked; source/model reuse rights
  and original measurement methods remain explicit limitations.
- Dataset and parameter provenance registries, a source-aware preliminary review,
  state-of-the-art comparison, conditional novelty audit, data-feasibility report,
  decision log and mathematical modelling/validation plan created.

## Required work still blocked

Runtime network revision 1 still has no custom research domains. The proxy rejected
**40 distinct research-source requests**. This does not establish that the papers
or data do not exist. All eleven supplied bibliographic identifiers remain
unverified. The 12 search queries were attempted but yielded no retrievable
results; zero studies were screened. No primary paper/supplement, TAURUS processed
accession, human adalimumab calibration dataset, or independent infliximab/biopsy
validation dataset has been verified or retrieved from those research endpoints.

Consequently the systematic review, full novelty assessment and human research
feasibility decision are incomplete. The OSP reports establish prior work on
whole-body/two-pore/FcRn models, but cannot settle the entire proposed novelty claim.
The available mouse observations cannot validate human anti-TNF tissue prediction.
Human molecular and IBD physiological parameters remain unassigned when unsupported.

## Saved cloud configuration and next action

Confirmed draft saves contain `install_script`, `start_skill`, and 21 research
domain additions while retaining the package-manager preset. No secrets are
required or requested. These saves neither applied the network changes nor
published the environment. In environment settings, review and save the domain
changes to enable research access. Refresh runtime status, retry a fresh source
request, and then resume acquisition/screening. Publish the environment after its
preparation and configuration have been reviewed; fresh-task restoration has not
been tested in this session.

The existing checkout is used directly. Cloud tasks are already isolated; no Git
worktree is needed unless explicitly requested. No commits or pushes were made.
Only the title README was previously tracked; its intentional update and all new
project files are available for review. Third-party raw/processed artifacts and
the virtual environment are ignored and retained on this machine.

## Reproducible commands

```bash
cd /workspace/INFLAMMAPBPK
bash scripts/install.sh
source scripts/environment.sh
pytest -q
ruff check src tests scripts
mypy src
pre-commit validate-config
python scripts/check_environment.py  # currently exits 1: Kaleido export failure
python scripts/acquire_sources.py --scope github
python scripts/extract_osp_7e3.py
# After research networking is applied and a fresh connection succeeds:
python scripts/acquire_sources.py --scope research
```

Acquisition exit status alone is not a retrieval-success measure. Inspect
`data/metadata/retrieval_log.csv`, verify article identities and publication status,
paginate/screen all relevant search results, review primary texts and supplements,
and inspect processed-data sizes/licences before download. Establish assay meaning,
regimen/timing, inflammation severity, independence and information content before
selecting a final primary outcome. See `research/data_availability.md` and
`docs/modelling_plan.md` for the explicit go/no-go gates and fallback design.
