"""Matching of a prompt against the learning-mode patterns.

Two pattern sets exist:
- base: `rules/patterns.json`, the same for everyone. Its hits are the
  comparable `flags` of the log and the weekly stats.
- effective: base minus the user's disabled patterns plus the user's added
  ones (see `lib/local_patterns.py`). Its hits drive the hook's signals.
"""

import json
import re
from functools import cache
from pathlib import Path

from lib import catalog, local_patterns
from lib.paths import patterns_file
from lib.prompt_text import own_text


@cache
def rule_info() -> dict[str, dict]:
    """Rule id → rule fields (English name, hint, question, scope), without patterns."""
    rules = json.loads(patterns_file().read_text())["rules"]
    return {r["id"]: {**{k: v for k, v in r.items() if k != "patterns"}, "name": catalog.text(r["id"], "name", "en")}
            for r in rules}


@cache
def base_patterns() -> list[dict]:
    rules = json.loads(patterns_file().read_text())["rules"]
    return [{"rule": r["id"], "pattern": p} for r in rules for p in r["patterns"]]


def effective_patterns(data: Path) -> list[dict]:
    overlay = local_patterns.load(data)
    disabled = {(d["rule"], d["pattern"]) for d in overlay["disabled"]}
    kept = [p for p in base_patterns() if (p["rule"], p["pattern"]) not in disabled]
    return kept + [{"rule": a["rule"], "pattern": a["pattern"]} for a in overlay["added"]]


@cache
def _compiled(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.I)


def hits(prompt: str, pattern: dict) -> bool:
    """Does one pattern hit? Rules with `scope: own` ignore pasted blocks."""
    scope = rule_info().get(pattern["rule"], {}).get("scope", "own")
    text = own_text(prompt) if scope == "own" else prompt
    return bool(_compiled(pattern["pattern"]).search(text))


def matched_rules(prompt: str, patterns: list[dict]) -> list[str]:
    """Ids of the rules hit by any of `patterns`, in rule order."""
    hit = {p["rule"] for p in patterns if hits(prompt, p)}
    return [rule_id for rule_id in rule_info() if rule_id in hit]


def base_flags(prompt: str) -> list[str]:
    return matched_rules(prompt, base_patterns())


def signals(prompt: str, data: Path) -> list[dict]:
    """Rules to point Claude at, from the effective patterns."""
    return [rule_info()[rule_id] for rule_id in matched_rules(prompt, effective_patterns(data))]
