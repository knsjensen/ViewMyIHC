"""A Home Assistant automation that tells short, long and double presses of an IHC push button apart.

IHC reports a push button as an on/off value (on while pressed), so the automation measures the press itself:
still on after ``long_ms`` is a long press; released and pressed again within ``double_ms`` is a double press;
otherwise a short press. ``mode: single`` lets the automation's own waits catch the release and the second press.
"""

from __future__ import annotations

import re
from typing import Any

import yaml

_ENTITY = re.compile(r"^binary_sensor\.[a-z0-9_]+$")


def _seconds(ms: int) -> str:
    return f"00:00:{ms / 1000:06.3f}"


TEXTS = {
    "da": {"press": "tryk", "long": "Langt tryk", "double": "Dobbelt tryk", "short": "Kort tryk",
           "replace": "erstat med din egen handling", "description": "Kort, langt og dobbelt tryk på {title} (lavet med ViewMyIHC)"},
    "en": {"press": "press", "long": "Long press", "double": "Double press", "short": "Short press",
           "replace": "replace with your own action", "description": "Short, long and double press of {title} (made with ViewMyIHC)"},
}


def press_automation(entity_id: str, name: str, long_ms: int = 800, double_ms: int = 400, language: str = "en") -> str:
    """YAML for one automation with a placeholder action per press type."""
    if not _ENTITY.match(entity_id):
        raise ValueError("Expected a binary_sensor entity id")
    if not 200 <= long_ms <= 5000 or not 100 <= double_ms <= 2000:
        raise ValueError("Times out of range")
    title = name or entity_id
    text = TEXTS.get(language, TEXTS["en"])

    def placeholder(kind: str) -> list[dict[str, Any]]:
        return [{"action": "logbook.log", "data": {"name": title, "message": f"{text[kind]} – {text['replace']}"}}]

    def state(to: str, **extra: str) -> list[dict[str, Any]]:
        return [{"trigger": "state", "entity_id": entity_id, **extra, "to": to}]

    automation = {
        "alias": f"{title} – {text['press']}",
        "description": text["description"].replace("{title}", title),
        "mode": "single",
        "triggers": state("on", **{"from": "off"}),
        "actions": [
            {"wait_for_trigger": state("off"), "timeout": _seconds(long_ms)},
            {
                "choose": [{"alias": text["long"], "conditions": "{{ wait.trigger is none }}",
                            "sequence": placeholder("long")}],
                "default": [
                    {"wait_for_trigger": state("on"), "timeout": _seconds(double_ms)},
                    {"if": "{{ wait.trigger is not none }}", "then": placeholder("double"), "else": placeholder("short")},
                ],
            },
        ],
    }
    return yaml.safe_dump(automation, sort_keys=False, allow_unicode=True, width=120)
