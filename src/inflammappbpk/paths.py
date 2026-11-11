"""Repository data paths without implicit working-directory dependence."""

import os
from pathlib import Path


def project_root() -> Path:
    """Locate the development checkout; installed wheels need an explicit data path."""
    for path in Path(__file__).resolve().parents:
        if (path / "pyproject.toml").is_file() and (path / "data" / "metadata").is_dir():
            return path
    raise FileNotFoundError("Development checkout not found; set INFLAMMAPBPK_DATA_DIR")


def data_root() -> Path:
    """Return the configured data root, or this checkout's data directory."""
    override = os.environ.get("INFLAMMAPBPK_DATA_DIR")
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            raise ValueError("INFLAMMAPBPK_DATA_DIR must be absolute")
        return path
    return project_root() / "data"
