"""Appendix F — Implementation Timeline.

Proposed rollout schedule including observation period, calibration phase,
and full activation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Appendix F — Implementation Timeline", page_icon="📅", layout="wide")

st.title("Appendix F — Implementation Timeline")
st.markdown("""
A phased rollout ensures the framework is validated with real data before
consequences attach. This approach protects franchises from being penalized
during calibration while building confidence in the system's accuracy.
""")

# ── Phase definitions ───────────────────────────────────────────────────
PHASES = [
    {
        "phase": "Phase 0: Foundation",
        "duration": "6 months (offseason)",
        "timing": "Year 0 offseason",
        "status": "Pre-launch",
        "activities": [
            "TII Review Board appointed (3 independent statisticians, 2 former GMs, 1 NBPA rep)",
            "Full methodology published and open for public comment",
            "Historical backtesting completed (minimum 15 seasons)",
            "Data pipeline infrastructure built and validated",
            "Threshold calibration using backtesting results",
            "Board of Governors vote on framework adoption",
        ],
        "milestones": [
            "Backtesting validation report published",
            "All 4 TII components calibrated against historical data",
            "Data sharing agreements with teams finalized",
        ],
        "risks": [
            "Threshold disagreements delay adoption",
            "Data access issues with historical seasons",
        ],
    },
    {
        "phase": "Phase 1: Shadow Scoring",
        "duration": "1 full season",
        "timing": "Year 1 regular season",
        "status": "Observation only",
        "activities": [
            "TII scores computed for all 30 teams in real-time",
            "SP accumulation tracked for all teams",
            "Scores shared with teams privately at mid-season and end-of-season",
            "NO public reporting, NO consequences, NO penalties",
            "Teams given opportunity to provide feedback on methodology",
            "Review Board collects calibration data",
        ],
        "milestones": [
            "Mid-season checkpoint reports delivered to all 30 teams",
            "End-of-season shadow scores published (internal only)",
            "Calibration review meeting with Board of Governors",
        ],
        "risks": [
            "Teams may alter behavior knowing they're being monitored (Hawthorne effect — actually desirable)",
            "Shadow scoring may reveal threshold issues requiring adjustment",
        ],
    },
    {
        "phase": "Phase 2: Public Reporting",
        "duration": "1 full season",
        "timing": "Year 2 regular season",
        "status": "Transparency without penalties",
        "activities": [
            "TII scores published at All-Star break (mid-season checkpoint)",
            "End-of-season final scores published publicly",
            "SP rankings published alongside TII",
            "Media and fan engagement with the scoring system",
            "Still NO lottery penalties, NO SSL rewards, NO ETP activation",
            "Teams can appeal classifications (appeals process tested)",
        ],
        "milestones": [
            "First public mid-season TII report",
            "First public end-of-season TII report",
            "Appeals process tested with at least 2 teams",
            "Public credibility assessment conducted",
        ],
        "risks": [
            "Public scrutiny reveals edge cases not anticipated",
            "Media misinterpretation of scores",
            "Teams lobby for methodology changes",
        ],
    },
    {
        "phase": "Phase 3: Partial Activation",
        "duration": "1 full season",
        "timing": "Year 3 regular season",
        "status": "SSL active, lottery penalties dormant",
        "activities": [
            "SSL rewards activated — qualifying teams receive cap credits and draft assets",
            "SP accumulation has real consequences for first time",
            "Lottery penalties remain dormant (no combination reduction, no position displacement)",
            "ETP remains dormant",
            "Full public reporting continues",
            "Review Board conducts first annual methodology review",
        ],
        "milestones": [
            "First SSL lottery conducted",
            "First cap elasticity credits awarded",
            "Year 3 calibration review (threshold adjustments if needed)",
        ],
        "risks": [
            "SSL rewards may be too small to change behavior",
            "Teams may game SP accumulation without genuine behavior change",
        ],
    },
    {
        "phase": "Phase 4: Full Activation",
        "duration": "Ongoing",
        "timing": "Year 4+ regular season",
        "status": "Fully operational",
        "activities": [
            "All framework components active simultaneously",
            "Lottery combination penalties applied to Orange/Red teams",
            "Position displacement applied to Orange/Red teams",
            "ETP capable of activating based on league-wide conditions",
            "SSL rewards at full scale",
            "Annual methodology review cycle established",
            "3-year comprehensive review with Board of Governors",
        ],
        "milestones": [
            "First lottery with combination penalties applied",
            "First public demonstration of framework consequences",
            "3-year comprehensive review (adjust weights, thresholds, prize structure)",
        ],
        "risks": [
            "Unintended consequences in competitive dynamics",
            "Teams find novel circumvention strategies",
            "CBA negotiation may require framework adjustments",
        ],
    },
]

# ── Timeline visualization ──────────────────────────────────────────────
st.subheader("Rollout Phases")

timeline_data = []
for p in PHASES:
    timeline_data.append({
        "Phase": p["phase"],
        "Duration": p["duration"],
        "Status": p["status"],
        "Key Milestone": p["milestones"][0] if p["milestones"] else "",
    })

st.dataframe(pd.DataFrame(timeline_data), use_container_width=True, hide_index=True)

# ── Detailed phase cards ────────────────────────────────────────────────
st.markdown("---")

for p in PHASES:
    with st.expander(f"**{p['phase']}** — {p['duration']} ({p['status']})"):
        st.markdown(f"**Timing:** {p['timing']}")

        st.markdown("**Activities:**")
        for a in p["activities"]:
            st.markdown(f"- {a}")

        st.markdown("**Milestones:**")
        for m in p["milestones"]:
            st.markdown(f"- {m}")

        if p["risks"]:
            st.markdown("**Risks & Mitigations:**")
            for r in p["risks"]:
                st.markdown(f"- {r}")

# ── Component activation matrix ─────────────────────────────────────────
st.markdown("---")
st.subheader("Component Activation Matrix")

matrix_data = {
    "Component": [
        "TII Scoring (private)",
        "TII Scoring (public)",
        "SP Accumulation",
        "SSL Rewards",
        "Lottery Combination Penalties",
        "Position Displacement",
        "ETP Mechanism",
        "Appeals Process",
        "Annual Review Cycle",
    ],
    "Phase 0": ["—"] * 9,
    "Phase 1": ["Active", "—", "Shadow", "—", "—", "—", "—", "—", "—"],
    "Phase 2": ["Active", "Active", "Active", "—", "—", "—", "—", "Testing", "—"],
    "Phase 3": ["Active", "Active", "Active", "Active", "—", "—", "—", "Active", "Active"],
    "Phase 4": ["Active", "Active", "Active", "Active", "Active", "Active", "Active", "Active", "Active"],
}

matrix_df = pd.DataFrame(matrix_data)

def highlight_active(val):
    if val == "Active":
        return "background-color: #d4edda; font-weight: bold"
    elif val == "Shadow" or val == "Testing":
        return "background-color: #fff3cd"
    elif val == "—":
        return "color: #ccc"
    return ""

st.dataframe(
    matrix_df.style.map(highlight_active),
    use_container_width=True,
    hide_index=True,
)

# ── CBA integration considerations ──────────────────────────────────────
st.markdown("---")
st.subheader("CBA Integration Considerations")

st.markdown("""
The framework is designed to be **CBA-compatible** rather than CBA-dependent.
Key considerations:

**Requires CBA amendment:**
- SSL cap elasticity credits (new financial mechanism)
- Trade flexibility enhancements (modification of existing trade rules)
- ETP pick redirection (modification of draft assignment rules)

**Does NOT require CBA amendment:**
- TII scoring and publication (league can adopt unilaterally as competitive integrity measure)
- SP tracking and publication (informational only)
- Lottery combination adjustments (Board of Governors authority under current rules)
- Position displacement (Board of Governors authority)

**Recommended approach:** Begin Phases 0-2 under existing league authority.
Negotiate SSL/ETP components into next CBA cycle. This allows 2+ years of
public data and credibility building before the most consequential components
require formal labor agreement.
""")

# ── Backtesting validation note ──────────────────────────────────────────
st.markdown("---")
st.subheader("Backtesting Informs Timeline")

st.markdown("""
The 8 historical case studies in Appendix A directly inform this timeline:

- **Threshold calibration issues** (Cases A/B scoring Yellow instead of expected Red)
  validate the need for Phases 1-2 before penalties activate
- **Successful control cases** (Cases F/G correctly scoring Green) build confidence
  in the detection methodology
- **Ambiguous cases** (Case D) demonstrate why the appeals process must be tested
  before full activation
- **The calibration dashboard** provides the tooling needed for Phase 0 threshold tuning

The framework's credibility depends on getting the observation period right.
Rushing to penalties before the system is validated would undermine stakeholder trust.
""")
