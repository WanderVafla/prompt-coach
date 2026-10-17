"""Filesystem locations used by the plugin."""

import json
import os
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def data_dir(override: str | None = None) -> Path:
    """Persistent plugin data directory (survives plugin updates)."""
    raw = override or os.environ.get("CLAUDE_PLUGIN_DATA")
    path = Path(raw) if raw else Path.home() / ".local" / "share" / "prompt-coach"
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_file(data: Path, week: str) -> Path:
    """One JSONL log file per ISO week, e.g. log/2026-W42.jsonl."""
    folder = data / "log"
    folder.mkdir(exist_ok=True)
    return folder / f"{week}.jsonl"


def claude_config_dir() -> Path:
    raw = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(raw) if raw else Path.home() / ".claude"


def plugin_version() -> str:
    return json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]


def patterns_file() -> Path:
    return PLUGIN_ROOT / "rules" / "patterns.json"
