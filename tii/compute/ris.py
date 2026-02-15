"""Compute Rotation Integrity Score (RIS) — Weight: 25%."""

import numpy as np
import pandas as pd

from tii import cache
from tii.config import get_case


def compute_ris(case_id: str) -> dict:
    """Compute RIS component metrics for a case study.

    Sub-components:
      3a. Baseline rotation (pre-elimination top-8 minutes distribution)
      3b. Post-elimination rotation changes
      3c. Minutes-to-quality correlation shift
      3d. Lineup consistency / experimentation rate

    Returns dict with all RIS sub-component data for rendering.
    """
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    result = {
        "baseline_rotation": {},
        "post_elim_changes": {},
        "quality_correlation": {},
        "experimentation": {},
    }

    # Load data
    player_box = cache.load_df("box_scores_advanced_players", team_id=team_id, season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)
    pgl = cache.load_df("player_game_logs", team_id=team_id, season=season)

    if player_box.empty:
        result["error"] = "No player box score data — run box score ingest first"
        return result

    if game_logs.empty:
        result["error"] = "No game log data"
        return result

    game_logs = game_logs.sort_values("game_date").reset_index(drop=True)
    total_games = len(game_logs)

    # Get elimination info
    elim_data = cache.load_computed(case_id, "elimination")
    elim_date = elim_data["data"].get("elimination_date") if elim_data else None
    elim_game_num = elim_data["data"].get("elimination_game_number") if elim_data else None

    if not elim_date or not elim_game_num:
        result["error"] = "No elimination date — RIS requires elimination context"
        return result

    # Split game IDs into pre/post elimination
    pre_elim_games = game_logs.iloc[:elim_game_num]["game_id"].astype(str).tolist()
    post_elim_games = game_logs.iloc[elim_game_num:]["game_id"].astype(str).tolist()

    pre_box = player_box[player_box["game_id"].astype(str).isin(pre_elim_games)]
    post_box = player_box[player_box["game_id"].astype(str).isin(post_elim_games)]

    # --- 3a. Baseline rotation (pre-elimination) ---
    if not pre_box.empty:
        pre_summary = (
            pre_box.groupby(["player_id", "player_name"])
            .agg(
                avg_minutes=("minutes", "mean"),
                games=("game_id", "count"),
                avg_net_rating=("net_rating", "mean"),
                avg_usg=("usg_pct", "mean"),
            )
            .reset_index()
            .sort_values("avg_minutes", ascending=False)
        )

        # Top 8 rotation players (most minutes pre-elimination)
        top8_pre = pre_summary.head(8)
        baseline = []
        for _, p in top8_pre.iterrows():
            baseline.append({
                "player_id": int(p["player_id"]),
                "player_name": p["player_name"],
                "pre_avg_minutes": round(float(p["avg_minutes"]), 1),
                "pre_games": int(p["games"]),
                "pre_net_rating": round(float(p["avg_net_rating"]), 1),
                "pre_usg": round(float(p["avg_usg"]), 3),
            })

        result["baseline_rotation"] = {
            "pre_elim_games": len(pre_elim_games),
            "total_pre_players": len(pre_summary),
            "top_8": baseline,
        }

    # --- 3b. Post-elimination rotation changes ---
    if not post_box.empty and result.get("baseline_rotation", {}).get("top_8"):
        post_summary = (
            post_box.groupby(["player_id", "player_name"])
            .agg(
                avg_minutes=("minutes", "mean"),
                games=("game_id", "count"),
                avg_net_rating=("net_rating", "mean"),
                avg_usg=("usg_pct", "mean"),
            )
            .reset_index()
            .sort_values("avg_minutes", ascending=False)
        )

        # Compare top-8 pre players to their post-elim minutes
        changes = []
        top8_ids = {p["player_id"] for p in baseline}

        for pre_player in baseline:
            pid = pre_player["player_id"]
            post_row = post_summary[post_summary["player_id"] == pid]

            if not post_row.empty:
                post_min = round(float(post_row.iloc[0]["avg_minutes"]), 1)
                post_games = int(post_row.iloc[0]["games"])
                min_change = round(post_min - pre_player["pre_avg_minutes"], 1)
                pct_change = round(
                    (min_change / pre_player["pre_avg_minutes"]) * 100, 1
                ) if pre_player["pre_avg_minutes"] > 0 else 0
            else:
                post_min = 0
                post_games = 0
                min_change = -pre_player["pre_avg_minutes"]
                pct_change = -100.0

            changes.append({
                "player_name": pre_player["player_name"],
                "pre_avg_min": pre_player["pre_avg_minutes"],
                "post_avg_min": post_min,
                "min_change": min_change,
                "pct_change": pct_change,
                "post_games": post_games,
            })

        # New players in post-elim top-8 who weren't in pre-elim top-8
        post_top8 = post_summary.head(8)
        new_rotation = []
        for _, p in post_top8.iterrows():
            if int(p["player_id"]) not in top8_ids:
                new_rotation.append({
                    "player_name": p["player_name"],
                    "post_avg_min": round(float(p["avg_minutes"]), 1),
                    "post_games": int(p["games"]),
                })

        # Average minutes change for top-8
        avg_min_change = round(np.mean([c["min_change"] for c in changes]), 1)
        # Count players with >20% minutes decrease
        significant_decreases = sum(1 for c in changes if c["pct_change"] < -20)

        result["post_elim_changes"] = {
            "post_elim_games": len(post_elim_games),
            "changes": changes,
            "new_rotation_players": new_rotation,
            "avg_minutes_change": avg_min_change,
            "significant_decreases": significant_decreases,
            "rotation_disruption_flag": significant_decreases >= 3,
        }

    # --- 3c. Minutes-to-quality correlation ---
    # Compare: do better players (higher net rating) still get more minutes post-elim?
    if not pre_box.empty and not post_box.empty:
        pre_corr = _minutes_quality_corr(pre_box)
        post_corr = _minutes_quality_corr(post_box)

        if pre_corr is not None and post_corr is not None:
            corr_shift = round(post_corr - pre_corr, 3)
            result["quality_correlation"] = {
                "pre_elim_corr": round(pre_corr, 3),
                "post_elim_corr": round(post_corr, 3),
                "correlation_shift": corr_shift,
                "meritocracy_decline_flag": corr_shift < -0.15,
            }

    # --- 3d. Lineup experimentation ---
    # Count unique player appearances per game pre vs post elimination
    if not pre_box.empty and not post_box.empty:
        pre_unique = pre_box.groupby("game_id")["player_id"].nunique()
        post_unique = post_box.groupby("game_id")["player_id"].nunique()

        pre_avg_players = round(float(pre_unique.mean()), 1)
        post_avg_players = round(float(post_unique.mean()), 1)

        # Count total unique players used
        pre_total_unique = pre_box["player_id"].nunique()
        post_total_unique = post_box["player_id"].nunique()

        result["experimentation"] = {
            "pre_avg_players_per_game": pre_avg_players,
            "post_avg_players_per_game": post_avg_players,
            "pre_total_unique_players": pre_total_unique,
            "post_total_unique_players": post_total_unique,
            "experimentation_increase": round(post_avg_players - pre_avg_players, 1),
        }

    # Store
    cache.store_computed(case_id, team_id, season, "RIS", result)
    return result


def _minutes_quality_corr(box_df: pd.DataFrame) -> float | None:
    """Compute correlation between minutes and net_rating across players."""
    summary = (
        box_df.groupby("player_id")
        .agg(avg_minutes=("minutes", "mean"), avg_nr=("net_rating", "mean"))
        .reset_index()
    )
    summary = summary[summary["avg_minutes"] > 5]  # Exclude garbage-time-only players
    if len(summary) < 5:
        return None
    return float(summary["avg_minutes"].corr(summary["avg_nr"]))
