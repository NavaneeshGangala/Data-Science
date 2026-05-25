"""
Download MovieLens 100K dataset.

Source: GroupLens (https://grouplens.org/datasets/movielens/100k/)
       Mirror on Kaggle: https://www.kaggle.com/datasets/prajitdatta/movielens-100k-dataset

This script downloads the MovieLens 100K dataset and extracts it to ./data/ml-100k/.
Run from the project root:

    python scripts/download_data.py

If GroupLens is unreachable, the script will also try the Kaggle CLI (requires
`pip install kaggle` and a configured ~/.kaggle/kaggle.json) and finally fall
back to the bundled synthetic sample in ./data/sample/ so the notebook still
runs end-to-end.
"""
from __future__ import annotations

import io
import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TARGET_DIR = DATA_DIR / "ml-100k"
SAMPLE_DIR = DATA_DIR / "sample"

PRIMARY_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
KAGGLE_DATASET = "prajitdatta/movielens-100k-dataset"


def _try_grouplens() -> bool:
    print(f"[1/3] Trying GroupLens primary mirror: {PRIMARY_URL}")
    try:
        req = urllib.request.Request(PRIMARY_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = r.read()
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            zf.extractall(DATA_DIR)
        print(f"    -> extracted to {TARGET_DIR}")
        return True
    except Exception as exc:
        print(f"    !! failed: {exc}")
        return False


def _try_kaggle() -> bool:
    print(f"[2/3] Trying Kaggle CLI: {KAGGLE_DATASET}")
    try:
        import subprocess
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET,
             "-p", str(DATA_DIR), "--unzip"],
            check=True,
        )
        nested = DATA_DIR / "ml-100k" / "ml-100k"
        if nested.exists():
            TARGET_DIR.mkdir(parents=True, exist_ok=True)
            for f in nested.iterdir():
                shutil.move(str(f), TARGET_DIR / f.name)
            nested.rmdir()
        print(f"    -> extracted to {TARGET_DIR}")
        return True
    except FileNotFoundError:
        print("    !! kaggle CLI not installed (pip install kaggle)")
        return False
    except Exception as exc:
        print(f"    !! failed: {exc}")
        return False


def _use_sample() -> bool:
    print(f"[3/3] Falling back to bundled sample in {SAMPLE_DIR}")
    if not SAMPLE_DIR.exists():
        print("    !! sample directory missing - regenerate with scripts/make_sample.py")
        return False
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for f in SAMPLE_DIR.iterdir():
        shutil.copy2(f, TARGET_DIR / f.name)
    print(f"    -> copied sample to {TARGET_DIR}")
    return True


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if TARGET_DIR.exists() and any(TARGET_DIR.iterdir()):
        print(f"Data already present at {TARGET_DIR}. Delete the folder to re-download.")
        return 0
    for step in (_try_grouplens, _try_kaggle, _use_sample):
        if step():
            print("\nDone.")
            return 0
    print("\nCould not obtain dataset.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
