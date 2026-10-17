"""Merge the classifier labels of a week into one summary for the reviewer:
counts per mode and rule, plus the prompts worth reading (bad, good, unsure)."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

MAX_TEXT = 400


def load_labels(work: Path) -> tuple[dict[int, dict], list[str]]:
    labels, missing = {}, []
    for batch in sorted(work.glob("batch-[0-9][0-9].json")):
        out = batch.with_name(batch.stem + ".labels.json")
        if not out.exists():
            missing.append(batch.name)
            continue
        for label in json.loads(out.read_text(encoding="utf-8")):
            labels[int(label["id"])] = label
    return labels, missing


def summarize(entries: list[dict], labels: dict[int, dict]) -> dict:
    counts = {"learning": Counter(), "tool": Counter()}
    rules = {"good": Counter(), "bad": Counter()}
    regex_confirmed = Counter()
    candidates, unlabeled = [], []

    for entry in entries:
        label = labels.get(entry["id"])
        if label is None:
            unlabeled.append(entry["id"])
            continue
        verdict = label.get("verdict", "neutral")
        counts[entry["mode"]][verdict] += 1
        for rule in label.get("rules", []):
            if verdict in rules:
                rules[verdict][rule] += 1
        regex_confirmed.update(r for r in entry["flags"] if verdict == "bad" and r in label.get("rules", []))
        if verdict != "neutral" or label.get("confidence") == "low":
            candidates.append({**label, "project": entry["project"], "mode": entry["mode"],
                               "session": entry["session"], "prompt": entry["prompt"][:MAX_TEXT]})

    return {
        "verdicts": {mode: dict(c) for mode, c in counts.items()},
        "rules": {verdict: dict(c) for verdict, c in rules.items()},
        "regex_confirmed": dict(regex_confirmed),
        "unlabeled": unlabeled,
        "candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", required=True)
    args = parser.parse_args()

    work = Path(args.work_dir)
    entries = json.loads((work / "prompts.json").read_text(encoding="utf-8"))
    labels, missing = load_labels(work)
    if missing:
        sys.exit(f"No labels yet for: {', '.join(missing)}")
    print(json.dumps(summarize(entries, labels), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
