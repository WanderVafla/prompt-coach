"""Review notes in the vault: naming and frontmatter reading."""

import re
from pathlib import Path

SHARE_FOLDER = "_share"
TREND_NOTE = "_trend.md"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def note_path(folder: Path, week: str, author: str) -> Path:
    return folder / f"{week} {author}.md"


def share_path(folder: Path, week: str, author: str) -> Path:
    return folder / SHARE_FOLDER / f"{week} {author}.md"


def frontmatter(note: Path) -> tuple[str, dict[str, str]]:
    """Raw frontmatter block and its flat `key: value` pairs."""
    found = FRONTMATTER.match(note.read_text(encoding="utf-8"))
    if not found:
        return "", {}
    raw = found.group(1)
    pairs = {}
    for line in raw.splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "-")):
            pairs[key.strip()] = value.strip().strip('"')
    return raw, pairs


def previous(folder: Path, week: str, author: str) -> Path | None:
    """The author's latest review before `week`."""
    earlier = sorted(p for p in folder.glob(f"*-W* {author}.md") if p.name < f"{week} ")
    return earlier[-1] if earlier else None
