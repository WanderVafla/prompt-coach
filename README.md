# prompt-coach

A Claude Code plugin for using AI as a **lever, not a crutch**, based on the
Jobtrek course *Utiliser une IA, 3. Levier ou béquille*.

- **Signals.** In learning projects, a prompt that skips your own thinking
  (asking for full code, "check again" without a hypothesis, asking the AI to
  write your PR text) gets one line in Claude's reply: `⚠️ R4 · Hypothesis
  before check: what did you change and why?` Claude still answers.
- **Weekly review.** `/prompt-coach:review-prompts` grades your week 1–12 and
  writes a note into your Obsidian vault: best prompts, rewrites of the worst,
  one rule to focus on next week. Haiku agents label every prompt in parallel;
  the main model only re-checks unsure labels and writes the verdict.
- **Comparison.** Each review also produces a numbers-only copy in `_share/`
  that you can send to others. A Dataview note shows your trend and the
  comparison table.

## Install

```
/plugin marketplace add WanderVafla/prompt-coach
/plugin install prompt-coach@prompt-coach
```

Then `/plugin` → prompt-coach → set the options:

| Option | Meaning |
|---|---|
| `vault` | absolute path of your Obsidian vault |
| `reviews_folder` | folder in the vault for reviews (default `Prompt reviews`) |
| `author` | your name, as others will see it |
| `language` | `auto`, `en`, `fr` or `ru` |

Requires `python3` (3.10+) and, for the trend note, the Obsidian **Dataview** plugin.

## Mark your projects

Each project says what it is for in `.claude/ai-mode`:

```bash
echo learning > .claude/ai-mode   # school projects: the AI makes you work
echo tool > .claude/ai-mode       # your own tools: the AI works, you keep control
```

No file means `tool`: nothing gets in the way.

Start a prompt with `#tool` to skip signals once (deadline). It is counted in
the review as `overrides`.

## Weekly review

```
/prompt-coach:review-prompts            # last completed week
/prompt-coach:review-prompts current    # this week so far
/prompt-coach:review-prompts 2026-W42
```

Weeks before installation are rebuilt from Claude Code transcripts, which
Claude Code keeps about 30 days.

## Learned patterns

Each review tunes the signals to you, using the week's labels as truth:

- a pattern that fires ≥ 5 times with precision < 0.3 is **disabled**;
- a disabled pattern that becomes accurate again (≥ 3 hits, precision ≥ 0.6) is **re-enabled**;
- for violations no pattern caught, the reviewer proposes new regexes; a script
  **adds** only those catching ≥ 2 real cases with precision ≥ 0.75
  (at most 3 per week, 30 in total).

Changes live in `patterns.local.json` in the plugin data folder and are listed
in the review note. The shared `rules/patterns.json` never changes, and the
stats in reviews are computed with it only, so comparisons stay fair.
To forget everything learned:

```bash
python3 <plugin>/skills/review-prompts/scripts/tune.py reset --data-dir <plugin data folder>
```

## Rule names in Obsidian

Reviews store rule ids only (`[[R4]]`). On publish they become Dataview inline
links that Obsidian labels from `_rules/R4.md`, e.g. **R4 · Hypothesis before
check**, in the review language. Hover shows the rule, click opens it. Names
live in `rules/catalog.json`; the `_rules/` notes are regenerated on each review.

## Compare with others

Send your `_share/<week> <name>.md` files (frontmatter only, no prompt text)
and put the ones you receive into your own `_share/` folder. Compare only
reviews with the same `rubric_version`.

## Privacy

Prompts are logged only on your machine, in the plugin data folder. Review
notes quote your prompts; `_share/` copies do not.

## Layout

```
plugins/prompt-coach/
  agents/           prompt-classifier.md: Haiku agent that labels one batch of prompts
  hooks/            guard.py (signals + log), session_start.py (options, reminder)
  lib/              shared code: paths, options, mode, rules, local_patterns, tuning, catalog, rule_notes, weeks, stats, batches, sources
  rules/            patterns.json: regex per rule, rubric version · catalog.json: rule names and examples (en, fr, ru)
  skills/review-prompts/
    SKILL.md        review procedure
    rubric.md       grading rules and the 1–12 scale
    scripts/        collect.py (stats + batches), labels.py (merge labels), tune.py (learned patterns), finalize.py (checks, rule links, _rules, _share, trend)
    templates/      review note and Dataview trend notes (en, fr, ru)
```
