"""Ingest per-game advanced box scores (team + player level)."""

import click
import pandas as pd
from nba_api.stats.endpoints import boxscoreadvancedv3

from tii import cache, rate_limit


def ingest_box_scores(team_id: int, season: str, force: bool = False) -> int:
    """Fetch advanced box scores for every game in a team-season.

    Requires team_game_logs to be ingested first (for game IDs).
    Returns number of games fetched.
    """
    # Check if already done
    existing = cache.count_rows("box_scores_advanced", team_id=team_id, season=season)
    game_logs = cache.load_df("team_game_logs", team_id=team_id, season=season)

    if game_logs.empty:
        click.echo(f"  [skip] No game logs for {team_id}/{season} — run ingest first")
        return 0

    total_games = len(game_logs)

    if not force and existing >= total_games:
        click.echo(f"  [cached] box_scores for {team_id}/{season} ({existing} games)")
        return 0

    # Get list of game IDs to fetch
    game_ids = game_logs["game_id"].astype(str).tolist()

    # Check which games we already have
    if not force:
        conn = cache._get_conn()
        cur = conn.execute(
            "SELECT game_id FROM box_scores_advanced WHERE team_id = ? AND season = ?",
            (team_id, season),
        )
        existing_games = {row[0] for row in cur.fetchall()}
        conn.close()
        game_ids = [gid for gid in game_ids if gid not in existing_games]

    if not game_ids:
        click.echo(f"  [cached] box_scores complete for {team_id}/{season}")
        return 0

    click.echo(f"  [fetch] {len(game_ids)} box scores for {team_id}/{season}")
    fetched = 0
    errors = 0

    for i, game_id in enumerate(game_ids):
        try:
            rate_limit.wait()
            result = boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game_id)

            team_df = result.team_stats.get_data_frame()
            player_df = result.player_stats.get_data_frame()

            # Team-level advanced stats
            team_row = team_df[team_df["teamId"] == team_id]
            if not team_row.empty:
                r = team_row.iloc[0]
                team_data = pd.DataFrame([{
                    "game_id": game_id,
                    "team_id": team_id,
                    "season": season,
                    "off_rating": _safe_float(r.get("offensiveRating", 0)),
                    "def_rating": _safe_float(r.get("defensiveRating", 0)),
                    "net_rating": _safe_float(r.get("netRating", 0)),
                    "pace": _safe_float(r.get("pace", 0)),
                    "ts_pct": _safe_float(r.get("trueShootingPercentage", 0)),
                }])
                cache.upsert_df("box_scores_advanced", team_data)

            # Player-level advanced stats (only our team's players)
            our_players = player_df[player_df["teamId"] == team_id]
            if not our_players.empty:
                player_rows = []
                for _, p in our_players.iterrows():
                    player_rows.append({
                        "game_id": game_id,
                        "team_id": team_id,
                        "player_id": int(p["personId"]),
                        "player_name": f"{p.get('firstName', '')} {p.get('familyName', '')}".strip(),
                        "season": season,
                        "minutes": _parse_minutes(p.get("minutes", 0)),
                        "off_rating": _safe_float(p.get("offensiveRating", 0)),
                        "def_rating": _safe_float(p.get("defensiveRating", 0)),
                        "net_rating": _safe_float(p.get("netRating", 0)),
                        "usg_pct": _safe_float(p.get("usagePercentage", 0)),
                        "ts_pct": _safe_float(p.get("trueShootingPercentage", 0)),
                    })
                if player_rows:
                    cache.upsert_df("box_scores_advanced_players", pd.DataFrame(player_rows))

            fetched += 1

        except Exception as e:
            errors += 1
            if errors <= 3:
                click.echo(f"    [err] game {game_id}: {e}")

        # Progress every 20 games
        if (i + 1) % 20 == 0:
            click.echo(f"    ... {i + 1}/{len(game_ids)} games processed")

    click.echo(f"  [ok] {fetched} box scores cached ({errors} errors)")
    return fetched


def _safe_float(val) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _parse_minutes(val) -> float:
    """Parse minutes from various formats (PT02M30.00S ISO format or float)."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    # V3 uses ISO 8601 duration format: PT30M12.00S
    if s.startswith("PT"):
        try:
            s = s[2:]  # Remove "PT"
            minutes = 0.0
            if "M" in s:
                m_part, s = s.split("M")
                minutes += float(m_part)
            if "S" in s:
                s_part = s.replace("S", "")
                if s_part:
                    minutes += float(s_part) / 60.0
            return round(minutes, 2)
        except (ValueError, IndexError):
            return 0.0
    if ":" in s:
        parts = s.split(":")
        try:
            return float(parts[0]) + float(parts[1]) / 60.0
        except (ValueError, IndexError):
            return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0
