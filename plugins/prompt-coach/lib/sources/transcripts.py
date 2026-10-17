"""Prompts of a week rebuilt from Claude Code transcripts.

Used for weeks before the plugin was installed. Claude Code keeps transcripts
about 30 days, so older weeks are gone. Mode and flags are computed now, from
today's `.claude/ai-mode` files and base patterns.
"""

import json
from pathlib import Path

from lib import mode, paths, prompt_text, rules, weeks


def _user_texts(record: dict) -> list[str]:
    content = record.get("message", {}).get("content")
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [part.get("text", "") for part in content if part.get("type") == "text"]
    return []


def _is_user_prompt(record: dict) -> bool:
    return record.get("type") == "user" and not record.get("isMeta") and not record.get("isSidechain")


def read(week: str) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    entries = []
    for transcript in (paths.claude_config_dir() / "projects").glob("*/*.jsonl"):
        for line in transcript.open(encoding="utf-8", errors="replace"):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = record.get("timestamp", "")
            if not _is_user_prompt(record) or not ts or weeks.of_timestamp(ts) != week:
                continue
            for text in _user_texts(record):
                # Resumed and forked sessions copy earlier messages: keep one.
                key = (ts, text)
                if prompt_text.is_noise(text) or key in seen:
                    continue
                seen.add(key)
                entries.append(_entry(record, ts, text))
    return sorted(entries, key=lambda e: e["ts"])


def _entry(record: dict, ts: str, text: str) -> dict:
    cwd = record.get("cwd") or "."
    project_mode = mode.find_mode(cwd) if Path(cwd).exists() else mode.TOOL
    override = prompt_text.is_override(text)
    flags = rules.base_flags(text) if project_mode == mode.LEARNING and not override else []
    return {
        "ts": ts,
        "session": record.get("sessionId", ""),
        "project": mode.project_name(cwd) if Path(cwd).exists() else Path(cwd).name,
        "mode": project_mode,
        "prompt": prompt_text.loggable(text),
        "flags": flags,
        "override": override,
    }
