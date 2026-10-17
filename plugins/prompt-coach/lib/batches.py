"""Split a week of prompts into batch files for the classifier agents."""

import json
from pathlib import Path

BATCH_SIZE = 50


def work_dir(data: Path, week: str) -> Path:
    folder = data / "review" / week
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("batch-*.json"):
        old.unlink()
    return folder


def write(entries: list[dict], folder: Path) -> list[dict]:
    """Batches keep each session's prompts in order and together where they fit.

    Returns, per batch, the input file and the file its labels go to.
    """
    ordered = sorted(entries, key=lambda e: (e["session"], e["ts"]))
    batches = []
    for start in range(0, len(ordered), BATCH_SIZE):
        number = len(batches) + 1
        batch_file = folder / f"batch-{number:02d}.json"
        batch_file.write_text(json.dumps(ordered[start:start + BATCH_SIZE], ensure_ascii=False, indent=1),
                              encoding="utf-8")
        batches.append({"batch": str(batch_file), "out": str(folder / f"batch-{number:02d}.labels.json")})
    return batches
