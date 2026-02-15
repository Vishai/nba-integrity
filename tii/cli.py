"""CLI interface for TII backtesting tool."""

import click

from tii.config import get_all_cases, get_case
from tii.cases_store import add_dynamic_case, append_activity
from tii.activity import summarize_activity, tail_events


@click.group()
def cli():
    """TII Backtesting Tool — Tanking Integrity Index historical data collection."""
    pass


@cli.command("list")
def list_cases():
    """Show all configured case studies (built-in + dynamic)."""
    click.echo(
        f"\n{'Case':<18}{'Team':<30}{'Season':<12}{'Archetype':<35}{'Expected':<12}{'Added by'}"
    )
    click.echo("-" * 120)
    for cid, c in get_all_cases().items():
        added_by = c.get("added_by", "")
        if c.get("skip"):
            status = f"(deferred: {c.get('note', '')})"
            click.echo(
                f"{cid:<18}{c['team_name']:<30}{c['season']:<12}{c['archetype']:<35}{status:<12}{added_by}"
            )
        else:
            click.echo(
                f"{cid:<18}{c['team_name']:<30}{c['season']:<12}"
                f"{c['archetype']:<35}{c['expected_classification']:<12}{added_by}"
            )
    click.echo()


@cli.command()
@click.option("--case", "case_id", help="Case id (e.g. A or UTA-2024-25)")
@click.option("--team", help="Team abbreviation or name (e.g. UTA or 'Utah Jazz')")
@click.option("--season", help="Season string like '2024-25'")
@click.option("--added-by", help="Name/email of the person adding this case")
@click.option("--all", "all_cases", is_flag=True, help="Ingest all active cases")
@click.option("--force", is_flag=True, help="Re-fetch even if cached")
@click.option("--delay", type=float, default=1.5, help="Rate limit delay in seconds")
def ingest(case_id, team, season, added_by, all_cases, force, delay):
    """Fetch and cache raw data for a team-season."""
    from tii import rate_limit
    from tii.ingest.team_season import ingest_case

    rate_limit.set_delay(delay)

    if all_cases:
        for cid, c in get_all_cases().items():
            if not c.get("skip"):
                ingest_case(cid, force=force)
        return

    if team and season:
        from tii.team_lookup import lookup_team

        t = lookup_team(team)
        cid = add_dynamic_case(
            team_abbr=t["abbreviation"],
            team_id=t["id"],
            team_name=t["full_name"],
            season=season,
            added_by=added_by,
        )
        append_activity(
            {
                "event": "ingest_requested",
                "case_id": cid,
                "team_abbr": t["abbreviation"],
                "team_id": t["id"],
                "season": season,
                "added_by": added_by,
            }
        )
        ingest_case(cid, force=force)
        return

    if case_id:
        ingest_case(case_id.upper(), force=force)
        return

    click.echo("Error: provide --case ID, or --team TEAM --season SEASON, or --all")
    raise SystemExit(1)


@cli.command()
@click.option("--case", "case_id", help="Case id (e.g. A or UTA-2024-25)")
@click.option("--team", help="Team abbreviation or name (e.g. UTA or 'Utah Jazz')")
@click.option("--season", help="Season string like '2024-25'")
@click.option("--added-by", help="Name/email of the person adding this case")
@click.option("--all", "all_cases", is_flag=True, help="Compute all active cases")
def compute(case_id, team, season, added_by, all_cases):
    """Derive TII component metrics from cached data."""
    from tii.compute.elimination import compute_elimination_date
    from tii.compute.btca import compute_btca
    from tii.compute.sas import compute_sas
    from tii.compute.nrci import compute_nrci
    from tii.compute.ris import compute_ris
    from tii.compute.composite import compute_composite
    from tii.compute.supplemental import compute_supplemental
    from tii.ingest.historical import ingest_historical_standings

    # Ensure historical standings are available for BTCA
    ingest_historical_standings()

    def run_case(cid):
        case = get_case(cid)
        click.echo(f"\nComputing Case {cid}: {case['team_name']} — {case['season']}")

        # 1. Elimination date (needed by everything)
        elim = compute_elimination_date(cid)
        if elim.get("elimination_date"):
            click.echo(
                f"  Eliminated: {elim['elimination_date']} "
                f"(game {elim['elimination_game_number']})"
            )
        else:
            click.echo(f"  Not eliminated — {elim.get('note', 'see data')}")

        # 2. SAS
        sas = compute_sas(cid)
        if sas.get("error"):
            click.echo(f"  SAS error: {sas['error']}")
        else:
            summ = sas.get("absence_summary", {})
            click.echo(
                f"  SAS: {summ.get('num_qualified', 0)} qualified, "
                f"absence rate={summ.get('absence_rate', 0)}"
            )

        # 3. NRCI
        nrci = compute_nrci(cid)
        if nrci.get("error"):
            click.echo(f"  NRCI error: {nrci['error']}")
        else:
            rolling = nrci.get("rolling_net_rating", {})
            ppe = nrci.get("pre_post_elim", {})
            click.echo(
                f"  NRCI: season NR={rolling.get('season_net_rating', '--')}, "
                f"max decline={rolling.get('max_decline', '--')}, "
                f"post-elim change={ppe.get('net_rating_change', '--')}"
            )

        # 4. RIS
        ris = compute_ris(cid)
        if ris.get("error"):
            click.echo(f"  RIS error: {ris['error']}")
        else:
            changes = ris.get("post_elim_changes", {})
            corr = ris.get("quality_correlation", {})
            click.echo(
                f"  RIS: {changes.get('significant_decreases', 0)} sig decreases, "
                f"corr shift={corr.get('correlation_shift', '--')}"
            )

        # 5. BTCA
        btca = compute_btca(cid)
        if btca.get("error"):
            click.echo(f"  BTCA error: {btca['error']}")
        else:
            lc = btca.get("league_context", {})
            click.echo(
                f"  BTCA: bottom-6 avg={lc.get('current_bottom6_avg', '--')} "
                f"(hist={lc.get('historical_avg', '--')})"
            )

        # 6. Supplemental indicators
        supp = compute_supplemental(cid)
        dpi = supp.get("draft_pick_incentive", {})
        vsi = supp.get("veteran_shelving", {})
        click.echo(
            f"  Supplemental: draft pos={dpi.get('draft_position', '--')}, "
            f"shelved vets={vsi.get('shelved_count', 0)}"
        )

        # 7. Composite TII
        comp = compute_composite(cid)
        click.echo(
            f"  === TII: {comp['composite_score']} / 100 → "
            f"{comp['classification']} "
            f"(expected: {comp['expected_classification']})"
        )

    if all_cases:
        for cid, c in get_all_cases().items():
            if not c.get("skip"):
                run_case(cid)
        return

    if team and season:
        from tii.team_lookup import lookup_team

        t = lookup_team(team)
        cid = add_dynamic_case(
            team_abbr=t["abbreviation"],
            team_id=t["id"],
            team_name=t["full_name"],
            season=season,
            added_by=added_by,
        )
        append_activity(
            {
                "event": "compute_requested",
                "case_id": cid,
                "team_abbr": t["abbreviation"],
                "team_id": t["id"],
                "season": season,
                "added_by": added_by,
            }
        )
        run_case(cid)
        return

    if case_id:
        run_case(case_id.upper())
        return

    click.echo("Error: provide --case ID, or --team TEAM --season SEASON, or --all")
    raise SystemExit(1)


@cli.command()
def status():
    """Show ingestion and computation status for each case."""
    from tii import cache

    click.echo(f"\n{'Case':<6}{'Team':<8}{'Season':<12}{'Games':<8}{'BoxSc':<8}"
               f"{'Splits':<8}{'Elim':<14}{'TII':<10}{'Class'}")
    click.echo("-" * 90)

    for cid, c in get_all_cases().items():
        if c.get("skip"):
            click.echo(f"{cid:<6}{'--':<8}{c['season']:<12}{'--':<8}"
                        f"{'--':<8}{'--':<8}{'--':<14}{'--':<10}{'--'}")
            continue

        team_id = c["team_id"]
        season = c["season"]

        games = cache.count_rows("team_game_logs", team_id=team_id, season=season)
        box_scores = cache.count_rows("box_scores_advanced", team_id=team_id, season=season)
        splits = cache.count_rows("team_splits", team_id=team_id, season=season)

        elim = cache.load_computed(cid, "elimination")
        elim_str = "--"
        if elim:
            d = elim["data"]
            if d.get("elimination_date"):
                elim_str = d["elimination_date"]
            else:
                elim_str = "not elim"

        comp = cache.load_computed(cid, "composite")
        tii_str = "--"
        class_str = "--"
        if comp:
            tii_str = str(comp["data"].get("composite_score", "--"))
            class_str = comp["data"].get("classification", "--")

        click.echo(
            f"{cid:<6}{c['team_abbr']:<8}{season:<12}"
            f"{games if games > 0 else '--':<8}{box_scores if box_scores > 0 else '--':<8}"
            f"{splits if splits > 0 else '--':<8}{elim_str:<14}"
            f"{tii_str:<10}{class_str}"
        )
    click.echo()


@cli.command()
@click.option("--case", "case_id", help="Case id (e.g. A or UTA-2024-25)")
@click.option("--all", "all_cases", is_flag=True, help="Render all active cases")
@click.option("--output", "output_path", type=click.Path(), help="Output file path")
@click.option("--inject", is_flag=True, help="Write into APPENDIX_A_AUTOGEN markers")
def render(case_id, all_cases, output_path, inject):
    """Generate filled Appendix A markdown from computed data."""
    from tii.render.markdown import render_case, render_all_cases, inject_into_appendix

    if inject:
        inject_into_appendix()
    elif all_cases:
        md = render_all_cases()
        if output_path:
            with open(output_path, "w") as f:
                f.write(md)
            click.echo(f"Written to {output_path}")
        else:
            click.echo(md)
    elif case_id:
        md = render_case(case_id.upper())
        if output_path:
            with open(output_path, "w") as f:
                f.write(md)
            click.echo(f"Written to {output_path}")
        else:
            click.echo(md)
    else:
        click.echo("Error: provide --case ID, --all, or --inject")
        raise SystemExit(1)


@cli.command("activity")
@click.option("--tail", "tail_n", type=int, default=25, help="Show last N events")
def activity_cmd(tail_n: int):
    """Show activity summary (who added/ran what) + recent events."""

    summary = summarize_activity()

    click.echo(f"\nTotal events: {summary['total']}")
    click.echo("\nBy event:")
    for k, v in summary["by_event"]:
        click.echo(f"  {k}: {v}")

    click.echo("\nBy user:")
    for k, v in summary["by_user"]:
        click.echo(f"  {k}: {v}")

    click.echo("\nTop cases:")
    for k, v in summary["by_case"]:
        click.echo(f"  {k}: {v}")

    click.echo(f"\nLast {tail_n} events:")
    for ev in tail_events(tail_n):
        click.echo(
            f"  {ev.get('ts','')} {ev.get('event','')} case={ev.get('case_id','')} user={ev.get('added_by','')}"
        )


if __name__ == "__main__":
    cli()
