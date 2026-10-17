"""Project mode lookup: `learning` or `tool`.

A project declares its mode in `.claude/ai-mode` (one word). The nearest file
up from the working directory wins. No file means `tool`, so nothing gets in
the way by default.
"""

from pathlib import Path

LEARNING = "learning"
TOOL = "tool"
MODE_FILE = Path(".claude") / "ai-mode"


def find_mode(cwd: str | Path) -> str:
    start = Path(cwd).resolve()
    for folder in [start, *start.parents]:
        candidate = folder / MODE_FILE
        if candidate.is_file():
            word = candidate.read_text().strip().lower()
            return LEARNING if word == LEARNING else TOOL
        if folder == Path.home():
            break
    return TOOL


def project_name(cwd: str | Path) -> str:
    """Name of the folder holding the mode file, else of the git root, else cwd."""
    start = Path(cwd).resolve()
    for folder in [start, *start.parents]:
        if (folder / MODE_FILE).is_file() or (folder / ".git").exists():
            return folder.name
        if folder == Path.home():
            break
    return start.name
