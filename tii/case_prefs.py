"""Case preferences (pin/hide) stored separately from case definitions.

We keep preferences in a separate file so built-in cases (A-H) remain immutable
and dynamic cases can share the same UX.

Local-first, file-backed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_PREFS_PATH = Path(__file__).resolve().parent.parent / "data" / "case_prefs.json"


def load_case_prefs(path: Path = DEFAULT_PREFS_PATH) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        return {}
    return data


def save_case_prefs(prefs: Dict[str, Dict[str, Any]], path: Path = DEFAULT_PREFS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prefs, indent=2, sort_keys=True))


def get_pref(case_id: str, key: str, default: Any = None) -> Any:
    prefs = load_case_prefs()
    return prefs.get(case_id, {}).get(key, default)


def set_pref(case_id: str, key: str, value: Any) -> None:
    prefs = load_case_prefs()
    prefs.setdefault(case_id, {})[key] = value
    save_case_prefs(prefs)


def is_pinned(case_id: str) -> bool:
    return bool(get_pref(case_id, "pinned", False))


def is_hidden(case_id: str) -> bool:
    return bool(get_pref(case_id, "hidden", False))
