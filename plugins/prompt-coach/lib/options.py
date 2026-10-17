"""User options of the plugin.

Hooks receive the options as CLAUDE_PLUGIN_OPTION_* environment variables.
Skill scripts run from the Bash tool and may not, so the SessionStart hook
saves a snapshot that scripts read instead.
"""

import json
import os
from pathlib import Path

PREFIX = "CLAUDE_PLUGIN_OPTION_"
DEFAULTS = {"vault": "", "reviews_folder": "Prompt reviews", "author": "", "language": "auto"}


def from_env() -> dict[str, str]:
    found = {k[len(PREFIX):].lower(): v for k, v in os.environ.items() if k.startswith(PREFIX)}
    return {**DEFAULTS, **{k: v for k, v in found.items() if v != ""}}


def save_snapshot(data: Path, options: dict[str, str]) -> None:
    (data / "options.json").write_text(json.dumps(options, ensure_ascii=False, indent=2))


def load(data: Path) -> dict[str, str]:
    """Environment first, then the snapshot, then defaults."""
    env = {k: v for k, v in from_env().items() if v != DEFAULTS.get(k)}
    snapshot_file = data / "options.json"
    snapshot = json.loads(snapshot_file.read_text()) if snapshot_file.exists() else {}
    options = {**DEFAULTS, **snapshot, **env}
    if not options["author"]:
        options["author"] = os.environ.get("USER", "me")
    return options


def reviews_dir(options: dict[str, str]) -> Path | None:
    if not options.get("vault"):
        return None
    return Path(options["vault"]).expanduser() / options["reviews_folder"]
