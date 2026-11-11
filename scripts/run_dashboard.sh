#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
source scripts/environment.sh
exec .venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1 "$@"
