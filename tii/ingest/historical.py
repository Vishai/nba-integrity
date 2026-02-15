"""Ingest historical standings for BTCA baseline (20 seasons)."""

import click

from tii import cache
from tii.ingest.standings import ingest_standings


# 20 seasons for historical baseline (2004-05 through 2023-24)
BASELINE_SEASONS = [
    "2004-05", "2005-06", "2006-07", "2007-08", "2008-09",
    "2009-10", "2010-11", "2011-12", "2012-13", "2013-14",
    "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
    "2019-20", "2020-21", "2021-22", "2022-23", "2023-24",
]


def ingest_historical_standings(force: bool = False):
    """Fetch standings for 20 historical seasons (for BTCA baseline).

    Only fetches seasons not already cached. Takes ~30s on first run.
    """
    click.echo(f"\nIngesting historical standings ({len(BASELINE_SEASONS)} seasons)...")
    fetched = 0
    for season in BASELINE_SEASONS:
        if not force and cache.has_data("standings_snapshots", season=season):
            continue
        ingest_standings(season, force=force)
        fetched += 1

    if fetched == 0:
        click.echo("  [cached] All historical standings already cached")
    else:
        click.echo(f"  [ok] Fetched {fetched} new seasons")
