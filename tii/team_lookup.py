"""Team lookup helpers using nba_api."""

from __future__ import annotations

from typing import Optional, Dict, Any

from nba_api.stats.static import teams


def lookup_team(team: str) -> Dict[str, Any]:
    """Lookup an NBA team by abbreviation or name.

    Accepts:
      - "UTA", "BOS", ...
      - "Utah Jazz", "Boston Celtics", ...
      - partial names (best effort)

    Returns a dict containing at least: id, full_name, abbreviation.
    Raises ValueError if ambiguous/not found.
    """

    q = (team or "").strip()
    if not q:
        raise ValueError("Team is required")

    # Abbreviation match first.
    if len(q) <= 4:
        found_one = teams.find_team_by_abbreviation(q.upper())
        if found_one:
            return found_one

    # Full name match.
    found = teams.find_teams_by_full_name(q)
    if len(found) == 1:
        return found[0]

    # Nickname/partial match.
    all_teams = teams.get_teams()
    lowered = q.lower()
    partial = [t for t in all_teams if lowered in t.get("full_name", "").lower()]
    if len(partial) == 1:
        return partial[0]

    if len(found) > 1 or len(partial) > 1:
        candidates = partial or found
        labels = ", ".join([t.get("full_name") for t in candidates[:10]])
        raise ValueError(f"Ambiguous team '{team}'. Candidates: {labels}")

    raise ValueError(f"Team not found: '{team}'")
