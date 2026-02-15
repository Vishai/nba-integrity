"""Ingest team dashboard splits (pre/post ASB, monthly, etc.) with advanced stats."""

import click
import pandas as pd
from nba_api.stats.endpoints import teamdashboardbygeneralsplits

from tii import cache, rate_limit


def ingest_team_splits(team_id: int, season: str, force: bool = False) -> pd.DataFrame:
    """Fetch and cache pre/post ASB, monthly, and overall splits with net rating.

    Returns DataFrame with columns: team_id, season, split_type, gp, w, l,
    win_pct, plus_minus, off_rating, def_rating, net_rating.
    """
    if not force and cache.has_data("team_splits", team_id=team_id, season=season):
        click.echo(f"  [cached] team_splits for {team_id} / {season}")
        return cache.load_df("team_splits", team_id=team_id, season=season)

    click.echo(f"  [fetch] TeamDashboardByGeneralSplits (Advanced) team={team_id} season={season}")
    rate_limit.wait()
    result = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(
        team_id=team_id,
        season=season,
        season_type_all_star="Regular Season",
        measure_type_detailed_defense="Advanced",
    )
    dfs = result.get_data_frames()

    rows = []

    def _safe_float(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    # DataFrame 0: Overall
    if len(dfs) > 0 and not dfs[0].empty:
        r = dfs[0].iloc[0]
        rows.append({
            "split_type": "Overall",
            "gp": int(r["GP"]), "w": int(r["W"]), "l": int(r["L"]),
            "win_pct": _safe_float(r["W_PCT"]),
            "plus_minus": 0.0,
            "off_rating": _safe_float(r.get("OFF_RATING", 0)),
            "def_rating": _safe_float(r.get("DEF_RATING", 0)),
            "net_rating": _safe_float(r.get("NET_RATING", 0)),
        })

    # DataFrame 3: Monthly splits
    if len(dfs) > 3 and not dfs[3].empty:
        for _, r in dfs[3].iterrows():
            rows.append({
                "split_type": f"Month_{r['GROUP_VALUE']}",
                "gp": int(r["GP"]), "w": int(r["W"]), "l": int(r["L"]),
                "win_pct": _safe_float(r["W_PCT"]),
                "plus_minus": 0.0,
                "off_rating": _safe_float(r.get("OFF_RATING", 0)),
                "def_rating": _safe_float(r.get("DEF_RATING", 0)),
                "net_rating": _safe_float(r.get("NET_RATING", 0)),
            })

    # DataFrame 4: Pre/Post All-Star
    if len(dfs) > 4 and not dfs[4].empty:
        for _, r in dfs[4].iterrows():
            split_name = str(r["GROUP_VALUE"]).replace(" ", "")
            rows.append({
                "split_type": split_name,
                "gp": int(r["GP"]), "w": int(r["W"]), "l": int(r["L"]),
                "win_pct": _safe_float(r["W_PCT"]),
                "plus_minus": 0.0,
                "off_rating": _safe_float(r.get("OFF_RATING", 0)),
                "def_rating": _safe_float(r.get("DEF_RATING", 0)),
                "net_rating": _safe_float(r.get("NET_RATING", 0)),
            })

    if not rows:
        click.echo(f"  [warn] No splits data for {team_id} / {season}")
        return pd.DataFrame()

    out = pd.DataFrame(rows)
    out["team_id"] = team_id
    out["season"] = season

    cache.upsert_df("team_splits", out)
    click.echo(f"  [ok] {len(out)} splits cached")
    return out
