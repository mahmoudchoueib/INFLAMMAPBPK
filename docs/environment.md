# Environment evidence and commands

Reference: Debian 13 x86_64, Python 3.12.14, uv 0.13.5, CPU. No nvidia-smi or exposed
NVIDIA/AMD device/driver paths were detected; JAX enumerated TFRT_CPU_0. Installed
versions and runtime checks
are recorded in `environment_check.json`; `uv.lock` and `requirements.txt` contain
the exact resolved dependencies. The lock retains PyPI artifact hashes and all
installation requests preserve TLS verification and cloud proxy trust.

```bash
cd /workspace/INFLAMMAPBPK
bash scripts/install.sh
source scripts/environment.sh
pytest -q
ruff check src tests scripts
mypy src
python scripts/check_environment.py
python scripts/acquire_sources.py --scope github
python scripts/extract_osp_7e3.py
```

The environment checker exits nonzero if **any** import/functional check fails.
Currently the generic scientific checks pass while the expanded Kaleido PNG check
fails. It is an optional visualisation capability, not silently skipped: managed
Chromium's URLBlocklist is `*` and its allowlist covers HTTP(S), not `file://`.
Kaleido 1.5.0 generates a local file page and cannot initialise its JS scope under
that policy. A test of 1.1.0 hit the same restriction, so the lock retains 1.5.0.
Disabling MathJax did not resolve it. Browser policy was not modified. Matplotlib
PNG and Plotly HTML output are supported alternatives and are checked separately.
Do not interpret the overall checker as passing or static export as supported.

`source scripts/environment.sh` configures writable caches and activates `.venv`.
This resolves the initial ArviZ/matplotlib home-directory permission failures.
It does not overwrite HOME or the platform proxy/CA variables. Notebooks can be
run with `jupyter lab --no-browser` from the activated environment when needed;
no dashboard application or persistent service is implemented in Chunk 1.

The user explicitly requested new project manifests and tests in the Chunk 1
brief. Future environment-only setup should leave these tracked files unchanged
and use the frozen installation script. Generated dependency exports should only
change in an authorised dependency-update task.

## Chunk 4 update

The dashboard is now implemented; run `make dashboard`. Portable setup defaults to
checkout-local caches rather than a hardcoded /workspace path. Scientific static
figures use Matplotlib PNG/SVG/PDF and do not depend on Kaleido's blocked file-URL
workflow. The historical expanded Kaleido check remains distinct from required
platform QA. See installation.md and PROJECT_STATUS.md for the current workflow.
