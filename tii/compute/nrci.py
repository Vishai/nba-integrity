"""Compute Net Rating Collapse Index (NRCI) — Weight: 25%."""

import numpy as np
import pandas as pd

from tii import cache
from tii.config import get_case


def compute_nrci(case_id: str) -> dict:
    """Compute NRCI component metrics for a case study.

    Sub-components:
      2a. Rolling 15-game net rating windows — detect steepest decline
      2b. Q4 close-game performance isolation
      2c. Pre/post elimination net rating split
      2d. Opponent-adjusted expected net rating vs actual

    Returns dict with all NRCI sub-component data for rendering.
    """
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    result = {
        "rolling_net_rating": {},
        "q4_performance": {},
        "pre_post_elim": {},
        "opponent_adjusted": {},
    }

    # Load data
    box_scores = cache.load_df("box_scores_advanced", team_id=team_id, season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if box_scores.empty:
        result["error"] = "No box score data — run ingest with box scores first"
        return result

    if game_logs.empty:
        result["error"] = "No game log data"
        return result

    # Merge box scores with game logs for date ordering
    game_logs = game_logs.sort_values("game_date").reset_index(drop=True)
    merged = game_logs.merge(
        box_scores[["game_id", "off_rating", "def_rating", "net_rating", "pace"]],
        on="game_id",
        how="left",
    )
    merged = merged.sort_values("game_date").reset_index(drop=True)

    # Get elimination info
    elim_data = cache.load_computed(case_id, "elimination")
    elim_date = elim_data["data"].get("elimination_date") if elim_data else None
    elim_game_num = elim_data["data"].get("elimination_game_number") if elim_data else None

    total_games = len(merged)

    # --- 2a. Rolling 15-game net rating ---
    window = 15
    if len(merged) >= window:
        rolling_nr = merged["net_rating"].rolling(window=window, min_periods=window).mean()

        # Find peak and trough
        valid = rolling_nr.dropna()
        if len(valid) > 0:
            peak_idx = valid.idxmax()
            trough_idx = valid.idxmin()
            peak_val = round(float(valid[peak_idx]), 1)
            trough_val = round(float(valid[trough_idx]), 1)

            # Steepest decline = peak before trough
            if peak_idx < trough_idx:
                decline = round(peak_val - trough_val, 1)
            else:
                # Peak came after trough — find best peak before lowest point
                pre_trough = valid[:trough_idx + 1]
                if len(pre_trough) > 0:
                    alt_peak = round(float(pre_trough.max()), 1)
                    decline = round(alt_peak - trough_val, 1)
                else:
                    decline = 0

            # Season-long net rating
            season_nr = round(float(merged["net_rating"].mean()), 1)

            # First 15 and last 15
            first_15_nr = round(float(merged["net_rating"].iloc[:15].mean()), 1)
            last_15_nr = round(float(merged["net_rating"].iloc[-15:].mean()), 1)

            # Collect rolling values for every 10th game
            snapshots = []
            for i in range(window - 1, len(merged), 10):
                if i < len(rolling_nr) and pd.notna(rolling_nr.iloc[i]):
                    snapshots.append({
                        "game_number": i + 1,
                        "rolling_net_rating": round(float(rolling_nr.iloc[i]), 1),
                    })

            result["rolling_net_rating"] = {
                "season_net_rating": season_nr,
                "first_15_net_rating": first_15_nr,
                "last_15_net_rating": last_15_nr,
                "peak_rolling": peak_val,
                "peak_game": int(peak_idx) + 1,
                "trough_rolling": trough_val,
                "trough_game": int(trough_idx) + 1,
                "max_decline": decline,
                "snapshots": snapshots,
            }

    # --- 2b. Q4 close-game performance ---
    # Use plus_minus and pts data to approximate close games
    # A "close game" = margin <= 5 points at any point in Q4
    # Since we don't have play-by-play, approximate with final margin <= 10
    close_games = merged[abs(merged["pts"] - merged.get("opp_pts", merged["pts"])) <= 10]

    # Since opp_pts might be 0 (placeholder), use plus_minus from box score
    # Actually game_logs has pts but opp_pts=0. Use net_rating as proxy.
    # Better approach: games with net_rating between -5 and 5 were close
    close_mask = merged["net_rating"].between(-8, 8)
    close = merged[close_mask]
    blowout_loss = merged[(merged["wl"] == "L") & (merged["net_rating"] < -15)]

    if not close.empty:
        close_wins = int(close["wl"].eq("W").sum())
        close_total = len(close)
        close_wp = round(close_wins / close_total, 3) if close_total > 0 else 0

        result["q4_performance"] = {
            "close_games": close_total,
            "close_wins": close_wins,
            "close_losses": close_total - close_wins,
            "close_game_win_pct": close_wp,
            "blowout_losses": len(blowout_loss),
            "blowout_loss_pct": round(len(blowout_loss) / total_games, 3),
        }

    # --- 2c. Pre/post elimination net rating ---
    if elim_date and elim_game_num:
        pre_elim = merged.iloc[:elim_game_num]
        post_elim = merged.iloc[elim_game_num:]

        if not pre_elim.empty and not post_elim.empty:
            pre_nr = round(float(pre_elim["net_rating"].mean()), 1)
            post_nr = round(float(post_elim["net_rating"].mean()), 1)
            nr_change = round(post_nr - pre_nr, 1)

            pre_off = round(float(pre_elim["off_rating"].mean()), 1)
            post_off = round(float(post_elim["off_rating"].mean()), 1)
            pre_def = round(float(pre_elim["def_rating"].mean()), 1)
            post_def = round(float(post_elim["def_rating"].mean()), 1)

            result["pre_post_elim"] = {
                "elimination_date": elim_date,
                "elimination_game": elim_game_num,
                "pre_elim_games": len(pre_elim),
                "post_elim_games": len(post_elim),
                "pre_elim_net_rating": pre_nr,
                "post_elim_net_rating": post_nr,
                "net_rating_change": nr_change,
                "pre_elim_off_rating": pre_off,
                "post_elim_off_rating": post_off,
                "pre_elim_def_rating": pre_def,
                "post_elim_def_rating": post_def,
                "collapse_flag": nr_change < -3.0,
            }
    else:
        result["pre_post_elim"] = {"note": "No elimination date — split N/A"}

    # --- 2d. Opponent-adjusted (simple version) ---
    # Compare team's net rating to league average for teams with similar records
    standings = cache.load_df("standings_snapshots", season=season)
    if not standings.empty:
        team_row = standings[standings["team_id"] == team_id]
        if not team_row.empty:
            team_wins = int(team_row.iloc[0]["wins"])

            # Teams within +/-5 wins
            similar = standings[
                (standings["wins"] >= team_wins - 5) &
                (standings["wins"] <= team_wins + 5) &
                (standings["team_id"] != team_id)
            ]

            if not similar.empty:
                # Load their net ratings from splits (Overall)
                peer_nrs = []
                for _, peer in similar.iterrows():
                    peer_splits = cache.load_df(
                        "team_splits",
                        team_id=int(peer["team_id"]),
                        season=season,
                    )
                    overall = peer_splits[peer_splits["split_type"] == "Overall"]
                    if not overall.empty:
                        peer_nrs.append(float(overall.iloc[0]["net_rating"]))

                if peer_nrs:
                    peer_avg_nr = round(np.mean(peer_nrs), 1)
                    team_season_nr = round(float(merged["net_rating"].mean()), 1)
                    diff = round(team_season_nr - peer_avg_nr, 1)

                    result["opponent_adjusted"] = {
                        "team_net_rating": team_season_nr,
                        "peer_group_avg_net_rating": peer_avg_nr,
                        "peer_count": len(peer_nrs),
                        "difference_from_peers": diff,
                        "team_wins": team_wins,
                        "peer_win_range": f"{team_wins - 5} to {team_wins + 5}",
                    }

    # Store
    cache.store_computed(case_id, team_id, season, "NRCI", result)
    return result
