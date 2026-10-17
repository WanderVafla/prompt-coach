"""Check a written review note, then publish its comparable part.

Turns `[[R4]]` rule links into links Obsidian labels with the rule name,
refreshes the rule notes in `_rules/`, writes `_share/<week> <author>.md` with
the frontmatter only (no prompts, so it is safe to send to others) and creates
the Dataview trend note if missing.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from lib import reviews, rule_notes  # noqa: E402

REQUIRED = ["type", "author", "week", "plugin_version", "rubric_version", "score", "score_learning", "score_tool",
            "prompts", "learning_prompts", "signals", "signal_rate", "overrides"]
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def check(note: Path) -> tuple[str, dict[str, str]]:
    raw, pairs = reviews.frontmatter(note)
    missing = [key for key in REQUIRED if key not in pairs]
    if missing:
        sys.exit(f"Missing frontmatter keys in {note.name}: {', '.join(missing)}")
    if pairs["type"] != "prompt-review":
        sys.exit("Frontmatter `type` must be `prompt-review`")
    return raw, pairs


def ensure_trend(folder: Path, language: str) -> Path:
    trend = folder / reviews.TREND_NOTE
    if not trend.exists():
        template = TEMPLATES / f"trend.{language}.md"
        if not template.exists():
            template = TEMPLATES / "trend.en.md"
        trend.write_text(template.read_text(encoding="utf-8").replace("{folder}", _vault_relative(folder)),
                         encoding="utf-8")
    return trend


def _vault_relative(folder: Path) -> str:
    """Dataview paths start at the vault root: the first parent holding `.obsidian`."""
    for parent in folder.parents:
        if (parent / ".obsidian").is_dir():
            return folder.relative_to(parent).as_posix()
    return folder.name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--note", required=True)
    parser.add_argument("--language", default="en")
    args = parser.parse_args()

    note = Path(args.note)
    raw, pairs = check(note)
    note.write_text(rule_notes.resolve_links(note.read_text(encoding="utf-8")), encoding="utf-8")
    rules_folder = rule_notes.write_all(note.parent, args.language)
    share = reviews.share_path(note.parent, pairs["week"], pairs["author"])
    share.parent.mkdir(exist_ok=True)
    share.write_text(f"---\n{raw}\n---\n", encoding="utf-8")
    trend = ensure_trend(note.parent, args.language)
    print(f"ok\nshare: {share}\ntrend: {trend}\nrules: {rules_folder}")


if __name__ == "__main__":
    main()
