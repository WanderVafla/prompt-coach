# 📈 Tendance des prompts

> [!info] Plugin **Dataview** requis
> Les bilans sont créés par `/prompt-coach:review-prompts`. Pour vous comparer, déposez les fichiers `_share/` des autres dans votre dossier `_share/`.

## Mes semaines

```dataview
TABLE WITHOUT ID file.link AS "Bilan", score AS "🎯 Note", score_learning AS "🎓", score_tool AS "🛠️", prompts AS "Prompts", round(signal_rate * 100) + "%" AS "⚠️ signaux", overrides AS "#tool", plugin_version AS "plugin"
FROM "{folder}"
WHERE type = "prompt-review" AND file.folder = "{folder}"
SORT week DESC
```

## Comparaison

```dataview
TABLE WITHOUT ID week AS "Semaine", author AS "Qui", score AS "🎯", score_learning AS "🎓", score_tool AS "🛠️", round(signal_rate * 100) + "%" AS "⚠️", rubric_version AS "v", plugin_version AS "plugin"
FROM "{folder}/_share"
WHERE type = "prompt-review"
SORT week DESC, score DESC
```

> [!warning] Ne comparez que la même `v`
> `rubric_version` est la version des règles. Comparer des versions différentes n'est pas équitable.
