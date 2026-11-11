#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
source scripts/environment.sh
if command -v uv >/dev/null 2>&1; then
  _inflammappbpk_uv="$(command -v uv)"
else
  python3.12 -m venv .bootstrap
  .bootstrap/bin/python -m pip install uv==0.13.5
  _inflammappbpk_uv="$PWD/.bootstrap/bin/uv"
fi
"$_inflammappbpk_uv" sync --frozen --all-extras
"$_inflammappbpk_uv" pip check --python .venv/bin/python
