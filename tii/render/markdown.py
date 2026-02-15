"""Render Appendix A markdown from cached/computed data."""

from pathlib import Path

import click
import pandas as pd

from tii import cache
from tii.config import CASES, get_case


APPENDIX_PATH = Path(__file__).parent.parent.parent / "NBA SRP Appendix A.md"
START_MARKER = "<!-- APPENDIX_A_AUTOGEN_START -->"
END_MARKER = "<!-- APPENDIX_A_AUTOGEN_END -->"


def _get_qualified_players(team_id: int, season: str, min_threshold: float = 25.0) -> pd.DataFrame:
    """Get players averaging min_threshold+ minutes per game."""
    pgl = cache.load_df("player_game_logs", team_id=team_id, season=season)
    if pgl.empty:
        return pd.DataFrame()

    summary = (
        pgl.groupby(["player_id", "player_name"])
        .agg(
            avg_minutes=("minutes", "mean"),
            games_played=("game_id", "count"),
            total_pts=("pts", "sum"),
        )
        .reset_index()
    )
    summary = summary.sort_values("avg_minutes", ascending=False)
    return summary[summary["avg_minutes"] >= min_threshold]


def _get_record(team_id: int, season: str) -> str:
    """Get final W-L record."""
    gl = cache.load_df("team_game_logs", team_id=team_id, season=season)
    if gl.empty:
        return "--"
    last = gl.sort_values("game_number").iloc[-1]
    return f"{int(last['w'])}-{int(last['l'])}"


def _get_elimination_info(case_id: str) -> dict:
    """Get elimination computation results."""
    result = cache.load_computed(case_id, "elimination")
    if result is None:
        return {}
    return result["data"]


def _ordinal(n: int) -> str:
    """Return ordinal string (1st, 2nd, 3rd, 4th, ...)."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _get_lottery_position(team_id: int, season: str) -> str:
    """Get lottery position (Xth-worst record) from standings."""
    standings = cache.load_df("standings_snapshots", season=season)
    if standings.empty:
        return "--"
    standings = standings.sort_values("wins", ascending=True).reset_index(drop=True)
    for idx, row in standings.iterrows():
        if int(row["team_id"]) == team_id:
            return _ordinal(idx + 1)
    return "--"


def _render_sas_section(case_id: str, team_id: int, season: str, total_games: int) -> str:
    """Render Component 1: Star Availability Score."""
    sas = cache.load_computed(case_id, "SAS")
    if sas is None:
        return "SAS not yet computed. Run `python tii.py compute --case {}`.\n".format(case_id)

    data = sas["data"]
    if data.get("error"):
        return f"SAS error: {data['error']}\n"

    lines = []

    # 1a. Qualified players table
    lines.append("**1a. Identify Qualified Players (25+ min/game)**\n")
    lines.append("|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|")
    lines.append("|---|---|---|---|---|---|---|")

    players = data.get("qualified_players", [])
    if players:
        for p in players:
            lines.append(
                f"|{p['player_name']}|{p['avg_minutes']}|{p['avg_pts']}|"
                f"{p['games_played']}|{p['games_missed']}|{p['dnp_count']}|{p['absent_from_log']}|"
            )
    else:
        lines.append("|No qualified players found||||||")

    lines.append("")

    # 1b. Absence summary
    summ = data.get("absence_summary", {})
    lines.append("**1b. Absence Summary**\n")
    lines.append(f"- Qualified players: {summ.get('num_qualified', '--')}")
    lines.append(f"- Total star-game absences: {summ.get('total_star_absences', '--')}")
    lines.append(f"- Total possible appearances: {summ.get('total_possible_appearances', '--')}")
    lines.append(f"- Absence rate: {summ.get('absence_rate', '--')}")
    lines.append("")

    # 1c. Clustering
    clust = data.get("clustering", {})
    if clust.get("note"):
        lines.append(f"**1c. Absence Clustering:** {clust['note']}\n")
    else:
        lines.append("**1c. Absence Clustering (Pre vs Post Elimination)**\n")
        lines.append("|Period|Games|Absences|Absence Rate|")
        lines.append("|---|---|---|---|")
        lines.append(
            f"|Pre-elimination|{clust.get('pre_elim_games', '--')}|"
            f"{clust.get('pre_elim_absences', '--')}|{clust.get('pre_elim_absence_rate', '--')}|"
        )
        lines.append(
            f"|Post-elimination|{clust.get('post_elim_games', '--')}|"
            f"{clust.get('post_elim_absences', '--')}|{clust.get('post_elim_absence_rate', '--')}|"
        )
        ratio = clust.get("cluster_ratio", 0)
        flag = "YES" if clust.get("flag") else "No"
        lines.append(f"\n- Cluster ratio (post/pre): **{ratio}x**")
        lines.append(f"- Flag (>=2.0x): **{flag}**")
    lines.append("")

    # 1d. Distribution by outcome
    dist = data.get("distribution", {})
    if dist:
        lines.append("**1d. Absence Distribution by Game Outcome**\n")
        lines.append("|Outcome|Team Games|Star Absences|Absence Rate|")
        lines.append("|---|---|---|---|")
        lines.append(
            f"|Wins|{dist.get('team_wins', '--')}|"
            f"{dist.get('absences_in_wins', '--')}|{dist.get('win_absence_rate', '--')}|"
        )
        lines.append(
            f"|Losses|{dist.get('team_losses', '--')}|"
            f"{dist.get('absences_in_losses', '--')}|{dist.get('loss_absence_rate', '--')}|"
        )
    lines.append("")

    # Show scored value if composite exists
    comp = cache.load_computed(case_id, "composite")
    if comp:
        raw = comp["data"].get("raw_scores", {}).get("SAS", "--")
        lines.append(f"**1e. SAS Component Score: {raw} / 100**\n")
    else:
        lines.append("**1e. SAS Component Score: -- / 100**\n")
    return "\n".join(lines)


def _render_btca_section(case_id: str) -> str:
    """Render Component 4: Bottom-Tier Clustering Analysis."""
    btca = cache.load_computed(case_id, "BTCA")
    if btca is None:
        return "BTCA not yet computed. Run `python tii.py compute --case {}`.\n".format(case_id)

    data = btca["data"]
    if data.get("error"):
        return f"BTCA error: {data['error']}\n"

    lines = []

    # 4a. League context
    lc = data.get("league_context", {})
    if lc:
        lines.append("**4a. League Context — Bottom-6 Analysis**\n")
        lines.append(f"- Team record: **{lc.get('team_record', '--')}**")
        lines.append(f"- Current bottom-6 avg wins: **{lc.get('current_bottom6_avg', '--')}**")
        lines.append(f"- Historical baseline (20 seasons): mean={lc.get('historical_avg', '--')}, "
                      f"σ={lc.get('historical_std', '--')}")
        lines.append(f"- Deviation from baseline: **{lc.get('deviation_from_baseline', '--')}σ**")
        lines.append(f"- Teams on pace for <22 wins: {lc.get('teams_under_22_wins', '--')}")
        flag = "YES" if lc.get("league_wide_flag") else "No"
        lines.append(f"- League-wide cluster flag (>=4 teams): **{flag}**")
        lines.append("")

        b6 = lc.get("bottom_6_teams", [])
        if b6:
            lines.append("|Rank|Team|Wins|")
            lines.append("|---|---|---|")
            for i, (name, wins) in enumerate(b6, 1):
                lines.append(f"|{i}|{name}|{wins}|")
            lines.append("")

    # 4b. Temporal pattern
    tp = data.get("temporal_pattern", {})
    if tp.get("error"):
        lines.append(f"**4b. Temporal Pattern:** {tp['error']}\n")
    elif tp:
        lines.append("**4b. Individual Team Temporal Pattern (Pre/Post ASB)**\n")
        lines.append("|Split|Record|Win%|Net Rating|")
        lines.append("|---|---|---|---|")
        lines.append(
            f"|Pre-ASB|{tp.get('pre_asb_record', '--')}|"
            f"{tp.get('pre_asb_win_pct', '--')}|{tp.get('pre_asb_net_rating', '--')}|"
        )
        lines.append(
            f"|Post-ASB|{tp.get('post_asb_record', '--')}|"
            f"{tp.get('post_asb_win_pct', '--')}|{tp.get('post_asb_net_rating', '--')}|"
        )
        lines.append(f"\n- Post-ASB as % of pre-ASB: **{tp.get('post_as_pct_of_pre', '--')}%**")
        flag = "YES" if tp.get("flag") else "No"
        lines.append(f"- Below 50% threshold flag: **{flag}**")
        lines.append("")

    # 4c. Calendar correlation
    cc = data.get("calendar_correlation", {})
    periods = cc.get("periods", {})
    if periods:
        lines.append("**4c. Calendar Correlation — Win Rates by Period**\n")
        lines.append("|Period|Games|Record|Win Rate|")
        lines.append("|---|---|---|---|")
        for period_name, pdata in periods.items():
            lines.append(
                f"|{period_name}|{pdata.get('games', '--')}|"
                f"{pdata.get('record', '--')}|{pdata.get('win_rate', '--')}|"
            )
        lines.append("")

        if cc.get("trade_deadline"):
            lines.append(f"- Trade deadline: {cc['trade_deadline']}")
        if cc.get("asb_date"):
            lines.append(f"- All-Star break: {cc['asb_date']}")
        if cc.get("elimination_date"):
            lines.append(f"- Elimination date: {cc['elimination_date']}")
        lines.append("")

    comp = cache.load_computed(case_id, "composite")
    if comp:
        raw = comp["data"].get("raw_scores", {}).get("BTCA", "--")
        lines.append(f"**4d. BTCA Component Score: {raw} / 100**\n")
    else:
        lines.append("**4d. BTCA Component Score: -- / 100**\n")
    return "\n".join(lines)


def _render_nrci_section(case_id: str) -> str:
    """Render Component 2: Net Rating Collapse Index."""
    nrci = cache.load_computed(case_id, "NRCI")
    if nrci is None:
        return "NRCI not yet computed. Run `python tii.py compute --case {}`.\n".format(case_id)

    data = nrci["data"]
    if data.get("error"):
        return f"NRCI error: {data['error']}\n"

    lines = []

    # 2a. Rolling net rating
    rolling = data.get("rolling_net_rating", {})
    if rolling:
        lines.append("**2a. Rolling 15-Game Net Rating**\n")
        lines.append(f"- Peak rolling net rating: **{rolling.get('peak_rolling', '--')}** (game {rolling.get('peak_game', '--')})")
        lines.append(f"- Trough rolling net rating: **{rolling.get('trough_rolling', '--')}** (game {rolling.get('trough_game', '--')})")
        lines.append(f"- Maximum decline (peak to trough): **{rolling.get('max_decline', '--')}**")
        lines.append(f"- Season-long net rating: {rolling.get('season_net_rating', '--')}")
        lines.append(f"- First 15 games net rating: {rolling.get('first_15_net_rating', '--')}")
        lines.append(f"- Last 15 games net rating: {rolling.get('last_15_net_rating', '--')}")
        lines.append("")

        snapshots = rolling.get("snapshots", [])
        if snapshots:
            lines.append("|Through Game #|Rolling Net Rating|")
            lines.append("|---|---|")
            for s in snapshots:
                lines.append(f"|{s.get('game_number', '--')}|{s.get('rolling_net_rating', '--')}|")
            lines.append("")

    # 2b. Close-game performance
    q4 = data.get("q4_performance", {})
    if q4:
        lines.append("**2b. Close-Game Performance (games within 8 pts net rating)**\n")
        lines.append(f"- Close games: {q4.get('close_games', '--')}")
        lines.append(f"- Close game record: {q4.get('close_wins', '--')}-{q4.get('close_losses', '--')}")
        lines.append(f"- Close game win %: **{q4.get('close_game_win_pct', '--')}**")
        lines.append(f"- Blowout losses: {q4.get('blowout_losses', '--')} ({q4.get('blowout_loss_pct', '--')})")
        lines.append("")

    # 2c. Pre/post elimination
    ppe = data.get("pre_post_elim", {})
    if ppe and not ppe.get("note"):
        lines.append("**2c. Pre/Post Elimination Net Rating**\n")
        lines.append("|Period|Games|Off Rating|Def Rating|Net Rating|")
        lines.append("|---|---|---|---|---|")
        lines.append(
            f"|Pre-elimination|{ppe.get('pre_elim_games', '--')}|"
            f"{ppe.get('pre_elim_off_rating', '--')}|{ppe.get('pre_elim_def_rating', '--')}|"
            f"{ppe.get('pre_elim_net_rating', '--')}|"
        )
        lines.append(
            f"|Post-elimination|{ppe.get('post_elim_games', '--')}|"
            f"{ppe.get('post_elim_off_rating', '--')}|{ppe.get('post_elim_def_rating', '--')}|"
            f"{ppe.get('post_elim_net_rating', '--')}|"
        )
        lines.append(f"\n- Net rating change: **{ppe.get('net_rating_change', '--')}**")
        flag = "YES" if ppe.get("collapse_flag") else "No"
        lines.append(f"- Collapse flag (change < -3.0): **{flag}**")
        lines.append("")
    elif ppe and ppe.get("note"):
        lines.append(f"**2c. Pre/Post Elimination:** {ppe['note']}\n")

    # 2d. Opponent-adjusted
    oa = data.get("opponent_adjusted", {})
    if oa:
        lines.append("**2d. Peer-Group Comparison (teams within +/-5 wins)**\n")
        lines.append(f"- Team net rating: {oa.get('team_net_rating', '--')}")
        lines.append(f"- Peer group avg net rating: {oa.get('peer_avg_net_rating', '--')}")
        lines.append(f"- Deviation from peers: **{oa.get('deviation', '--')}**")
        lines.append(f"- Peer group size: {oa.get('peer_count', '--')} teams")
        lines.append("")

    comp = cache.load_computed(case_id, "composite")
    if comp:
        raw = comp["data"].get("raw_scores", {}).get("NRCI", "--")
        lines.append(f"**2e. NRCI Component Score: {raw} / 100**\n")
    else:
        lines.append("**2e. NRCI Component Score: -- / 100**\n")
    return "\n".join(lines)


def _render_ris_section(case_id: str) -> str:
    """Render Component 3: Rotation Integrity Score."""
    ris = cache.load_computed(case_id, "RIS")
    if ris is None:
        return "RIS not yet computed. Run `python tii.py compute --case {}`.\n".format(case_id)

    data = ris["data"]
    if data.get("error"):
        return f"RIS error: {data['error']}\n"

    lines = []

    # 3a. Baseline rotation
    baseline = data.get("baseline_rotation", {})
    top8 = baseline.get("top_8", []) if isinstance(baseline, dict) else []
    if top8:
        lines.append("**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**\n")
        lines.append(f"Pre-elimination games: {baseline.get('pre_elim_games', '--')}\n")
        lines.append("|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|")
        lines.append("|---|---|---|---|---|")
        for p in top8:
            lines.append(
                f"|{p.get('player_name', '--')}|{p.get('pre_avg_minutes', '--')}|"
                f"{p.get('pre_games', '--')}|{p.get('pre_net_rating', '--')}|"
                f"{p.get('pre_usg', '--')}|"
            )
        lines.append("")

    # 3b. Post-elimination changes
    changes = data.get("post_elim_changes", {})
    if changes:
        lines.append("**3b. Post-Elimination Rotation Changes**\n")
        lines.append(f"- Post-elimination games: {changes.get('post_elim_games', '--')}")
        lines.append(f"- Significant minute decreases (>=20%): **{changes.get('significant_decreases', '--')}**")
        lines.append(f"- Average minutes change: {changes.get('avg_minutes_change', '--')}")
        flag = "YES" if changes.get("rotation_disruption_flag") else "No"
        lines.append(f"- Rotation disruption flag (>=3 sig decreases): **{flag}**")
        lines.append(f"- New rotation players: {len(changes.get('new_rotation_players', []))}")
        lines.append("")

        player_changes = changes.get("changes", [])
        if player_changes:
            lines.append("|Player|Pre Avg Min|Post Avg Min|Change|Change %|")
            lines.append("|---|---|---|---|---|")
            for pc in player_changes:
                lines.append(
                    f"|{pc.get('player_name', '--')}|{pc.get('pre_avg_min', '--')}|"
                    f"{pc.get('post_avg_min', '--')}|{pc.get('min_change', '--')}|{pc.get('pct_change', '--')}%|"
                )
            lines.append("")

        new_rot = changes.get("new_rotation_players", [])
        if new_rot:
            lines.append("**New rotation players post-elimination:**\n")
            for nr in new_rot:
                lines.append(f"- {nr.get('player_name', '--')} — {nr.get('post_avg_min', '--')} min/game ({nr.get('post_games', '--')} games)")
            lines.append("")

    # 3c. Quality correlation
    corr = data.get("quality_correlation", {})
    if corr:
        lines.append("**3c. Minutes-Quality Correlation Shift**\n")
        lines.append(f"- Pre-elimination correlation: {corr.get('pre_elim_corr', '--')}")
        lines.append(f"- Post-elimination correlation: {corr.get('post_elim_corr', '--')}")
        lines.append(f"- Correlation shift: **{corr.get('correlation_shift', '--')}**")
        note = corr.get("note", "")
        if note:
            lines.append(f"- Note: {note}")
        lines.append("")

    # 3d. Experimentation
    exp = data.get("experimentation", {})
    if exp:
        lines.append("**3d. Lineup Experimentation**\n")
        lines.append(f"- Pre-elimination unique players/game: {exp.get('pre_avg_players_per_game', '--')}")
        lines.append(f"- Post-elimination unique players/game: {exp.get('post_avg_players_per_game', '--')}")
        lines.append(f"- Experimentation increase: **{exp.get('experimentation_increase', '--')}**")
        lines.append("")

    comp = cache.load_computed(case_id, "composite")
    if comp:
        raw = comp["data"].get("raw_scores", {}).get("RIS", "--")
        lines.append(f"**3e. RIS Component Score: {raw} / 100**\n")
    else:
        lines.append("**3e. RIS Component Score: -- / 100**\n")
    return "\n".join(lines)


def _render_supplemental_section(case_id: str) -> str:
    """Render Supplemental Indicators section (DPI, VSI, MDP, LOI)."""
    supp = cache.load_computed(case_id, "supplemental")
    if supp is None:
        return "Supplemental indicators not yet computed. Run `python tii.py compute --case {}`.\n".format(case_id)

    data = supp["data"]
    lines = []

    # DPI: Draft Pick Incentive
    dpi = data.get("draft_pick_incentive", {})
    if dpi and not dpi.get("error"):
        lines.append("**5a. Draft Pick Incentive (DPI)**\n")
        lines.append(f"- Final record: {dpi.get('team_wins', '--')}-{dpi.get('team_losses', '--')}")
        lines.append(f"- Draft lottery position: **{_ordinal(dpi.get('draft_position', 0))}**-worst record")
        lines.append(f"- In bottom 3: {'Yes' if dpi.get('in_bottom_3') else 'No'}")
        lines.append(f"- In bottom 5: {'Yes' if dpi.get('in_bottom_5') else 'No'}")
        wg = dpi.get('wins_gap_to_next_better')
        lines.append(f"- Wins gap to next better draft slot: {wg if wg is not None else '--'}")
        lines.append(f"- Bottom-5 cluster size (teams within 3 wins): {dpi.get('bottom_5_cluster_size', '--')}")
        lines.append(f"- Wins needed to exit bottom 5: {dpi.get('wins_to_exit_bottom_5', '--')}")
        lines.append("")
    elif dpi and dpi.get("error"):
        lines.append(f"**5a. DPI:** {dpi['error']}\n")

    # VSI: Veteran Shelving
    vsi = data.get("veteran_shelving", {})
    if vsi and not vsi.get("error"):
        lines.append("**5b. Veteran Shelving Index (VSI)**\n")
        lines.append(f"- Total unique players used: {vsi.get('total_players_used', '--')}")
        lines.append(f"- Regular rotation size (40%+ games, 15+ min): {vsi.get('regular_rotation_size', '--')}")
        lines.append(f"- One-off players (<5 games): {vsi.get('one_off_players', '--')}")
        lines.append(f"- **Shelved post-elimination: {vsi.get('shelved_count', 0)}**")
        lines.append("")

        shelved = vsi.get("shelved_post_elim", [])
        if shelved:
            lines.append("|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|")
            lines.append("|---|---|---|---|---|---|")
            for sp in shelved:
                lines.append(
                    f"|{sp.get('player_name', '--')}|{sp.get('pre_avg_min', '--')}|"
                    f"{sp.get('post_avg_min', '--')}|{sp.get('pre_games', '--')}|"
                    f"{sp.get('post_games', '--')}|{sp.get('minutes_drop', '--')}|"
                )
            lines.append("")
    elif vsi and vsi.get("error"):
        lines.append(f"**5b. VSI:** {vsi['error']}\n")

    # MDP: Margin of Defeat Profile
    mdp = data.get("margin_profile", {})
    if mdp and not mdp.get("error"):
        lines.append("**5c. Margin of Defeat Profile (MDP)**\n")
        lines.append(f"- Total losses: {mdp.get('total_losses', '--')}")
        lines.append(f"- Average loss margin (net rating): {mdp.get('avg_loss_margin', '--')}")
        lines.append(f"- Blowout losses (NR < -15): {mdp.get('blowout_losses', '--')} ({mdp.get('blowout_loss_pct', '--')})")
        lines.append(f"- Competitive losses (NR > -5): {mdp.get('competitive_losses', '--')} ({mdp.get('competitive_loss_pct', '--')})")
        lines.append(f"- 1st-half season NR: {mdp.get('first_half_net_rating', '--')}")
        lines.append(f"- 2nd-half season NR: {mdp.get('second_half_net_rating', '--')}")
        lines.append(f"- **Trajectory (2nd half − 1st half): {mdp.get('trajectory', '--')}**")

        pre_m = mdp.get('pre_elim_avg_margin')
        post_m = mdp.get('post_elim_avg_margin')
        if pre_m is not None and post_m is not None:
            lines.append(f"- Pre-elimination avg NR: {pre_m}")
            lines.append(f"- Post-elimination avg NR: {post_m}")
            lines.append(f"- Post-elim margin change: **{round(post_m - pre_m, 1)}**")
        lines.append("")
    elif mdp and mdp.get("error"):
        lines.append(f"**5c. MDP:** {mdp['error']}\n")

    # LOI: Lineup Overhaul / Trade Deadline
    loi = data.get("lineup_overhaul", {})
    if loi and not loi.get("error"):
        td = loi.get("trade_deadline", {})
        if td:
            lines.append("**5d. Trade Deadline Roster Churn (LOI)**\n")
            lines.append(f"- Trade deadline date: {td.get('date', '--')}")
            lines.append(f"- Total players departed: {td.get('total_departed', '--')}")
            lines.append(f"- **Meaningful departures (10+ min/game): {td.get('meaningful_departed', 0)}**")
            lines.append(f"- Total players arrived: {td.get('total_arrived', '--')}")
            lines.append(f"- **Meaningful arrivals (10+ min/game): {td.get('meaningful_arrived', 0)}**")
            lines.append(f"- Total roster churn: {td.get('roster_churn', '--')}")
            lines.append("")

            departed = td.get("departed_players", [])
            if departed:
                lines.append("Key departures:\n")
                for dp in departed:
                    lines.append(f"- {dp['player_name']} ({dp['avg_min_before']} min/game pre-deadline)")
                lines.append("")

            arrived = td.get("arrived_players", [])
            if arrived:
                lines.append("Key arrivals:\n")
                for ap in arrived:
                    lines.append(f"- {ap['player_name']} ({ap['avg_min_after']} min/game post-deadline)")
                lines.append("")

        churn = loi.get("roster_churn_overall", {})
        if churn:
            lines.append(f"- Total unique players used (season): {churn.get('total_unique_players', '--')}")
            lines.append(f"- First-half unique players: {churn.get('first_half_unique', '--')}")
            lines.append(f"- Second-half unique players: {churn.get('second_half_unique', '--')}")
            lines.append("")
    elif loi and loi.get("error"):
        lines.append(f"**5d. LOI:** {loi['error']}\n")

    if not lines:
        lines.append("No supplemental data available.\n")

    return "\n".join(lines)


def _render_composite_table(case_id: str) -> str:
    """Render TII composite calculation table."""
    comp = cache.load_computed(case_id, "composite")
    if comp is None:
        return (
            "|Component|Raw Score|Weight|Weighted Score|\n"
            "|---|---|---|---|\n"
            "|SAS|-- /100|x 0.30|--|\n"
            "|NRCI|-- /100|x 0.25|--|\n"
            "|RIS|-- /100|x 0.25|--|\n"
            "|BTCA|-- /100|x 0.20|--|\n"
            "|**Composite TII**|||**-- / 100**|\n"
        )

    d = comp["data"]
    raw = d.get("raw_scores", {})
    weighted = d.get("weighted_scores", {})
    composite = d.get("composite_score", "--")
    classification = d.get("classification", "--")
    expected = d.get("expected_classification", "--")
    match = d.get("match", False)

    lines = []
    lines.append("|Component|Raw Score|Weight|Weighted Score|")
    lines.append("|---|---|---|---|")
    lines.append(f"|SAS|{raw.get('SAS', '--')} /100|x 0.30|{weighted.get('SAS', '--')}|")
    lines.append(f"|NRCI|{raw.get('NRCI', '--')} /100|x 0.25|{weighted.get('NRCI', '--')}|")
    lines.append(f"|RIS|{raw.get('RIS', '--')} /100|x 0.25|{weighted.get('RIS', '--')}|")
    lines.append(f"|BTCA|{raw.get('BTCA', '--')} /100|x 0.20|{weighted.get('BTCA', '--')}|")
    lines.append(f"|**Composite TII**|||**{composite} / 100**|")
    lines.append("")
    match_str = "MATCH" if match else "MISMATCH"
    lines.append(f"**Classification: {classification}** (Expected: {expected}) — **{match_str}**")
    lines.append("")
    return "\n".join(lines)


def render_case(case_id: str) -> str:
    """Render a single case study section."""
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    record = _get_record(team_id, season)
    elim = _get_elimination_info(case_id)
    lottery_pos = _get_lottery_position(team_id, season)

    # Count total games
    gl = cache.load_df("team_game_logs", team_id=team_id, season=season)
    total_games = len(gl) if not gl.empty else 0

    # Elimination string
    if elim.get("elimination_date"):
        elim_str = (
            f"{elim['elimination_date']} (game {elim['elimination_game_number']} of {total_games})"
        )
    elif elim.get("note"):
        elim_str = elim["note"]
    else:
        elim_str = "Not computed — run `python tii.py compute --case {}`".format(case_id)

    # Render component sections
    sas_section = _render_sas_section(case_id, team_id, season, total_games)
    nrci_section = _render_nrci_section(case_id)
    ris_section = _render_ris_section(case_id)
    btca_section = _render_btca_section(case_id)
    supplemental_section = _render_supplemental_section(case_id)
    composite_table = _render_composite_table(case_id)

    md = f"""### CASE {case_id}: {case['team_name']} — {season}

**Archetype:** {case['archetype']}
**Expected Classification:** {case['expected_classification']}
**Final Record:** {record}
**Lottery Position:** {lottery_pos}-worst record
**Computed Elimination Date:** {elim_str}

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

{sas_section}

---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

{nrci_section}

---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

{ris_section}

---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

{btca_section}

---

#### Supplemental Indicators (contextual — not scored)

{supplemental_section}

---

#### TII Composite Calculation

{composite_table}

"""
    return md


def render_all_cases() -> str:
    """Render all active case studies."""
    sections = ["# Autogenerated Case Data (MVP)\n"]
    for cid, c in CASES.items():
        if c.get("skip"):
            sections.append(f"### CASE {cid}: {c['team_name']} — {c['season']}\n")
            sections.append(f"**Status:** Deferred — {c.get('note', 'future season')}\n")
            continue
        try:
            sections.append(render_case(cid))
        except Exception as e:
            sections.append(f"### CASE {cid}: {c['team_name']} — {c['season']}\n")
            sections.append(f"**Status:** Error — {e}\n")
    return "\n".join(sections)


def inject_into_appendix():
    """Replace content between AUTOGEN markers in the Appendix A file."""
    if not APPENDIX_PATH.exists():
        click.echo(f"Error: {APPENDIX_PATH} not found")
        raise SystemExit(1)

    content = APPENDIX_PATH.read_text()
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)

    if start_idx == -1 or end_idx == -1:
        click.echo("Error: APPENDIX_A_AUTOGEN markers not found in file")
        raise SystemExit(1)

    new_content = render_all_cases()

    updated = (
        content[:start_idx + len(START_MARKER)]
        + "\n\n"
        + new_content
        + "\n\n"
        + content[end_idx:]
    )

    APPENDIX_PATH.write_text(updated)
    click.echo(f"Injected into {APPENDIX_PATH}")
