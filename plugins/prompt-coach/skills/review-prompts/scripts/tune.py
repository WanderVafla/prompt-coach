"""Adapt the user's signal patterns to the labels of a reviewed week.

    tune.py report --work-dir W --data-dir D
        pattern precision, patterns to disable or re-enable, and the
        prompts no pattern caught (for proposing new patterns)
    tune.py apply --work-dir W --data-dir D --week 2026-W42 [--proposals P.json]
        disables noisy patterns, re-enables recovered ones, adds the proposed
        patterns that pass the checks; prints what changed
    tune.py reset --data-dir D
        forgets all learned changes
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from labels import load_labels  # noqa: E402
from lib import local_patterns, paths, rules, tuning  # noqa: E402


def load_corpus(work: Path) -> list[dict]:
    entries = json.loads((work / "prompts.json").read_text(encoding="utf-8"))
    labels, missing = load_labels(work)
    if missing:
        sys.exit(f"No labels yet for: {', '.join(missing)}")
    return tuning.corpus(entries, labels)


def report(work: Path, data: Path) -> dict:
    items = load_corpus(work)
    effective = rules.effective_patterns(data)
    overlay = local_patterns.load(data)
    return {
        "labeled_prompts": len(items),
        "patterns": [{**p, **tuning.measure(p, items)} for p in effective],
        "to_disable": tuning.to_disable(effective, items),
        "to_enable": tuning.to_enable(overlay["disabled"], items),
        "misses": tuning.misses(items, effective),
    }


def apply(work: Path, data: Path, week: str, proposals_file: str | None) -> dict:
    items = load_corpus(work)
    overlay = local_patterns.load(data)
    effective = rules.effective_patterns(data)
    key = lambda p: (p["rule"], p["pattern"])  # noqa: E731

    enabled = tuning.to_enable(overlay["disabled"], items)
    overlay["disabled"] = [d for d in overlay["disabled"] if key(d) not in {key(e) for e in enabled}]

    disabled = tuning.to_disable(effective, items)
    added_keys = {key(a) for a in overlay["added"]}
    for pattern in disabled:
        if key(pattern) in added_keys:
            overlay["added"] = [a for a in overlay["added"] if key(a) != key(pattern)]
        else:
            overlay["disabled"].append({**pattern, "week": week})

    proposals = json.loads(Path(proposals_file).read_text(encoding="utf-8")) if proposals_file else []
    added, rejected = [], []
    known = {key(p) for p in rules.effective_patterns(data)} | added_keys
    for proposal in proposals:
        reason = "already exists" if key(proposal) in known else tuning.check_proposal(proposal, items)
        if reason is None and len(added) >= tuning.MAX_ADDED_PER_WEEK:
            reason = f"limit of {tuning.MAX_ADDED_PER_WEEK} new patterns per week"
        if reason is None and len(overlay["added"]) >= tuning.MAX_ADDED_TOTAL:
            reason = f"limit of {tuning.MAX_ADDED_TOTAL} learned patterns"
        if reason:
            rejected.append({**proposal, "reason": reason})
            continue
        stats = tuning.measure(proposal, items)
        entry = {"rule": proposal["rule"], "pattern": proposal["pattern"], "week": week, **stats}
        overlay["added"].append(entry)
        added.append(entry)

    local_patterns.save(data, overlay)
    return {"enabled": enabled, "disabled": disabled, "added": added, "rejected": rejected}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["report", "apply", "reset"])
    parser.add_argument("--work-dir")
    parser.add_argument("--data-dir")
    parser.add_argument("--week")
    parser.add_argument("--proposals")
    args = parser.parse_args()

    data = paths.data_dir(args.data_dir)
    if args.command == "reset":
        local_patterns.path(data).unlink(missing_ok=True)
        print("learned patterns removed")
        return
    if not args.work_dir or (args.command == "apply" and not args.week):
        sys.exit("--work-dir is required, and --week for apply")
    work = Path(args.work_dir)
    result = report(work, data) if args.command == "report" else apply(work, data, args.week, args.proposals)
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
