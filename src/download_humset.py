"""Download the HumSet training data (Apache-2.0) from Hugging Face into data/raw/humset/.

Usage:  python -m src.download_humset
"""
import requests

from src.config import HUMSET

BASE = "https://huggingface.co/datasets/nlp-thedeep/humset/resolve/main/data/"

if __name__ == "__main__":
    for name in ("train.jsonl", "validation.jsonl", "test.jsonl"):
        target = HUMSET / name
        if target.exists():
            print(f"{name}: already present")
            continue
        with requests.get(BASE + name, stream=True, timeout=300) as r:
            r.raise_for_status()
            with target.open("wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        print(f"{name}: downloaded")
