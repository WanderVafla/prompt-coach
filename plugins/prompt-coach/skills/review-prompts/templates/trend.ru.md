# 📈 Тренд промптов

> [!info] Нужен плагин **Dataview**
> Заметки разборов создаёт `/prompt-coach:review-prompts`. Чтобы сравниться с другими, положи их файлы из `_share/` в свою папку `_share/`.

## Мои недели

```dataview
TABLE WITHOUT ID file.link AS "Разбор", score AS "🎯 Оценка", score_learning AS "🎓", score_tool AS "🛠️", prompts AS "Промптов", round(signal_rate * 100) + "%" AS "⚠️ сигналов", overrides AS "#tool", plugin_version AS "плагин"
FROM "{folder}"
WHERE type = "prompt-review" AND file.folder = "{folder}"
SORT week DESC
```

## Сравнение

```dataview
TABLE WITHOUT ID week AS "Неделя", author AS "Кто", score AS "🎯", score_learning AS "🎓", score_tool AS "🛠️", round(signal_rate * 100) + "%" AS "⚠️", rubric_version AS "v", plugin_version AS "плагин"
FROM "{folder}/_share"
WHERE type = "prompt-review"
SORT week DESC, score DESC
```

> [!warning] Сравнивай только одинаковую `v`
> `rubric_version` — версия правил. Разборы по разным версиям сравнивать нечестно.
