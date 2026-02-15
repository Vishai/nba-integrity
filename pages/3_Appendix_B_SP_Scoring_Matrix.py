"""Appendix B — Stewardship Points Detailed Scoring Matrix.

Derives SP (reward) scoring from TII (detection) data. Shows what each
backtesting case would earn under the SP system — the inverse of TII.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from tii.config import CASES

st.set_page_config(page_title="Appendix B — SP Scoring Matrix", page_icon="⭐", layout="wide")

COMPUTED_DIR = Path(__file__).resolve().parent.parent / "data" / "computed"

# ── SP Category definitions from SRP Section III ────────────────────────
SP_CATEGORIES = {
    "Star Availability Compliance": {
        "weight": 0.25,
        "max_points": 25,
        "description": "Teams earn SP for making their best players genuinely available.",
        "tii_inverse": "SAS",
        "scoring": """
| SP Earned | Condition |
|-----------|-----------|
| 25 (max)  | Absence rate below league average, no clustering, no loss/win skew |
| 20        | Absence rate slightly above average but no suspicious patterns |
| 15        | Moderate absences, minor clustering (cluster ratio < 1.5x) |
| 10        | Elevated absences OR moderate clustering |
| 5         | High absences with some clustering |
| 0         | Severe absences with clear clustering and loss/win skew |
""",
    },
    "Net Rating Integrity": {
        "weight": 0.20,
        "max_points": 20,
        "description": "Teams earn SP for maintaining competitive performance throughout the season.",
        "tii_inverse": "NRCI",
        "scoring": """
| SP Earned | Condition |
|-----------|-----------|
| 20 (max)  | No significant performance decline; close-game win% above .400 |
| 15        | Mild post-elimination decline (< 3 pts NR change) |
| 10        | Moderate decline but still competitive in close games |
| 5         | Significant decline but explainable by roster changes |
| 0         | Severe unexplained collapse, especially in close games |
""",
    },
    "Rotation Consistency": {
        "weight": 0.20,
        "max_points": 20,
        "description": "Teams earn SP for maintaining consistent rotation patterns throughout the season.",
        "tii_inverse": "RIS",
        "scoring": """
| SP Earned | Condition |
|-----------|-----------|
| 20 (max)  | Rotation patterns stable pre- and post-elimination; merit correlation maintained |
| 15        | Minor rotation changes (1-2 players), correlation shift > -0.10 |
| 10        | Moderate changes (3 players), some new rotation players |
| 5         | Significant rotation overhaul but correlation still positive |
| 0         | Wholesale rotation inversion; merit correlation goes negative |
""",
    },
    "Competitive Engagement": {
        "weight": 0.15,
        "max_points": 15,
        "description": "Teams eliminated from playoff contention earn SP for maintaining competitive effort.",
        "tii_inverse": "BTCA",
        "scoring": """
| SP Earned | Condition |
|-----------|-----------|
| 15 (max)  | Post-elimination win rate within 80% of pre-elimination rate |
| 12        | Post-elim win rate within 60% of pre-elimination rate |
| 8         | Some post-ASB decline but not calendar-correlated |
| 4         | Clear post-ASB/post-elim collapse |
| 0         | Dramatic calendar-correlated losing pattern |
""",
    },
    "Homegrown Retention": {
        "weight": 0.20,
        "max_points": 20,
        "description": "Teams earn SP for retaining and developing draft picks and homegrown talent.",
        "tii_inverse": None,
        "scoring": """
| SP Earned | Condition |
|-----------|-----------|
| 20 (max)  | Extended 3+ homegrown players in the past 3 years |
| 15        | Extended 2 homegrown players; drafted players in rotation |
| 10        | Extended 1 homegrown player; active development program |
| 5         | No recent extensions but drafted players contribute |
| 0         | No homegrown player retention pattern |

*Note: This category is not directly measurable from TII backtesting data.
The estimates below use a placeholder based on known roster context.*
""",
    },
}


@st.cache_data
def load_all_case_data():
    out = {}
    for cid, cfg in CASES.items():
        if cfg.get("skip"):
            continue
        json_path = COMPUTED_DIR / f"case_{cid}.json"
        if not json_path.exists():
            continue
        metrics = json.loads(json_path.read_text())
        out[cid] = {
            "case_id": cid,
            "team": cfg["team_name"],
            "season": cfg["season"],
            "archetype": cfg["archetype"],
            "expected": cfg["expected_classification"],
            **{m: metrics.get(m, {}) for m in ("SAS", "NRCI", "RIS", "BTCA", "supplemental")},
        }
    return out


def compute_sp_from_tii(case_data):
    """Derive SP category scores from TII component data (inverse relationship)."""
    sp = {}

    # Star Availability Compliance (inverse of SAS)
    sas = case_data.get("SAS", {})
    ar = sas.get("absence_summary", {}).get("absence_rate", 0)
    cr = sas.get("clustering", {}).get("cluster_ratio", 0)
    if ar < 0.10 and cr < 1.5:
        sp["Star Availability Compliance"] = 25
    elif ar < 0.20 and cr < 1.5:
        sp["Star Availability Compliance"] = 20
    elif ar < 0.30 and cr < 2.0:
        sp["Star Availability Compliance"] = 15
    elif ar < 0.40:
        sp["Star Availability Compliance"] = 10
    elif ar < 0.50:
        sp["Star Availability Compliance"] = 5
    else:
        sp["Star Availability Compliance"] = 0

    # Net Rating Integrity (inverse of NRCI)
    nrci = case_data.get("NRCI", {})
    nr_change = nrci.get("pre_post_elim", {}).get("net_rating_change", 0)
    cwp = nrci.get("q4_performance", {}).get("close_game_win_pct", 0.5)
    if nr_change > -3 and cwp > 0.40:
        sp["Net Rating Integrity"] = 20
    elif nr_change > -3:
        sp["Net Rating Integrity"] = 15
    elif nr_change > -5 and cwp > 0.30:
        sp["Net Rating Integrity"] = 10
    elif nr_change > -8:
        sp["Net Rating Integrity"] = 5
    else:
        sp["Net Rating Integrity"] = 0

    # Rotation Consistency (inverse of RIS)
    ris = case_data.get("RIS", {})
    sd = ris.get("post_elim_changes", {}).get("significant_decreases", 0)
    cs = ris.get("quality_correlation", {}).get("correlation_shift", 0)
    if sd <= 1 and cs > -0.10:
        sp["Rotation Consistency"] = 20
    elif sd <= 2 and cs > -0.10:
        sp["Rotation Consistency"] = 15
    elif sd <= 3:
        sp["Rotation Consistency"] = 10
    elif cs > 0:
        sp["Rotation Consistency"] = 5
    else:
        sp["Rotation Consistency"] = 0

    # Competitive Engagement (inverse of BTCA)
    btca = case_data.get("BTCA", {})
    pct = btca.get("temporal_pattern", {}).get("post_as_pct_of_pre", 100)
    pewr = btca.get("calendar_correlation", {}).get("periods", {}).get(
        "Post-elimination", {}).get("win_rate", 0.5)
    if pct >= 80:
        sp["Competitive Engagement"] = 15
    elif pct >= 60:
        sp["Competitive Engagement"] = 12
    elif pct >= 40:
        sp["Competitive Engagement"] = 8
    elif pct >= 20:
        sp["Competitive Engagement"] = 4
    else:
        sp["Competitive Engagement"] = 0

    # Homegrown Retention — placeholder (not derivable from TII data)
    # Use a rough estimate based on archetype
    arch = case_data.get("archetype", "")
    if "control" in arch.lower() or "injury" in arch.lower():
        sp["Homegrown Retention"] = 15
    elif "competitive" in arch.lower():
        sp["Homegrown Retention"] = 18
    elif "rebuild" in arch.lower() or "ambiguous" in arch.lower():
        sp["Homegrown Retention"] = 8
    elif "tank" in arch.lower():
        sp["Homegrown Retention"] = 3
    else:
        sp["Homegrown Retention"] = 10

    return sp


all_data = load_all_case_data()

# ── Page content ────────────────────────────────────────────────────────
st.title("Appendix B — Stewardship Points Scoring Matrix")
st.markdown("""
Stewardship Points (SP) are the **reward currency** of the framework.
While the TII detects bad behavior, SP rewards good behavior. Teams accumulate
SP across five categories to qualify for SSL eligibility and ETP supplemental picks.

The SP system is designed as the **inverse of TII**: a team with low TII scores
earns high SP, and vice versa. This page shows the detailed scoring rubric and
applies it to the 8 backtesting cases.
""")

# ── Category rubrics ────────────────────────────────────────────────────
st.subheader("SP Category Rubrics")

for cat_name, cat_info in SP_CATEGORIES.items():
    with st.expander(f"**{cat_name}** — {cat_info['max_points']} pts max ({cat_info['weight']:.0%} weight)"):
        st.markdown(cat_info["description"])
        st.markdown(cat_info["scoring"])
        if cat_info["tii_inverse"]:
            st.caption(f"Derived from TII component: {cat_info['tii_inverse']} (inverse relationship)")

# ── SP Decay mechanism ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("SP Decay Mechanism")
st.markdown("""
Points operate on a **rolling three-year half-life**:

| Season | Multiplier |
|--------|-----------|
| Current season | 100% |
| Prior season | 50% |
| Two seasons prior | 25% |

This prevents teams from "banking" integrity points during one season
and cashing them in while tanking the next.
""")

# ── Apply SP to backtesting cases ───────────────────────────────────────
st.markdown("---")
st.subheader("SP Scores — Applied to Backtesting Cases")

sp_rows = []
for cid, d in sorted(all_data.items()):
    sp_scores = compute_sp_from_tii(d)
    total = sum(sp_scores.values())
    max_possible = sum(c["max_points"] for c in SP_CATEGORIES.values())
    pct = total / max_possible * 100

    # SSL eligibility
    if pct >= 70:
        ssl = "Full"
    elif pct >= 50:
        ssl = "Reduced"
    else:
        ssl = "Ineligible"

    sp_rows.append({
        "Case": cid,
        "Team": d["team"],
        "Season": d["season"],
        "Star Avail": sp_scores["Star Availability Compliance"],
        "NR Integrity": sp_scores["Net Rating Integrity"],
        "Rotation": sp_scores["Rotation Consistency"],
        "Comp Engage": sp_scores["Competitive Engagement"],
        "Retention": sp_scores["Homegrown Retention"],
        "Total SP": total,
        "SP %": f"{pct:.0f}%",
        "SSL Eligibility": ssl,
    })

sp_df = pd.DataFrame(sp_rows)

def color_ssl(row):
    if row["SSL Eligibility"] == "Full":
        return ["background-color: #d4edda"] * len(row)
    elif row["SSL Eligibility"] == "Reduced":
        return ["background-color: #fff3cd"] * len(row)
    return ["background-color: #f8d7da"] * len(row)

st.dataframe(
    sp_df.style.apply(color_ssl, axis=1),
    use_container_width=True,
    hide_index=True,
)

# ── Per-case detail ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Case Detail")

selected = st.selectbox(
    "Select case",
    options=sorted(all_data.keys()),
    format_func=lambda c: f"Case {c}: {all_data[c]['team']} — {all_data[c]['season']}",
    key="sp_case_select",
)

if selected:
    d = all_data[selected]
    sp_scores = compute_sp_from_tii(d)
    total = sum(sp_scores.values())
    max_possible = sum(c["max_points"] for c in SP_CATEGORIES.values())

    st.markdown(f"### Case {selected}: {d['team']} ({d['season']})")
    st.caption(f"Archetype: {d['archetype']}")

    cols = st.columns(len(SP_CATEGORIES))
    for i, (cat_name, cat_info) in enumerate(SP_CATEGORIES.items()):
        earned = sp_scores[cat_name]
        maximum = cat_info["max_points"]
        cols[i].metric(
            cat_name.split()[0],  # Short label
            f"{earned}/{maximum}",
            help=cat_info["description"],
        )

    st.metric("Total SP", f"{total}/{max_possible} ({total/max_possible*100:.0f}%)")

    # Visual bar
    st.progress(total / max_possible)

    # Breakdown chart
    chart_data = pd.DataFrame({
        "Category": list(sp_scores.keys()),
        "Earned": list(sp_scores.values()),
        "Max": [SP_CATEGORIES[c]["max_points"] for c in sp_scores.keys()],
    })
    chart_data["Remaining"] = chart_data["Max"] - chart_data["Earned"]
    st.bar_chart(chart_data.set_index("Category")[["Earned", "Remaining"]])
