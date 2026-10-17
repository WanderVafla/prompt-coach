# 📈 Prompt trend

> [!info] Requires the **Dataview** plugin
> Reviews are written by `/prompt-coach:review-prompts`. To compare with others, drop their `_share/` files into your `_share/` folder.

## My weeks

```dataview
TABLE WITHOUT ID file.link AS "Review", score AS "🎯 Score", score_learning AS "🎓", score_tool AS "🛠️", prompts AS "Prompts", round(signal_rate * 100) + "%" AS "⚠️ signals", overrides AS "#tool", plugin_version AS "plugin"
FROM "{folder}"
WHERE type = "prompt-review" AND file.folder = "{folder}"
SORT week DESC
```

## Comparison

```dataview
TABLE WITHOUT ID week AS "Week", author AS "Who", score AS "🎯", score_learning AS "🎓", score_tool AS "🛠️", round(signal_rate * 100) + "%" AS "⚠️", rubric_version AS "v", plugin_version AS "plugin"
FROM "{folder}/_share"
WHERE type = "prompt-review"
SORT week DESC, score DESC
```

> [!warning] Compare only the same `v`
> `rubric_version` is the rules version. Reviews made with different versions are not comparable.
