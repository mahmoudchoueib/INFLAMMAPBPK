#!/usr/bin/env bash
# Source this file. Preserve HOME and platform proxy/CA configuration.
_inflammappbpk_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$_inflammappbpk_root/.cache}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$_inflammappbpk_root/.config}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$XDG_CACHE_HOME/matplotlib}"
export ARVIZ_DATA="${ARVIZ_DATA:-$XDG_CACHE_HOME/arviz}"
export IPYTHONDIR="${IPYTHONDIR:-$XDG_CACHE_HOME/ipython}"
export JUPYTER_DATA_DIR="${JUPYTER_DATA_DIR:-$_inflammappbpk_root/.local/share/jupyter}"
export JUPYTER_RUNTIME_DIR="${JUPYTER_RUNTIME_DIR:-$XDG_CACHE_HOME/jupyter/runtime}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$XDG_CACHE_HOME/uv}"
export UV_SYSTEM_CERTS=true
export JAX_PLATFORMS=cpu
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$MPLCONFIGDIR" "$ARVIZ_DATA" \
  "$IPYTHONDIR" "$JUPYTER_DATA_DIR" "$JUPYTER_RUNTIME_DIR"
if [[ -f "$_inflammappbpk_root/.venv/bin/activate" ]]; then
  source "$_inflammappbpk_root/.venv/bin/activate"
fi
