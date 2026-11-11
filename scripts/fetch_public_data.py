"""Retrieve only the small pinned public source needed for the numerical benchmark."""

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    for source in json.loads((ROOT / "configs/public_benchmark_manifest.json").read_text()):
        path = ROOT / source["local_path"]
        if not path.exists():
            if "url" not in source:
                raise FileNotFoundError(f"Missing versioned benchmark {path}")
            with urllib.request.urlopen(source["url"], timeout=30) as response:
                payload = response.read(source["max_bytes"] + 1)
            if len(payload) > source["max_bytes"]:
                raise ValueError("Download exceeds source budget")
            if hashlib.sha256(payload).hexdigest() != source["sha256"]:
                raise ValueError("Source checksum mismatch; downloaded content was not saved")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Source checksum mismatch: {path}")
        print(source["id"] + ": checksum verified")


if __name__ == "__main__":
    main()
