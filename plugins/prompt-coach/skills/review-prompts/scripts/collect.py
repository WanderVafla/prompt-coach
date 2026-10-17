"""Prepare a weekly review: write the prompts and their classifier batches to
the work folder, and print options, paths, stats and the previous review."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from lib import batches, options, paths, reviews, stats, weeks  # noqa: E402
from lib.sources import log, transcripts  # noqa: E402


def resolve_week(raw: str) -> str:
    if not raw:
        return weeks.last_completed()
    if raw == "current":
        return weeks.current()
    weeks.bounds(raw)  # raises on a malformed id
    return raw


def load_entries(data: Path, week: str, source: str) -> tuple[str, list[dict]]:
    if source in ("auto", "log"):
        entries = log.read(data, week)
        if entries or source == "log":
            return "log", entries
    return "transcripts", transcripts.read(week)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("week", nargs="?", default="", help="2026-W42, 'current', or empty for last week")
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--source", choices=["auto", "log", "transcripts"], default="auto")
    args = parser.parse_args()

    data = paths.data_dir(args.data_dir)
    opts = options.load(data)
    week = resolve_week(args.week)
    source, entries = load_entries(data, week, args.source)
    for number, entry in enumerate(entries):
        entry["id"] = number
    work = batches.work_dir(data, week)
    (work / "prompts.json").write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    folder = options.reviews_dir(opts)
    monday, sunday = weeks.bounds(week)

    previous = reviews.previous(folder, week, opts["author"]) if folder and folder.exists() else None
    output = {
        "week": week,
        "from": monday.isoformat(),
        "to": sunday.isoformat(),
        "source": source,
        "options": opts,
        "note_path": str(reviews.note_path(folder, week, opts["author"])) if folder else None,
        "plugin_version": paths.plugin_version(),
        "rubric_version": json.loads(paths.patterns_file().read_text())["rubric_version"],
        "stats": stats.weekly(entries),
        "previous_review": {"path": str(previous), "frontmatter": reviews.frontmatter(previous)[1]} if previous else None,
        "work_dir": str(work),
        "batches": batches.write(entries, work),
    }
    print(json.dumps(output, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
