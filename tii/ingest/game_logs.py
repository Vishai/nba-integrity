"""Ingest team game logs for a season."""

import click
import pandas as pd
from nba_api.stats.endpoints import teamgamelog

from tii import cache, rate_limit


def ingest_team_game_logs(team_id: int, season: str, force: bool = False) -> pd.DataFrame:
    """Fetch and cache all games for a team-season.

    Returns DataFrame with columns: team_id, season, game_id, game_date,
    matchup, wl, w, l, pts, opp_pts, plus_minus, game_number.
    """
    if not force and cache.has_data("team_game_logs", team_id=team_id, season=season):
        click.echo(f"  [cached] team_game_logs for {team_id} / {season}")
        return cache.load_df("team_game_logs", team_id=team_id, season=season)

    click.echo(f"  [fetch] TeamGameLog team={team_id} season={season}")
    rate_limit.wait()
    result = teamgamelog.TeamGameLog(
        team_id=team_id,
        season=season,
        season_type_all_star="Regular Season",
    )
    df = result.get_data_frames()[0]

    if df.empty:
        click.echo(f"  [warn] No game logs returned for {team_id} / {season}")
        return df

    # Normalize columns — TeamGameLog does not include PLUS_MINUS or OPP_PTS
    out = pd.DataFrame({
        "team_id": team_id,
        "season": season,
        "game_id": df["Game_ID"].astype(str),
        "game_date": pd.to_datetime(df["GAME_DATE"], format="mixed").dt.strftime("%Y-%m-%d"),
        "matchup": df["MATCHUP"],
        "wl": df["WL"],
        "w": df["W"].astype(int),
        "l": df["L"].astype(int),
        "pts": df["PTS"].astype(int),
        "opp_pts": 0,  # filled from box scores later
        "plus_minus": 0.0,  # filled from box scores later
    })

    # Game logs come in reverse chronological order — sort ascending
    out = out.sort_values("game_date").reset_index(drop=True)
    out["game_number"] = range(1, len(out) + 1)

    cache.upsert_df("team_game_logs", out)
    click.echo(f"  [ok] {len(out)} games cached")
    return out
