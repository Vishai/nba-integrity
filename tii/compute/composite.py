"""Compute composite TII score and classification."""

import numpy as np

from tii import cache
from tii.config import get_case, WEIGHTS, classify_tii


def _score_sas(data: dict) -> float:
    """Score SAS component (0-100, higher = more suspicious)."""
    score = 0.0

    summ = data.get("absence_summary", {})
    absence_rate = summ.get("absence_rate", 0)

    # Absence rate scoring (0-40 points)
    # 0-10% = 0, 10-25% = 0-15, 25-50% = 15-30, 50%+ = 30-40
    if absence_rate > 0.50:
        score += 30 + min((absence_rate - 0.50) * 100, 10)
    elif absence_rate > 0.25:
        score += 15 + (absence_rate - 0.25) * 60
    elif absence_rate > 0.10:
        score += (absence_rate - 0.10) * 100

    # Clustering ratio (0-30 points)
    clust = data.get("clustering", {})
    ratio = clust.get("cluster_ratio", 0)
    if ratio >= 3.0:
        score += 30
    elif ratio >= 2.0:
        score += 20 + (ratio - 2.0) * 10
    elif ratio >= 1.5:
        score += 10 + (ratio - 1.5) * 20
    elif ratio >= 1.0:
        score += (ratio - 1.0) * 20

    # Distribution skew (0-30 points)
    dist = data.get("distribution", {})
    loss_rate = dist.get("loss_absence_rate", 0)
    win_rate = dist.get("win_absence_rate", 0)
    if loss_rate > 0 and win_rate > 0:
        skew = loss_rate / win_rate if win_rate > 0 else 2.0
        if skew >= 2.0:
            score += 30
        elif skew >= 1.5:
            score += 15 + (skew - 1.5) * 30
        elif skew >= 1.0:
            score += (skew - 1.0) * 30

    return min(round(score, 1), 100)


def _score_nrci(data: dict) -> float:
    """Score NRCI component (0-100, higher = more suspicious)."""
    if data.get("error"):
        return 0.0

    score = 0.0

    # Rolling decline (0-35 points)
    rolling = data.get("rolling_net_rating", {})
    decline = rolling.get("max_decline", 0)
    if decline >= 15:
        score += 35
    elif decline >= 10:
        score += 20 + (decline - 10) * 3
    elif decline >= 5:
        score += 5 + (decline - 5) * 3

    # Pre/post elimination collapse (0-35 points)
    ppe = data.get("pre_post_elim", {})
    nr_change = ppe.get("net_rating_change", 0)
    if nr_change < -8:
        score += 35
    elif nr_change < -5:
        score += 20 + (abs(nr_change) - 5) * 5
    elif nr_change < -3:
        score += 10 + (abs(nr_change) - 3) * 5
    elif nr_change < 0:
        score += abs(nr_change) * 3.3

    # Close game win % (0-30 points)
    q4 = data.get("q4_performance", {})
    close_wp = q4.get("close_game_win_pct", 0.5)
    # Below .350 in close games is very suspicious
    if close_wp < 0.200:
        score += 30
    elif close_wp < 0.350:
        score += 15 + (0.350 - close_wp) * 100
    elif close_wp < 0.450:
        score += (0.450 - close_wp) * 150

    return min(round(score, 1), 100)


def _score_ris(data: dict) -> float:
    """Score RIS component (0-100, higher = more suspicious)."""
    if data.get("error"):
        return 0.0

    score = 0.0

    # Rotation disruption (0-35 points)
    changes = data.get("post_elim_changes", {})
    sig_decreases = changes.get("significant_decreases", 0)
    avg_change = changes.get("avg_minutes_change", 0)

    if sig_decreases >= 5:
        score += 35
    elif sig_decreases >= 3:
        score += 20 + (sig_decreases - 3) * 7.5
    elif sig_decreases >= 1:
        score += sig_decreases * 10

    # New rotation players (0-20 points)
    new_players = len(changes.get("new_rotation_players", []))
    score += min(new_players * 5, 20)

    # Minutes-quality correlation shift (0-25 points)
    corr = data.get("quality_correlation", {})
    corr_shift = corr.get("correlation_shift", 0)
    if corr_shift < -0.30:
        score += 25
    elif corr_shift < -0.15:
        score += 10 + (abs(corr_shift) - 0.15) * 100
    elif corr_shift < 0:
        score += abs(corr_shift) * 66.7

    # Experimentation increase (0-20 points)
    exp = data.get("experimentation", {})
    exp_increase = exp.get("experimentation_increase", 0)
    if exp_increase >= 2.0:
        score += 20
    elif exp_increase >= 1.0:
        score += 10 + (exp_increase - 1.0) * 10
    elif exp_increase > 0:
        score += exp_increase * 10

    return min(round(score, 1), 100)


def _score_btca(data: dict) -> float:
    """Score BTCA component (0-100, higher = more suspicious)."""
    if data.get("error"):
        return 0.0

    score = 0.0

    # League context / bottom-6 deviation (0-30 points)
    lc = data.get("league_context", {})
    deviation = abs(lc.get("deviation_from_baseline", 0))
    if deviation >= 2.0:
        score += 30
    elif deviation >= 1.0:
        score += 15 + (deviation - 1.0) * 15
    else:
        score += deviation * 15

    # Temporal pattern — post-ASB collapse (0-40 points)
    tp = data.get("temporal_pattern", {})
    pct_of_pre = tp.get("post_as_pct_of_pre", 100)
    if pct_of_pre < 30:
        score += 40
    elif pct_of_pre < 50:
        score += 25 + (50 - pct_of_pre) * 0.75
    elif pct_of_pre < 70:
        score += 10 + (70 - pct_of_pre) * 0.75
    elif pct_of_pre < 90:
        score += (90 - pct_of_pre) * 0.5

    # Calendar correlation — post-elimination win rate (0-30 points)
    cc = data.get("calendar_correlation", {})
    periods = cc.get("periods", {})
    post_elim = periods.get("Post-elimination", {})
    post_elim_wr = post_elim.get("win_rate", 0.5)

    if post_elim_wr < 0.100:
        score += 30
    elif post_elim_wr < 0.200:
        score += 20 + (0.200 - post_elim_wr) * 100
    elif post_elim_wr < 0.300:
        score += 10 + (0.300 - post_elim_wr) * 100
    elif post_elim_wr < 0.400:
        score += (0.400 - post_elim_wr) * 100

    return min(round(score, 1), 100)


def compute_composite(case_id: str) -> dict:
    """Compute weighted TII composite score and classification.

    Loads previously computed SAS, NRCI, RIS, BTCA data and scores each.
    """
    case = get_case(case_id)
    team_id = case["team_id"]
    season = case["season"]

    # Load all component data
    sas_data = cache.load_computed(case_id, "SAS")
    nrci_data = cache.load_computed(case_id, "NRCI")
    ris_data = cache.load_computed(case_id, "RIS")
    btca_data = cache.load_computed(case_id, "BTCA")

    components = {}

    # Score each component
    if sas_data:
        components["SAS"] = _score_sas(sas_data["data"])
    else:
        components["SAS"] = 0.0

    if nrci_data:
        components["NRCI"] = _score_nrci(nrci_data["data"])
    else:
        components["NRCI"] = 0.0

    if ris_data:
        components["RIS"] = _score_ris(ris_data["data"])
    else:
        components["RIS"] = 0.0

    if btca_data:
        components["BTCA"] = _score_btca(btca_data["data"])
    else:
        components["BTCA"] = 0.0

    # Weighted composite
    weighted = {}
    composite = 0.0
    for comp, raw_score in components.items():
        w = WEIGHTS[comp]
        ws = round(raw_score * w, 1)
        weighted[comp] = ws
        composite += ws

    composite = round(composite, 1)
    classification = classify_tii(composite)

    result = {
        "raw_scores": components,
        "weighted_scores": weighted,
        "composite_score": composite,
        "classification": classification,
        "expected_classification": case["expected_classification"],
        "match": classification in case["expected_classification"],
    }

    cache.store_computed(case_id, team_id, season, "composite", result, score=composite)
    return result
