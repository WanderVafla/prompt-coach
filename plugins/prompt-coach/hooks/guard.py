"""UserPromptSubmit hook: log every prompt, and in learning mode point Claude
at the rules the prompt may break. Claude decides whether it really does."""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import mode, paths, prompt_text, rules, weeks  # noqa: E402

CONTEXT = (
    "[prompt-coach] This project is in learning mode: the user wants to build skills, "
    "not just get results. Possible rule hits in this prompt:\n{hits}\n"
    "Only if the prompt really breaks a rule, start your reply with one line: "
    "'⚠️ <rule id> · <rule name>: <the question>' in the user's language, then answer "
    "the request normally. If the prompt already contains the user's own attempt, idea "
    "or hypothesis, add nothing and do not mention prompt-coach."
)


def main() -> None:
    event = json.load(sys.stdin)
    prompt = event.get("prompt", "")
    if prompt_text.is_noise(prompt):
        return

    cwd = event.get("cwd") or "."
    project_mode = mode.find_mode(cwd)
    override = prompt_text.is_override(prompt)
    checked = project_mode == mode.LEARNING and not override
    data = paths.data_dir()
    hits = rules.signals(prompt, data) if checked else []

    now = datetime.now().astimezone()
    entry = {
        "ts": now.isoformat(timespec="seconds"),
        "session": event.get("session_id", ""),
        "project": mode.project_name(cwd),
        "mode": project_mode,
        "prompt": prompt_text.loggable(prompt),
        "flags": rules.base_flags(prompt) if checked else [],
        "signals": [r["id"] for r in hits],
        "override": override,
    }
    log = paths.log_file(data, weeks.week_id(now.date()))
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if hits:
        lines = "\n".join(f"- {r['id']} {r['name']}: {r['hint']}. Question: {r['question']}" for r in hits)
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": CONTEXT.format(hits=lines),
        }}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # a broken coach must never block a prompt
        print(f"prompt-coach: {error}", file=sys.stderr)
