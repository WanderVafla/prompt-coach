---
name: review-prompts
description: Weekly review of the user's own prompts to Claude Code against the "lever, not crutch" rubric, written as a note into their Obsidian vault with a 1–12 score, best and worst prompts, rewrites and one focus rule for next week. Use when the user runs /prompt-coach:review-prompts or asks to review, grade or score their prompts of a week.
argument-hint: "[2026-W42 | current]  (empty = last completed week)"
allowed-tools: Read, Write, Agent, Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py *), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/labels.py *), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/tune.py *), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/finalize.py *)
---

# Weekly prompt review

## 1. Collect

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py $ARGUMENTS --data-dir "${CLAUDE_PLUGIN_DATA}"
```

The JSON holds `week`, `options`, `note_path`, `rubric_version`, `stats`,
`previous_review`, `work_dir` and `batches`. Stop and tell the user when:
- `note_path` is null: the `vault` option is not set. Tell them to run
  `/plugin`, open prompt-coach and set it.
- `batches` is empty: nothing to review for that week. If `source` is
  `transcripts`, older weeks may already be deleted by Claude Code.

`source: transcripts` means the week predates the plugin's log; say so in the
note in one line.

## 2. Label with Haiku

Labeling every prompt is the bulk of the work, so a cheap model does it.
Launch one `prompt-coach:prompt-classifier` agent per item of `batches`,
**all in one message** so they run in parallel. Each gets only:

```
rubric: ${CLAUDE_SKILL_DIR}/rubric.md
batch: <batch>
out: <out>
```

If that agent type is not available, use a general-purpose agent with
`model: haiku` and tell it to follow `${CLAUDE_PLUGIN_ROOT}/agents/prompt-classifier.md`.
Do not read the batch files yourself.

When all agents are done:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/labels.py --work-dir "<work_dir>"
```

It prints `verdicts` per mode, `rules` (good / bad counts per rule),
`regex_confirmed` and `candidates`: every prompt labeled good or bad, or
labeled with low confidence. If it reports missing labels, relaunch the
agents for those batches only.

## 3. Grade

Read `${CLAUDE_SKILL_DIR}/rubric.md` and grade from the `labels.py` summary.
Haiku labels are the evidence, you are the judge:
- re-read every `confidence: low` candidate and decide yourself;
- spot-check a few `high` ones; if Haiku is clearly wrong, correct it and
  trust the remaining labels less;
- grade each mode by its own rules: learning by R1–R7, tool by T1–T8;
- in the signals table, `confirmed` comes from `regex_confirmed`.

Pick:
- **best**: 2–3 prompts that show a rule done well;
- **fix**: 3–5 weakest prompts, each with a rewrite in the user's own style
  and language. Quote real prompts, shortened with `…`, never invented ones;
- **focus**: exactly one rule for next week, the one whose improvement
  would change the most. Not the same as `previous_review.frontmatter.focus`
  unless that one did not improve.

## 4. Tune the signals

The hook's patterns learn from these labels. Changes go to the user's own
`patterns.local.json`; the shared `rules/patterns.json` and the comparable
`flags` / `signals` stats never change.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/tune.py report --work-dir "<work_dir>" --data-dir "${CLAUDE_PLUGIN_DATA}"
```

Read `misses`: prompts that break a rule but no pattern caught. Where at
least two of them share a wording, propose one regex per wording:
- match the user's own phrasing, typos included (`проверь`, `праверь`);
- Python `re`, case-insensitive; use `\b` around short words;
- narrow beats broad: a pattern that also hits good prompts is rejected.

Write the proposals to `<work_dir>/proposals.json` as
`[{"rule": "R4", "pattern": "…", "why": "…"}]` (or `[]`), then:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/tune.py apply --work-dir "<work_dir>" --data-dir "${CLAUDE_PLUGIN_DATA}" --week <week> --proposals "<work_dir>/proposals.json"
```

The script decides, not you: it adds only proposals that catch ≥ 2 real
cases with precision ≥ 0.75, disables patterns that fire ≥ 5 times with
precision < 0.3, and re-enables disabled ones that became accurate. Put its
`added`, `disabled`, `enabled` into the note's patterns section; skip the
section when all three are empty.

## 5. Write the note

Language: `options.language`, or with `auto` the language most prompts
are written in. Frontmatter keys stay in English (Dataview and comparison
depend on them); everything else is in the chosen language.

Fill `${CLAUDE_SKILL_DIR}/templates/review.md` and write it to `note_path`:
- `plugin_version` and `rubric_version` are copied from the collect output;
- frontmatter numbers `prompts`, `learning_prompts`, `signals`,
  `signal_rate`, `overrides` are copied from `stats` exactly;
- `score_learning` / `score_tool` are `null` when the mode has < 5 prompts;
- trend arrow and delta compare with `previous_review.frontmatter.score`,
  or write `—` when there is no previous review;
- refer to rules **only** as `[[R4]]`, `[[T3]]`: never write rule names, in
  any language. Obsidian shows the names from `_rules/` (step 6 creates them);
  keep a link on its own line in callouts, not in the callout title;
- repeat a block (table row, callout) as many times as needed and delete
  blocks that would be empty.

Style: short lines, Obsidian callouts, tables and `==highlights==` instead of
paragraphs. The note is read in under two minutes.

## 6. Publish

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/finalize.py --note "<note_path>" --language <language>
```

It checks the frontmatter, turns `[[R4]]` into named links, refreshes `_rules/`, writes the shareable copy (numbers only, no
prompts) to `_share/` and creates the Dataview trend note on first run. If
it reports missing keys, fix the note and run it again.

## 7. Reply

One line: score, trend, focus rule, and the note path. Nothing else; the
note is the result.
