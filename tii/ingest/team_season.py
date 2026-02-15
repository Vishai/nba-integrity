"""Orchestrator: ingest all data for a team-season case."""

import click

from tii.config import get_case
from tii.ingest.game_logs import ingest_team_game_logs
from tii.ingest.standings import ingest_standings
from tii.ingest.player_stats import ingest_player_game_logs
from tii.ingest.splits import ingest_team_splits
from tii.ingest.box_scores import ingest_box_scores


def ingest_case(case_id: str, force: bool = False):
    """Run all ingestion steps for a case study."""
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    click.echo(f"\n{'='*60}")
    click.echo(f"INGEST Case {case_id}: {case['team_name']} — {season}")
    click.echo(f"{'='*60}")

    # 1. League standings (needed for elimination computation + BTCA)
    click.echo(f"\n[1/5] League Standings")
    ingest_standings(season, force=force)

    # 2. Team game logs
    click.echo(f"\n[2/5] Team Game Logs")
    ingest_team_game_logs(team_id, season, force=force)

    # 3. Player game logs
    click.echo(f"\n[3/5] Player Game Logs")
    ingest_player_game_logs(team_id, season, force=force)

    # 4. Team splits (pre/post ASB, monthly, advanced stats)
    click.echo(f"\n[4/5] Team Splits (Advanced)")
    ingest_team_splits(team_id, season, force=force)

    # 5. Advanced box scores (per-game, ~82 API calls)
    click.echo(f"\n[5/5] Advanced Box Scores")
    ingest_box_scores(team_id, season, force=force)

    click.echo(f"\n{'='*60}")
    click.echo(f"INGEST Case {case_id} complete.")
    click.echo(f"{'='*60}\n")
