"""Compute Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%."""

import numpy as np
import pandas as pd

from tii import cache
from tii.config import get_case, ASB_DATES, TRADE_DEADLINES
from tii.ingest.historical import BASELINE_SEASONS


def compute_btca(case_id: str) -> dict:
    """Compute BTCA component metrics for a case study.

    Returns dict with all BTCA sub-component data for rendering.
    """
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    result = {
        "league_context": {},
        "temporal_pattern": {},
        "calendar_correlation": {},
    }

    # --- 4a. League Context ---
    standings = cache.load_df("standings_snapshots", season=season)
    if standings.empty:
        result["error"] = "No standings data — run ingest first"
        return result

    team_row = standings[standings["team_id"] == team_id]
    if team_row.empty:
        result["error"] = f"Team {team_id} not found in {season} standings"
        return result

    team_wins = int(team_row.iloc[0]["wins"])
    team_losses = int(team_row.iloc[0]["losses"])

    # Bottom-6 teams this season
    bottom_6 = standings.nsmallest(6, "wins")
    bottom_6_wins = bottom_6["wins"].astype(int).tolist()
    bottom_6_teams = list(zip(bottom_6["team_name"].tolist(), bottom_6_wins))

    # Historical baseline: bottom-6 average wins across 20 seasons
    historical_bottom6_avgs = []
    for hist_season in BASELINE_SEASONS:
        hist_standings = cache.load_df("standings_snapshots", season=hist_season)
        if hist_standings.empty:
            continue
        hist_bottom6 = hist_standings.nsmallest(6, "wins")
        historical_bottom6_avgs.append(hist_bottom6["wins"].astype(float).mean())

    if historical_bottom6_avgs:
        hist_mean = np.mean(historical_bottom6_avgs)
        hist_std = np.std(historical_bottom6_avgs, ddof=1) if len(historical_bottom6_avgs) > 1 else 0
        current_bottom6_avg = np.mean(bottom_6_wins)
        deviation = (current_bottom6_avg - hist_mean) / hist_std if hist_std > 0 else 0
    else:
        hist_mean = hist_std = deviation = 0
        current_bottom6_avg = np.mean(bottom_6_wins)

    # Count teams on pace for <22 wins
    teams_under_22 = len(standings[standings["wins"] < 22])

    result["league_context"] = {
        "team_wins": team_wins,
        "team_losses": team_losses,
        "team_record": f"{team_wins}-{team_losses}",
        "bottom_6_teams": bottom_6_teams,
        "bottom_6_wins": bottom_6_wins,
        "historical_avg": round(hist_mean, 1),
        "historical_std": round(hist_std, 1),
        "current_bottom6_avg": round(current_bottom6_avg, 1),
        "deviation_from_baseline": round(deviation, 2),
        "teams_under_22_wins": teams_under_22,
        "league_wide_flag": teams_under_22 >= 4,
        "seasons_analyzed": len(historical_bottom6_avgs),
    }

    # --- 4b. Individual Team Temporal Pattern ---
    splits = cache.load_df("team_splits", team_id=team_id, season=season)

    pre_asb = splits[splits["split_type"] == "PreAll-Star"] if not splits.empty else pd.DataFrame()
    post_asb = splits[splits["split_type"] == "PostAll-Star"] if not splits.empty else pd.DataFrame()

    if not pre_asb.empty and not post_asb.empty:
        pre_wp = float(pre_asb.iloc[0]["win_pct"])
        post_wp = float(post_asb.iloc[0]["win_pct"])
        ratio = (post_wp / pre_wp * 100) if pre_wp > 0 else 0
        below_50 = ratio < 50

        # Check roster talent loss >30% (placeholder — needs EPM data in v2)
        talent_loss_clears = False

        result["temporal_pattern"] = {
            "pre_asb_win_pct": round(pre_wp, 3),
            "pre_asb_record": f"{int(pre_asb.iloc[0]['w'])}-{int(pre_asb.iloc[0]['l'])}",
            "post_asb_win_pct": round(post_wp, 3),
            "post_asb_record": f"{int(post_asb.iloc[0]['w'])}-{int(post_asb.iloc[0]['l'])}",
            "post_as_pct_of_pre": round(ratio, 1),
            "below_50_threshold": below_50,
            "roster_talent_loss_clears_flag": talent_loss_clears,
            "flag": below_50 and not talent_loss_clears,
            "pre_asb_net_rating": round(float(pre_asb.iloc[0].get("net_rating", 0)), 1),
            "post_asb_net_rating": round(float(post_asb.iloc[0].get("net_rating", 0)), 1),
        }
    else:
        result["temporal_pattern"] = {"error": "Pre/post ASB splits not available"}

    # --- 4c. Calendar Correlation ---
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)
    if not game_logs.empty:
        game_logs = game_logs.sort_values("game_date")

        trade_deadline = TRADE_DEADLINES.get(season)
        asb_date = ASB_DATES.get(season)

        # Get elimination date
        elim_data = cache.load_computed(case_id, "elimination")
        elim_date = elim_data["data"].get("elimination_date") if elim_data else None

        periods = {}

        if trade_deadline:
            pre_td = game_logs[game_logs["game_date"] < trade_deadline]
            if not pre_td.empty:
                w = int(pre_td["wl"].eq("W").sum())
                total = len(pre_td)
                periods["Pre-trade deadline"] = {
                    "win_rate": round(w / total, 3) if total > 0 else 0,
                    "record": f"{w}-{total - w}",
                    "games": total,
                }

        if trade_deadline and asb_date:
            td_to_asb = game_logs[
                (game_logs["game_date"] >= trade_deadline) &
                (game_logs["game_date"] < asb_date)
            ]
            if not td_to_asb.empty:
                w = int(td_to_asb["wl"].eq("W").sum())
                total = len(td_to_asb)
                periods["Post-deadline to ASB"] = {
                    "win_rate": round(w / total, 3) if total > 0 else 0,
                    "record": f"{w}-{total - w}",
                    "games": total,
                }

        if asb_date and elim_date:
            asb_to_elim = game_logs[
                (game_logs["game_date"] >= asb_date) &
                (game_logs["game_date"] < elim_date)
            ]
            if not asb_to_elim.empty:
                w = int(asb_to_elim["wl"].eq("W").sum())
                total = len(asb_to_elim)
                periods["Post-ASB to elimination"] = {
                    "win_rate": round(w / total, 3) if total > 0 else 0,
                    "record": f"{w}-{total - w}",
                    "games": total,
                }
        elif asb_date:
            post_asb_all = game_logs[game_logs["game_date"] >= asb_date]
            if not post_asb_all.empty:
                w = int(post_asb_all["wl"].eq("W").sum())
                total = len(post_asb_all)
                periods["Post-ASB"] = {
                    "win_rate": round(w / total, 3) if total > 0 else 0,
                    "record": f"{w}-{total - w}",
                    "games": total,
                }

        if elim_date:
            post_elim = game_logs[game_logs["game_date"] >= elim_date]
            if not post_elim.empty:
                w = int(post_elim["wl"].eq("W").sum())
                total = len(post_elim)
                periods["Post-elimination"] = {
                    "win_rate": round(w / total, 3) if total > 0 else 0,
                    "record": f"{w}-{total - w}",
                    "games": total,
                }

        result["calendar_correlation"] = {
            "periods": periods,
            "trade_deadline": trade_deadline,
            "asb_date": asb_date,
            "elimination_date": elim_date,
        }

    # Store
    cache.store_computed(case_id, team_id, season, "BTCA", result)
    return result
