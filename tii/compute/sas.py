"""Compute Star Availability Score (SAS) — Weight: 30%."""

import numpy as np
import pandas as pd

from tii import cache
from tii.config import get_case


def compute_sas(case_id: str) -> dict:
    """Compute SAS component metrics for a case study.

    Sub-components:
      1a. Identify qualified players (25+ min/game)
      1b. Count absences and classify (injury vs DNP-CD)
      1c. Absence clustering (post-elimination vs pre-elimination)
      1d. Distribution by game outcome (rest-in-blowout pattern)

    Returns dict with all SAS sub-component data for rendering.
    """
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    result = {
        "qualified_players": [],
        "absence_summary": {},
        "clustering": {},
        "distribution": {},
    }

    # Load data
    pgl = cache.load_df("player_game_logs", team_id=team_id, season=season)
    tgl = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if pgl.empty or tgl.empty:
        result["error"] = "No player/game log data — run ingest first"
        return result

    tgl = tgl.sort_values("game_date")
    total_games = len(tgl)
    all_game_ids = set(tgl["game_id"].astype(str))

    # Get elimination date for clustering analysis
    elim_data = cache.load_computed(case_id, "elimination")
    elim_date = elim_data["data"].get("elimination_date") if elim_data else None
    elim_game_num = elim_data["data"].get("elimination_game_number") if elim_data else None

    # --- 1a. Qualified players (25+ min/game) ---
    player_summary = (
        pgl.groupby(["player_id", "player_name"])
        .agg(
            avg_minutes=("minutes", "mean"),
            games_played=("game_id", "count"),
            total_pts=("pts", "sum"),
            avg_pts=("pts", "mean"),
        )
        .reset_index()
    )
    player_summary = player_summary.sort_values("avg_minutes", ascending=False)
    qualified = player_summary[player_summary["avg_minutes"] >= 25.0]

    players_list = []
    for _, p in qualified.iterrows():
        pid = int(p["player_id"])
        pname = p["player_name"]
        gp = int(p["games_played"])
        games_missed = total_games - gp

        # Get game IDs this player appeared in
        player_game_ids = set(
            pgl[pgl["player_id"] == pid]["game_id"].astype(str)
        )
        missed_game_ids = all_game_ids - player_game_ids

        # Classify absences: check if minutes > 0 in games they appeared in
        # If player is in game log with 0 minutes, that's a DNP
        player_rows = pgl[pgl["player_id"] == pid]
        dnp_games = player_rows[player_rows["minutes"] <= 0]
        dnp_count = len(dnp_games)

        # Games completely absent from the game log = likely injury/rest
        absent_count = len(missed_game_ids)

        # Total missed = absent + DNP
        total_missed = absent_count + dnp_count

        # Post-elimination absence count
        post_elim_missed = 0
        pre_elim_missed = 0
        if elim_date and missed_game_ids:
            for gid in missed_game_ids:
                game_row = tgl[tgl["game_id"].astype(str) == gid]
                if not game_row.empty:
                    gdate = game_row.iloc[0]["game_date"]
                    if gdate >= elim_date:
                        post_elim_missed += 1
                    else:
                        pre_elim_missed += 1

        # Count games in losses vs wins
        loss_games_missed = 0
        win_games_missed = 0
        for gid in missed_game_ids:
            game_row = tgl[tgl["game_id"].astype(str) == gid]
            if not game_row.empty and game_row.iloc[0]["wl"] == "L":
                loss_games_missed += 1
            elif not game_row.empty:
                win_games_missed += 1

        players_list.append({
            "player_id": pid,
            "player_name": pname,
            "avg_minutes": round(float(p["avg_minutes"]), 1),
            "avg_pts": round(float(p["avg_pts"]), 1),
            "games_played": gp,
            "games_missed": games_missed,
            "total_missed": total_missed,
            "absent_from_log": absent_count,
            "dnp_count": dnp_count,
            "post_elim_missed": post_elim_missed,
            "pre_elim_missed": pre_elim_missed,
            "loss_games_missed": loss_games_missed,
            "win_games_missed": win_games_missed,
        })

    result["qualified_players"] = players_list
    result["total_games"] = total_games

    # --- 1b. Absence summary ---
    total_star_absences = sum(p["total_missed"] for p in players_list)
    total_possible = len(players_list) * total_games if players_list else 0
    absence_rate = total_star_absences / total_possible if total_possible > 0 else 0

    result["absence_summary"] = {
        "total_star_absences": total_star_absences,
        "total_possible_appearances": total_possible,
        "absence_rate": round(absence_rate, 3),
        "num_qualified": len(players_list),
    }

    # --- 1c. Clustering: post-elimination vs pre-elimination absence rate ---
    if elim_date and elim_game_num and players_list:
        pre_elim_games = elim_game_num
        post_elim_games = total_games - elim_game_num

        total_pre_absences = sum(p["pre_elim_missed"] for p in players_list)
        total_post_absences = sum(p["post_elim_missed"] for p in players_list)

        pre_possible = len(players_list) * pre_elim_games if pre_elim_games > 0 else 0
        post_possible = len(players_list) * post_elim_games if post_elim_games > 0 else 0

        pre_rate = total_pre_absences / pre_possible if pre_possible > 0 else 0
        post_rate = total_post_absences / post_possible if post_possible > 0 else 0

        cluster_ratio = post_rate / pre_rate if pre_rate > 0 else 0

        result["clustering"] = {
            "elimination_date": elim_date,
            "elimination_game_number": elim_game_num,
            "pre_elim_games": pre_elim_games,
            "post_elim_games": post_elim_games,
            "pre_elim_absences": total_pre_absences,
            "post_elim_absences": total_post_absences,
            "pre_elim_absence_rate": round(pre_rate, 3),
            "post_elim_absence_rate": round(post_rate, 3),
            "cluster_ratio": round(cluster_ratio, 2),
            "flag": cluster_ratio >= 2.0,
        }
    else:
        result["clustering"] = {"note": "No elimination date — clustering N/A"}

    # --- 1d. Distribution by game outcome ---
    if players_list:
        total_loss_missed = sum(p["loss_games_missed"] for p in players_list)
        total_win_missed = sum(p["win_games_missed"] for p in players_list)
        team_losses = int(tgl["wl"].eq("L").sum())
        team_wins = int(tgl["wl"].eq("W").sum())

        loss_absence_rate = total_loss_missed / (len(players_list) * team_losses) if team_losses > 0 else 0
        win_absence_rate = total_win_missed / (len(players_list) * team_wins) if team_wins > 0 else 0

        result["distribution"] = {
            "team_wins": team_wins,
            "team_losses": team_losses,
            "absences_in_losses": total_loss_missed,
            "absences_in_wins": total_win_missed,
            "loss_absence_rate": round(loss_absence_rate, 3),
            "win_absence_rate": round(win_absence_rate, 3),
        }

    # Store
    cache.store_computed(case_id, team_id, season, "SAS", result)
    return result
