"""Activity log utilities (who added/ran what).

This is a lightweight audit trail so the "body of information" grows over time
and we can report on who has pulled which seasons/teams.

Stored as JSONL at data/activity_log.jsonl.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_ACTIVITY_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "activity_log.jsonl"


def iter_events(path: Path = DEFAULT_ACTIVITY_LOG_PATH) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def summarize_activity(path: Path = DEFAULT_ACTIVITY_LOG_PATH) -> Dict[str, Any]:
    events = list(iter_events(path))

    by_user = Counter()
    by_case = Counter()
    by_event = Counter()

    for ev in events:
        by_event[ev.get("event", "unknown")] += 1
        added_by = ev.get("added_by") or ev.get("user") or "unknown"
        by_user[added_by] += 1
        case_id = ev.get("case_id")
        if case_id:
            by_case[case_id] += 1

    return {
        "total": len(events),
        "by_event": by_event.most_common(),
        "by_user": by_user.most_common(),
        "by_case": by_case.most_common(25),
    }


def tail_events(n: int = 25, path: Path = DEFAULT_ACTIVITY_LOG_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    out: List[Dict[str, Any]] = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out
