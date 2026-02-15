"""Supplemental indicators that improve TII discrimination.

These indicators address blind spots in the core 4 components:
  - DPI: Draft Pick Incentive — how much the team benefits from losing
  - MDP: Margin of Defeat Profile — are losses unusually lopsided?
  - VSI: Veteran Shelving Index — healthy vets getting buried
  - PMI: Pace Manipulation Indicator — abnormal pace changes
  - LOI: Lineup Overhaul Index — roster churn / callup patterns
"""

import numpy as np
import pandas as pd

from tii import cache
from tii.config import get_case, get_conference


def compute_supplemental(case_id: str) -> dict:
    """Compute all supplemental indicators for a case."""
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    result = {
        "draft_pick_incentive": _compute_dpi(case_id, team_id, season),
        "margin_profile": _compute_margin_profile(case_id, team_id, season),
        "veteran_shelving": _compute_veteran_shelving(case_id, team_id, season),
        "pace_manipulation": _compute_pace_manipulation(case_id, team_id, season),
        "lineup_overhaul": _compute_lineup_overhaul(case_id, team_id, season),
    }

    cache.store_computed(case_id, team_id, season, "supplemental", result)
    return result


# ── DPI: Draft Pick Incentive ────────────────────────────────────────────────

def _compute_dpi(case_id: str, team_id: int, season: str) -> dict:
    """How much the team gained (in draft position) by each additional loss.

    The 'tanking gradient' measures the gap in wins between this team and the
    team immediately above them in the draft order. A large gap means the losses
    beyond a certain point didn't happen naturally — the team appears to have
    targeted a specific draft slot.
    """
    standings = cache.load_df("standings_snapshots", season=season)
    if standings.empty:
        return {"error": "No standings data"}

    standings = standings.sort_values("wins", ascending=True).reset_index(drop=True)
    team_row = standings[standings["team_id"] == team_id]
    if team_row.empty:
        return {"error": "Team not in standings"}

    team_wins = int(team_row.iloc[0]["wins"])
    team_losses = int(team_row.iloc[0]["losses"])
    team_rank = int(team_row.index[0])  # 0-indexed, 0 = worst record

    # Draft position (pre-lottery reform, approx: worst record = #1 pick odds)
    draft_position = team_rank + 1  # 1 = best odds, 30 = worst odds

    # Find the team with the next-worse record (next-better draft position)
    # and the team with the next-better record (next-worse draft position)
    wins_gap_below = None  # gap to team with fewer wins
    wins_gap_above = None  # gap to team with more wins

    if team_rank > 0:
        below_wins = int(standings.iloc[team_rank - 1]["wins"])
        wins_gap_below = team_wins - below_wins

    if team_rank < len(standings) - 1:
        above_wins = int(standings.iloc[team_rank + 1]["wins"])
        wins_gap_above = above_wins - team_wins

    # Bottom-5 cluster: how many teams within 3 wins of this team?
    cluster_size = len(standings[abs(standings["wins"] - team_wins) <= 3])

    # "Tank incentive" = how many wins could the team have added while
    # still finishing in the bottom 5?
    bottom_5_cutoff = int(standings.iloc[4]["wins"]) if len(standings) >= 5 else team_wins
    wins_to_exit_bottom_5 = max(0, bottom_5_cutoff - team_wins + 1)

    return {
        "team_wins": team_wins,
        "team_losses": team_losses,
        "draft_position": draft_position,  # 1=worst record
        "wins_gap_to_next_worse": wins_gap_below,
        "wins_gap_to_next_better": wins_gap_above,
        "bottom_5_cluster_size": cluster_size,
        "wins_to_exit_bottom_5": wins_to_exit_bottom_5,
        "bottom_5_cutoff_wins": bottom_5_cutoff,
        # Score: 0-100 based on how deep in the bottom they are
        "in_bottom_3": draft_position <= 3,
        "in_bottom_5": draft_position <= 5,
    }


# ── MDP: Margin of Defeat Profile ───────────────────────────────────────────

def _compute_margin_profile(case_id: str, team_id: int, season: str) -> dict:
    """Analyze the distribution and trajectory of loss margins.

    Tanking teams often show:
    - Increasing margin of defeat over the season
    - A surge in blowout losses post-elimination
    - Abnormally high variance in game margins (wins by a little, loses by a lot)
    """
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)
    box_scores = cache.load_df("box_scores_advanced", team_id=team_id, season=season)

    if game_logs.empty or box_scores.empty:
        return {"error": "No game/box data"}

    game_logs = game_logs.sort_values("game_date").reset_index(drop=True)
    merged = game_logs.merge(
        box_scores[["game_id", "net_rating"]], on="game_id", how="left"
    )

    losses = merged[merged["wl"] == "L"]
    wins = merged[merged["wl"] == "W"]

    if losses.empty:
        return {"error": "No losses found"}

    # Overall margin stats
    all_margins = merged["net_rating"].dropna()
    loss_margins = losses["net_rating"].dropna()
    win_margins = wins["net_rating"].dropna() if not wins.empty else pd.Series(dtype=float)

    avg_loss_margin = round(float(loss_margins.mean()), 1) if not loss_margins.empty else 0
    avg_win_margin = round(float(win_margins.mean()), 1) if not win_margins.empty else 0

    # Blowout analysis (losses by >15 NR)
    blowout_losses = losses[losses["net_rating"] < -15]
    blowout_pct = round(len(blowout_losses) / len(losses), 3)

    # Competitive losses (within 5 NR)
    competitive_losses = losses[losses["net_rating"] > -5]
    competitive_loss_pct = round(len(competitive_losses) / len(losses), 3)

    # First half vs second half margin trajectory
    half = len(merged) // 2
    first_half_nr = round(float(merged.iloc[:half]["net_rating"].mean()), 1)
    second_half_nr = round(float(merged.iloc[half:]["net_rating"].mean()), 1)
    trajectory = round(second_half_nr - first_half_nr, 1)

    # Post-elimination margin
    elim_data = cache.load_computed(case_id, "elimination")
    elim_game = elim_data["data"].get("elimination_game_number") if elim_data else None
    post_elim_avg_margin = None
    pre_elim_avg_margin = None

    if elim_game:
        pre = merged.iloc[:elim_game]
        post = merged.iloc[elim_game:]
        if not pre.empty and not post.empty:
            pre_elim_avg_margin = round(float(pre["net_rating"].mean()), 1)
            post_elim_avg_margin = round(float(post["net_rating"].mean()), 1)

    # Margin asymmetry: if a team wins by 3 but loses by 15, that's suspicious
    asymmetry = round(abs(avg_win_margin) - abs(avg_loss_margin), 1) if avg_win_margin else None

    return {
        "total_losses": len(losses),
        "total_wins": len(wins),
        "avg_loss_margin": avg_loss_margin,
        "avg_win_margin": avg_win_margin,
        "blowout_losses": len(blowout_losses),
        "blowout_loss_pct": blowout_pct,
        "competitive_losses": len(competitive_losses),
        "competitive_loss_pct": competitive_loss_pct,
        "first_half_net_rating": first_half_nr,
        "second_half_net_rating": second_half_nr,
        "trajectory": trajectory,
        "pre_elim_avg_margin": pre_elim_avg_margin,
        "post_elim_avg_margin": post_elim_avg_margin,
        "margin_asymmetry": asymmetry,
    }


# ── VSI: Veteran Shelving Index ──────────────────────────────────────────────

def _compute_veteran_shelving(case_id: str, team_id: int, season: str) -> dict:
    """Detect veterans on the roster getting minimal/zero playing time.

    This catches the Horford pattern: a team acquires or has a capable veteran
    who mysteriously doesn't play. Unlike SAS (which requires 25+ min/game to
    qualify), this looks at players who SHOULD be playing based on their
    career profile but aren't.

    Approach: Look at all players who appeared in <25% of games with <10 avg
    minutes, cross-reference with players who had significant minutes the
    prior season on any team.
    """
    pgl = cache.load_df("player_game_logs", team_id=team_id, season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if pgl.empty or game_logs.empty:
        return {"error": "No player/game data"}

    total_games = len(game_logs)

    # All players who appeared for this team
    player_summary = (
        pgl.groupby(["player_id", "player_name"])
        .agg(
            games=("game_id", "count"),
            avg_min=("minutes", "mean"),
            total_min=("minutes", "sum"),
            avg_pts=("pts", "mean"),
        )
        .reset_index()
    )

    # Players with significant playing time (regular rotation)
    regulars = player_summary[
        (player_summary["games"] >= total_games * 0.4) &
        (player_summary["avg_min"] >= 15)
    ]

    # Players who barely played despite being on the roster
    # Appeared in games but with very low minutes or very few games
    barely_played = player_summary[
        (player_summary["games"] < total_games * 0.25) |
        ((player_summary["games"] >= 10) & (player_summary["avg_min"] < 10))
    ]

    # Post-elimination shelving: players who had minutes early but lost them
    elim_data = cache.load_computed(case_id, "elimination")
    elim_date = elim_data["data"].get("elimination_date") if elim_data else None

    shelved_players = []
    if elim_date:
        pre_games = game_logs[game_logs["game_date"] < elim_date]["game_id"].astype(str).tolist()
        post_games = game_logs[game_logs["game_date"] >= elim_date]["game_id"].astype(str).tolist()

        if pre_games and post_games:
            for _, p in player_summary.iterrows():
                pid = int(p["player_id"])
                player_pre = pgl[(pgl["player_id"] == pid) & (pgl["game_id"].astype(str).isin(pre_games))]
                player_post = pgl[(pgl["player_id"] == pid) & (pgl["game_id"].astype(str).isin(post_games))]

                pre_min = float(player_pre["minutes"].mean()) if not player_pre.empty else 0
                post_min = float(player_post["minutes"].mean()) if not player_post.empty else 0
                pre_games_count = len(player_pre)
                post_games_count = len(player_post)

                # Player had 15+ min pre-elim, dropped to <5 post-elim
                if pre_min >= 15 and post_min < 5 and pre_games_count >= 5:
                    shelved_players.append({
                        "player_name": p["player_name"],
                        "pre_avg_min": round(pre_min, 1),
                        "post_avg_min": round(post_min, 1),
                        "pre_games": pre_games_count,
                        "post_games": post_games_count,
                        "minutes_drop": round(pre_min - post_min, 1),
                    })

    # Count players on roster who never played (appeared in 0 games in game logs)
    # We can't get this from player_game_logs since those only have active players
    # But we can detect it indirectly from roster changes

    # Total unique players used across the season
    total_unique_players = pgl["player_id"].nunique()

    # Players who only appeared in <5 games
    one_off_players = player_summary[player_summary["games"] < 5]

    return {
        "total_players_used": total_unique_players,
        "regular_rotation_size": len(regulars),
        "barely_played_count": len(barely_played),
        "barely_played": [
            {
                "player_name": r["player_name"],
                "games": int(r["games"]),
                "avg_min": round(float(r["avg_min"]), 1),
            }
            for _, r in barely_played.head(10).iterrows()
        ],
        "shelved_post_elim": shelved_players,
        "shelved_count": len(shelved_players),
        "one_off_players": len(one_off_players),
    }


# ── PMI: Pace Manipulation Indicator ─────────────────────────────────────────

def _compute_pace_manipulation(case_id: str, team_id: int, season: str) -> dict:
    """Detect abnormal pace changes that may indicate effort manipulation.

    Tanking teams sometimes play a radically different pace post-elimination:
    - Playing faster to generate more possessions (more variance → more blowouts)
    - Playing without structure → chaotic pace numbers

    We compare the team's pace to league average and track pace trajectory.
    """
    box_scores = cache.load_df("box_scores_advanced", team_id=team_id, season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if box_scores.empty or game_logs.empty:
        return {"error": "No box score / game data"}

    game_logs = game_logs.sort_values("game_date").reset_index(drop=True)
    merged = game_logs.merge(
        box_scores[["game_id", "pace"]], on="game_id", how="left"
    )
    merged = merged.dropna(subset=["pace"])

    if merged.empty or len(merged) < 20:
        return {"error": "Insufficient pace data"}

    season_pace = round(float(merged["pace"].mean()), 1)
    pace_std = round(float(merged["pace"].std()), 1)

    # First 20 games vs last 20 games
    first_20_pace = round(float(merged.head(20)["pace"].mean()), 1)
    last_20_pace = round(float(merged.tail(20)["pace"].mean()), 1)
    pace_change = round(last_20_pace - first_20_pace, 1)

    # Pre/post elimination
    elim_data = cache.load_computed(case_id, "elimination")
    elim_game = elim_data["data"].get("elimination_game_number") if elim_data else None

    pre_pace = None
    post_pace = None
    pace_shift = None

    if elim_game and elim_game < len(merged):
        pre = merged.iloc[:elim_game]
        post = merged.iloc[elim_game:]
        if not pre.empty and not post.empty:
            pre_pace = round(float(pre["pace"].mean()), 1)
            post_pace = round(float(post["pace"].mean()), 1)
            pace_shift = round(post_pace - pre_pace, 1)

    # Pace consistency: high variance = less structure
    pace_cv = round(pace_std / season_pace * 100, 1) if season_pace > 0 else 0

    # League context: get all teams' pace for the season
    league_pace_avg = None
    all_box = cache.load_df("box_scores_advanced", season=season)
    if not all_box.empty:
        league_pace_avg = round(float(all_box["pace"].mean()), 1)

    return {
        "season_avg_pace": season_pace,
        "pace_std": pace_std,
        "pace_cv": pace_cv,  # coefficient of variation (%)
        "first_20_pace": first_20_pace,
        "last_20_pace": last_20_pace,
        "pace_trajectory": pace_change,
        "pre_elim_pace": pre_pace,
        "post_elim_pace": post_pace,
        "pace_shift_at_elim": pace_shift,
        "league_avg_pace": league_pace_avg,
    }


# ── LOI: Lineup Overhaul Index ───────────────────────────────────────────────

def _compute_lineup_overhaul(case_id: str, team_id: int, season: str) -> dict:
    """Measure how much the roster churn changed post-trade-deadline and post-ASB.

    Excessive roster turnover at the deadline is a strong tanking signal — teams
    dealing veterans for picks/prospects. We track how many players appeared
    in games before vs after key dates.
    """
    from tii.config import ASB_DATES, TRADE_DEADLINES

    pgl = cache.load_df("player_game_logs", team_id=team_id, season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if pgl.empty or game_logs.empty:
        return {"error": "No player/game data"}

    game_logs = game_logs.sort_values("game_date")
    # pgl already has game_date, but use it from game_logs for consistency
    pgl_dates = pgl[["player_id", "player_name", "game_id", "minutes"]].merge(
        game_logs[["game_id", "game_date"]].drop_duplicates(),
        on="game_id", how="left",
    )
    pgl_with_date = pgl_dates

    trade_deadline = TRADE_DEADLINES.get(season)
    asb_date = ASB_DATES.get(season)

    result = {}

    # Pre/post trade deadline roster comparison
    if trade_deadline:
        pre_td = pgl_with_date[pgl_with_date["game_date"] < trade_deadline]
        post_td = pgl_with_date[pgl_with_date["game_date"] >= trade_deadline]

        if not pre_td.empty and not post_td.empty:
            pre_players = set(pre_td["player_id"].unique())
            post_players = set(post_td["player_id"].unique())

            departed = pre_players - post_players
            arrived = post_players - pre_players

            # Filter to meaningful players (at least 10 min/game in their period)
            pre_stats = pre_td.groupby("player_id")["minutes"].mean()
            post_stats = post_td.groupby("player_id")["minutes"].mean()

            meaningful_departed = [
                pid for pid in departed
                if pid in pre_stats.index and pre_stats[pid] >= 10
            ]
            meaningful_arrived = [
                pid for pid in arrived
                if pid in post_stats.index and post_stats[pid] >= 10
            ]

            # Get names for departed/arrived players
            departed_names = []
            for pid in meaningful_departed:
                name_row = pgl[pgl["player_id"] == pid].iloc[0]
                avg_min = round(float(pre_stats.get(pid, 0)), 1)
                departed_names.append({
                    "player_name": name_row["player_name"],
                    "avg_min_before": avg_min,
                })

            arrived_names = []
            for pid in meaningful_arrived:
                name_row = pgl[pgl["player_id"] == pid].iloc[0]
                avg_min = round(float(post_stats.get(pid, 0)), 1)
                arrived_names.append({
                    "player_name": name_row["player_name"],
                    "avg_min_after": avg_min,
                })

            result["trade_deadline"] = {
                "date": trade_deadline,
                "total_departed": len(departed),
                "meaningful_departed": len(meaningful_departed),
                "departed_players": departed_names,
                "total_arrived": len(arrived),
                "meaningful_arrived": len(meaningful_arrived),
                "arrived_players": arrived_names,
                "roster_churn": len(departed) + len(arrived),
            }

    # Total unique players: first 41 games vs last 41 games
    half = len(game_logs) // 2
    first_half_dates = game_logs.iloc[:half]["game_date"].tolist()
    second_half_dates = game_logs.iloc[half:]["game_date"].tolist()

    first_half_games = game_logs.iloc[:half]["game_id"].astype(str).tolist()
    second_half_games = game_logs.iloc[half:]["game_id"].astype(str).tolist()

    fh_players = pgl[pgl["game_id"].astype(str).isin(first_half_games)]["player_id"].nunique()
    sh_players = pgl[pgl["game_id"].astype(str).isin(second_half_games)]["player_id"].nunique()
    total_unique = pgl["player_id"].nunique()

    result["roster_churn_overall"] = {
        "total_unique_players": total_unique,
        "first_half_unique": fh_players,
        "second_half_unique": sh_players,
    }

    return result
