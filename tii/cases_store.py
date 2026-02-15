"""Dynamic case registry.

The original tool shipped with a fixed set of lettered case studies (A-H).
This module adds a lightweight, file-backed registry so you can add *any*
team/season pair and compute/ingest it like the built-in cases.

Design goals:
- No database required (works locally + in Streamlit Cloud)
- Stable case IDs (TEAMABBR-SEASON, e.g. "UTA-2024-25")
- Track who added the case for lightweight contributor aggregation
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CASES_PATH = Path(__file__).resolve().parent.parent / "data" / "cases.json"
DEFAULT_ACTIVITY_LOG_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "activity_log.jsonl"
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_case_id(team_abbr: str, season: str) -> str:
    """Create a stable case id."""

    return f"{team_abbr.upper()}-{season}"


def load_dynamic_cases(path: Path = DEFAULT_CASES_PATH) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Invalid cases registry format at {path}")
    return data


def save_dynamic_cases(cases: Dict[str, Dict[str, Any]], path: Path = DEFAULT_CASES_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cases, indent=2, sort_keys=True))


def append_activity(event: Dict[str, Any], path: Path = DEFAULT_ACTIVITY_LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": _utc_now_iso(), **event}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def add_dynamic_case(
    *,
    team_abbr: str,
    team_id: int,
    team_name: str,
    season: str,
    archetype: str = "Ad-hoc",
    expected_classification: str = "Unknown",
    playoff_cutoff_seed: int = 10,
    added_by: Optional[str] = None,
    path: Path = DEFAULT_CASES_PATH,
) -> str:
    cases = load_dynamic_cases(path)

    case_id = make_case_id(team_abbr, season)
    if case_id in cases:
        return case_id

    cases[case_id] = {
        "team_abbr": team_abbr.upper(),
        "team_id": int(team_id),
        "season": season,
        "team_name": team_name,
        "archetype": archetype,
        "expected_classification": expected_classification,
        "playoff_cutoff_seed": int(playoff_cutoff_seed),
        "added_by": added_by,
        "created_at": _utc_now_iso(),
    }

    save_dynamic_cases(cases, path)

    append_activity(
        {
            "event": "case_added",
            "case_id": case_id,
            "team_abbr": team_abbr.upper(),
            "team_id": int(team_id),
            "season": season,
            "added_by": added_by,
        }
    )

    return case_id
