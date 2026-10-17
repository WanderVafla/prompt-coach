"""Prompts of a week from the plugin's own log."""

import json
from pathlib import Path

from lib import paths


def read(data: Path, week: str) -> list[dict]:
    log = paths.log_file(data, week)
    if not log.exists():
        return []
    with log.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
