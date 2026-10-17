---
type: prompt-review
author: {author}
week: {week}
plugin_version: "{plugin_version}"
rubric_version: {rubric_version}
score: {score}
score_learning: {score_learning}
score_tool: {score_tool}
prompts: {prompts}
learning_prompts: {learning_prompts}
signals: {signals}
signal_rate: {signal_rate}
overrides: {overrides}
focus: "{focus_rule_id}"
---

# {title} · {week}

> [!abstract] {score}/12 · {trend_arrow} {trend_delta}
> {one_line_summary}

| {h_project} | {h_mode} | {h_score} | {h_prompts} | ⚠️ |
|---|:-:|:-:|:-:|:-:|
| {project} | 🎓 / 🛠️ | {project_score} | {project_prompts} | {project_signals} |

## ✅ {h_best}

> [!success]
> [[{rule_id}]]
> «{quoted_prompt}»
> *{why_it_is_good}*

## ❌ {h_fix}

| ❌ {h_was} | ✅ {h_better} |
|---|---|
| «{quoted_prompt}» | «{rewritten_prompt}» |

## 📊 {h_signals}

| {h_rule} | {h_hits} | {h_confirmed} |
|---|:-:|:-:|
| [[{rule_id}]] | {regex_hits} | {confirmed_hits} |

## 🔧 {h_patterns}

| | {h_rule} | {h_pattern} | {h_precision} |
|:-:|---|---|:-:|
| ➕ / ➖ / ↩️ | [[{rule_id}]] | `{pattern}` | {precision} |

## 🎯 {h_focus}

> [!tip]
> [[{focus_rule_id}]]
> {focus_one_line_how}
