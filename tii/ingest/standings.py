"""Ingest league standings for a season."""

import click
import pandas as pd
from nba_api.stats.endpoints import leaguestandings

from tii import cache, rate_limit


def ingest_standings(season: str, force: bool = False) -> pd.DataFrame:
    """Fetch and cache end-of-season standings for all 30 teams.

    Returns DataFrame with columns: season, team_id, team_name, conference,
    wins, losses, win_pct, league_rank.
    """
    if not force and cache.has_data("standings_snapshots", season=season):
        click.echo(f"  [cached] standings for {season}")
        return cache.load_df("standings_snapshots", season=season)

    click.echo(f"  [fetch] LeagueStandings season={season}")
    rate_limit.wait()
    result = leaguestandings.LeagueStandings(
        season=season,
        season_type="Regular Season",
    )
    df = result.get_data_frames()[0]

    if df.empty:
        click.echo(f"  [warn] No standings returned for {season}")
        return df

    out = pd.DataFrame({
        "season": season,
        "team_id": df["TeamID"].astype(int),
        "team_name": df["TeamName"],
        "conference": df["Conference"],
        "wins": df["WINS"].astype(int),
        "losses": df["LOSSES"].astype(int),
        "win_pct": df["WinPCT"].astype(float),
        "league_rank": pd.to_numeric(df["LeagueRank"], errors="coerce").fillna(0).astype(int),
    })

    cache.upsert_df("standings_snapshots", out)
    click.echo(f"  [ok] {len(out)} teams' standings cached")
    return out
