"""Measure patterns against a week of labeled prompts and decide changes.

Truth is the classifier's label: a prompt is a positive for rule R when it is
labeled `bad` with R at high confidence. Only learning-mode prompts without
`#tool` count, since signals exist only there.
"""

import re

from lib import rules
from lib.mode import LEARNING
from lib.prompt_text import own_text

MIN_HITS_TO_DISABLE = 5
DISABLE_BELOW = 0.3
MIN_HITS_TO_ENABLE = 3
ENABLE_FROM = 0.6
MIN_TRUE_HITS_TO_ADD = 2
ADD_FROM = 0.75
MAX_SHARE_OF_PROMPTS = 0.2
MAX_ADDED_PER_WEEK = 3
MAX_ADDED_TOTAL = 30
MISS_PREVIEW = 300


def corpus(entries: list[dict], labels: dict[int, dict]) -> list[dict]:
    """Labeled learning prompts with the set of rules they really break."""
    items = []
    for entry in entries:
        label = labels.get(entry["id"])
        if entry["mode"] != LEARNING or entry["override"] or label is None or label.get("confidence") == "low":
            continue
        broken = set(label.get("rules", [])) if label.get("verdict") == "bad" else set()
        items.append({"prompt": entry["prompt"], "broken": broken})
    return items


def measure(pattern: dict, items: list[dict]) -> dict:
    matched = [i for i in items if rules.hits(i["prompt"], pattern)]
    true_hits = sum(1 for i in matched if pattern["rule"] in i["broken"])
    return {"hits": len(matched), "true_hits": true_hits,
            "precision": round(true_hits / len(matched), 2) if matched else None}


def misses(items: list[dict], patterns: list[dict]) -> dict[str, list[str]]:
    """Per rule: prompts that break it but no effective pattern of it catches."""
    found: dict[str, list[str]] = {}
    for item in items:
        for rule_id in item["broken"]:
            own = [p for p in patterns if p["rule"] == rule_id]
            if not any(rules.hits(item["prompt"], p) for p in own):
                found.setdefault(rule_id, []).append(own_text(item["prompt"])[:MISS_PREVIEW])
    return found


def to_disable(patterns: list[dict], items: list[dict]) -> list[dict]:
    result = []
    for pattern in patterns:
        stats = measure(pattern, items)
        if stats["hits"] >= MIN_HITS_TO_DISABLE and stats["precision"] < DISABLE_BELOW:
            result.append({**pattern, **stats})
    return result


def to_enable(disabled: list[dict], items: list[dict]) -> list[dict]:
    result = []
    for pattern in disabled:
        stats = measure(pattern, items)
        if stats["hits"] >= MIN_HITS_TO_ENABLE and stats["precision"] >= ENABLE_FROM:
            result.append({**pattern, **stats})
    return result


def check_proposal(proposal: dict, items: list[dict]) -> str | None:
    """None when the proposed pattern is good enough, else the reason why not."""
    if proposal.get("rule") not in rules.rule_info():
        return "unknown rule"
    try:
        re.compile(proposal["pattern"], re.I)
    except (re.error, KeyError) as error:
        return f"invalid regex: {error}"
    stats = measure(proposal, items)
    if stats["true_hits"] < MIN_TRUE_HITS_TO_ADD:
        return f"catches {stats['true_hits']} real cases, needs {MIN_TRUE_HITS_TO_ADD}"
    if stats["precision"] < ADD_FROM:
        return f"precision {stats['precision']}, needs {ADD_FROM}"
    if items and stats["hits"] / len(items) > MAX_SHARE_OF_PROMPTS:
        return f"hits {stats['hits']} of {len(items)} prompts, too broad"
    return None
