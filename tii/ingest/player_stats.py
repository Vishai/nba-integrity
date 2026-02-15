"""Ingest player game logs for a team-season."""

import click
import pandas as pd
from nba_api.stats.endpoints import playergamelogs

from tii import cache, rate_limit


def ingest_player_game_logs(team_id: int, season: str, force: bool = False) -> pd.DataFrame:
    """Fetch and cache per-game player stats for everyone on a team-season.

    Returns DataFrame with columns: player_id, player_name, team_id, season,
    game_id, game_date, matchup, wl, minutes, pts, reb, ast, plus_minus.
    """
    if not force and cache.has_data("player_game_logs", team_id=team_id, season=season):
        click.echo(f"  [cached] player_game_logs for {team_id} / {season}")
        return cache.load_df("player_game_logs", team_id=team_id, season=season)

    click.echo(f"  [fetch] PlayerGameLogs team={team_id} season={season}")
    rate_limit.wait()
    result = playergamelogs.PlayerGameLogs(
        team_id_nullable=team_id,
        season_nullable=season,
        season_type_nullable="Regular Season",
    )
    df = result.get_data_frames()[0]

    if df.empty:
        click.echo(f"  [warn] No player game logs returned for {team_id} / {season}")
        return df

    def parse_minutes(min_str):
        """Convert 'MM:SS' or numeric minutes to float."""
        if pd.isna(min_str) or min_str == "" or min_str is None:
            return 0.0
        s = str(min_str)
        if ":" in s:
            parts = s.split(":")
            return float(parts[0]) + float(parts[1]) / 60.0
        return float(s)

    out = pd.DataFrame({
        "player_id": df["PLAYER_ID"].astype(int),
        "player_name": df["PLAYER_NAME"],
        "team_id": team_id,
        "season": season,
        "game_id": df["GAME_ID"].astype(str),
        "game_date": pd.to_datetime(df["GAME_DATE"]).dt.strftime("%Y-%m-%d"),
        "matchup": df["MATCHUP"],
        "wl": df["WL"],
        "minutes": df["MIN"].apply(parse_minutes),
        "pts": df["PTS"].fillna(0).astype(int),
        "reb": df["REB"].fillna(0).astype(int),
        "ast": df["AST"].fillna(0).astype(int),
        "plus_minus": df["PLUS_MINUS"].fillna(0).astype(float),
    })

    cache.upsert_df("player_game_logs", out)
    click.echo(f"  [ok] {len(out)} player-game rows cached ({out['player_id'].nunique()} players)")
    return out
