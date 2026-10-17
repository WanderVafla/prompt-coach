"""The user's own pattern changes, learned from weekly reviews.

Stored in the plugin data folder, so plugin updates keep them and the shared
`rules/patterns.json` stays the same for everyone.

    {"added":    [{"rule", "pattern", "week", "bad_hits", "other_hits"}],
     "disabled": [{"rule", "pattern", "week", "precision", "hits"}]}
"""

import json
from pathlib import Path

FILE_NAME = "patterns.local.json"


def path(data: Path) -> Path:
    return data / FILE_NAME


def load(data: Path) -> dict[str, list[dict]]:
    file = path(data)
    stored = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
    return {"added": stored.get("added", []), "disabled": stored.get("disabled", [])}


def save(data: Path, overlay: dict[str, list[dict]]) -> None:
    path(data).write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
