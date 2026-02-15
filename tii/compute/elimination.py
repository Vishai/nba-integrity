"""Compute playoff elimination date for a team-season."""

import pandas as pd

from tii import cache
from tii.config import get_case, get_conference


def compute_elimination_date(case_id: str) -> dict:
    """Compute when a team was mathematically eliminated from playoff contention.

    Returns dict with:
        elimination_date: ISO date string or None
        elimination_game_number: int or None
        playoff_cutoff_wins: int (Nth seed's final win total)
        playoff_cutoff_seed: int (8 or 10)
        max_possible_wins_at_elimination: int
    """
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]
    cutoff_seed = case["playoff_cutoff_seed"]

    # Load standings and game logs
    standings = cache.load_df("standings_snapshots", season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if standings.empty or game_logs.empty:
        return {"error": "Missing data — run ingest first"}

    # Get conference
    conf = get_conference(team_id)

    # Find the Nth-seed team's win total in the same conference
    conf_standings = standings[standings["conference"] == conf].sort_values(
        "wins", ascending=False
    )

    if len(conf_standings) < cutoff_seed:
        return {"error": f"Not enough teams in {conf} conference standings"}

    # The cutoff is the Nth seed's final win total
    cutoff_wins = int(conf_standings.iloc[cutoff_seed - 1]["wins"])

    # Walk through game log chronologically
    game_logs = game_logs.sort_values("game_number")
    total_games = len(game_logs)

    wins_so_far = 0
    elim_date = None
    elim_game = None

    for _, row in game_logs.iterrows():
        if row["wl"] == "W":
            wins_so_far += 1
        games_played = int(row["game_number"])
        remaining = total_games - games_played
        max_possible = wins_so_far + remaining

        if max_possible < cutoff_wins:
            elim_date = row["game_date"]
            elim_game = games_played
            break

    result = {
        "elimination_date": elim_date,
        "elimination_game_number": elim_game,
        "playoff_cutoff_wins": cutoff_wins,
        "playoff_cutoff_seed": cutoff_seed,
        "conference": conf,
        "final_wins": wins_so_far if elim_date is None else None,
    }

    # If not eliminated, note the final record
    if elim_date is None:
        final_w = int(game_logs.iloc[-1]["w"])
        final_l = int(game_logs.iloc[-1]["l"])
        result["final_wins"] = final_w
        result["note"] = (
            f"Team finished {final_w}-{final_l}, cutoff was {cutoff_wins} wins "
            f"(seed {cutoff_seed}). Not mathematically eliminated "
            f"(or eliminated on final game)."
        )

    # Store computed result
    cache.store_computed(case_id, team_id, season, "elimination", result)
    return result
