"""Rule names and examples per language: the single source of rule names."""

import json
from functools import cache

from lib.paths import PLUGIN_ROOT

LANGUAGES = ("en", "fr", "ru")


@cache
def rules() -> dict[str, dict]:
    return json.loads((PLUGIN_ROOT / "rules" / "catalog.json").read_text(encoding="utf-8"))


def text(rule_id: str, field: str, language: str) -> str:
    values = rules()[rule_id][field]
    return values.get(language) or values["en"]
