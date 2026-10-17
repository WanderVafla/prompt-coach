"""Deterministic weekly numbers. They are the comparable part of a review:
the same prompts give the same numbers for everyone."""

from collections import Counter, defaultdict

from lib.mode import LEARNING


def weekly(entries: list[dict]) -> dict:
    learning = [e for e in entries if e["mode"] == LEARNING]
    signals = sum(1 for e in learning if e["flags"])
    return {
        "prompts": len(entries),
        "learning_prompts": len(learning),
        "signals": signals,
        "signal_rate": round(signals / len(learning), 2) if learning else 0,
        "overrides": sum(1 for e in entries if e["override"]),
        "rule_hits": dict(Counter(flag for e in learning for flag in e["flags"])),
        "projects": _per_project(entries),
    }


def _per_project(entries: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        groups[entry["project"]].append(entry)
    return [
        {
            "project": name,
            "mode": group[-1]["mode"],
            "prompts": len(group),
            "signals": sum(1 for e in group if e["flags"]),
        }
        for name, group in sorted(groups.items(), key=lambda item: -len(item[1]))
    ]
