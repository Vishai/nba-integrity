"""Appendix D — Emerging Talent Pool Governance Simulator.

Interactive simulator showing how the ETP activates and scales based on
league-wide TII classifications. Uses the 8 backtesting cases to model
a hypothetical draft year.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from tii.config import CASES

COMPUTED_DIR = Path(__file__).resolve().parent.parent / "data" / "computed"

# ── ETP tier definitions from SRP Section V ─────────────────────────────
ETP_TIERS = [
    {"name": "Dormant", "condition": "Fewer than 3 teams Orange/Red",
     "etp_share": 0.0, "green_share": 1.0},
    {"name": "Tier 1", "condition": "3+ teams Orange or Red",
     "etp_share": 0.25, "green_share": 0.75},
    {"name": "Tier 2", "condition": "4+ teams Orange/Red OR 3+ Red",
     "etp_share": 0.40, "green_share": 0.60},
    {"name": "Tier 3", "condition": "5+ teams Orange/Red OR 4+ Red",
     "etp_share": 0.50, "green_share": 0.50},
]

# Standard lottery combination assignments (2019+ rules)
LOTTERY_COMBINATIONS = {
    1: 140, 2: 140, 3: 140, 4: 125, 5: 105,
    6: 90, 7: 75, 8: 60, 9: 45, 10: 30,
    11: 20, 12: 15, 13: 10, 14: 5,
}

COMBINATION_REDUCTION = {"Green": 0.0, "Yellow": 0.0, "Orange": 0.15, "Red": 0.30}
POSITION_DISPLACEMENT = {"Green": 0, "Yellow": 0, "Orange": 1, "Red": 2}


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
            **{m: metrics.get(m, {}) for m in ("SAS", "NRCI", "RIS", "BTCA")},
        }
    return out


all_data = load_all_case_data()

# ── Page header ─────────────────────────────────────────────────────────
st.title("Appendix D — ETP Governance Simulator")
st.markdown("""
The **Emerging Talent Pool** is the framework's league-wide enforcement
mechanism. It activates when multiple teams are simultaneously tanking,
and its severity **ratchets up** with each additional offender.

This simulator lets you assign TII classifications to lottery teams and see
exactly how the ETP, combination penalties, and position displacements play out.
""")

# ── Explain the tiers ───────────────────────────────────────────────────
with st.expander("How ETP tiers work", expanded=False):
    st.markdown("""
| Tier | Activation Condition | ETP Pool Share | Green Team Share |
|------|---------------------|---------------|-----------------|
| **Dormant** | Fewer than 3 teams Orange/Red | 0% | 100% of forfeitures |
| **Tier 1** | 3+ teams Orange or Red | 25% | 75% of forfeitures |
| **Tier 2** | 4+ teams Orange/Red OR 3+ Red | 40% | 60% of forfeitures |
| **Tier 3** | 5+ teams Orange/Red OR 4+ Red | 50% | 50% of forfeitures |

The **ratchet effect**: each additional team that tanks increases the forfeiture
pool AND can push the tier higher, compounding penalties for everyone already flagged.
""")

# ── Classification assignment ───────────────────────────────────────────
st.markdown("---")
st.subheader("Assign Classifications to Lottery Teams")
st.markdown("""
Set the TII classification for each of the 14 lottery positions. The simulator
uses real case study data to pre-populate suggestions — override any you like.
""")

# Build default suggestions from case data
case_list = sorted(all_data.keys())
classifications = ["Green", "Yellow", "Orange", "Red"]

team_configs = []
for pos in range(1, 15):
    team_configs.append({
        "position": pos,
        "team": f"Team #{pos}",
        "combinations": LOTTERY_COMBINATIONS[pos],
        "classification": "Green",
    })

# Pre-fill with case data in sidebar
st.sidebar.header("Quick Presets")
if st.sidebar.button("All Green (no tanking)"):
    st.session_state["preset"] = "all_green"
if st.sidebar.button("3 Red (moderate year)"):
    st.session_state["preset"] = "moderate"
if st.sidebar.button("3 Red + 2 Orange (severe)"):
    st.session_state["preset"] = "severe"
if st.sidebar.button("4 Red + 2 Orange (catastrophic)"):
    st.session_state["preset"] = "catastrophic"

preset = st.session_state.get("preset", "moderate")
preset_map = {
    "all_green": {i: "Green" for i in range(1, 15)},
    "moderate": {1: "Red", 2: "Red", 3: "Red", **{i: "Green" for i in range(4, 15)}},
    "severe": {1: "Red", 2: "Red", 3: "Red", 4: "Orange", 5: "Orange",
               **{i: "Green" for i in range(6, 15)}},
    "catastrophic": {1: "Red", 2: "Red", 3: "Red", 4: "Red", 5: "Orange", 6: "Orange",
                     **{i: "Green" for i in range(7, 15)}},
}
defaults = preset_map.get(preset, preset_map["moderate"])

# Classification selectors
cols = st.columns(7)
team_classifications = {}
for pos in range(1, 15):
    col_idx = (pos - 1) % 7
    default_cls = defaults.get(pos, "Green")
    default_idx = classifications.index(default_cls)
    team_classifications[pos] = cols[col_idx].selectbox(
        f"#{pos} ({LOTTERY_COMBINATIONS[pos]} combos)",
        classifications,
        index=default_idx,
        key=f"cls_{pos}",
    )

# ── Compute ETP scenario ────────────────────────────────────────────────
st.markdown("---")
st.subheader("Simulation Results")

# Count classifications
n_red = sum(1 for c in team_classifications.values() if c == "Red")
n_orange = sum(1 for c in team_classifications.values() if c == "Orange")
n_flagged = n_red + n_orange
n_green = sum(1 for c in team_classifications.values() if c == "Green")

# Determine ETP tier
if n_flagged >= 5 or n_red >= 4:
    tier = ETP_TIERS[3]
elif n_flagged >= 4 or n_red >= 3:
    tier = ETP_TIERS[2]
elif n_flagged >= 3:
    tier = ETP_TIERS[1]
else:
    tier = ETP_TIERS[0]

# Headline metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("ETP Tier", tier["name"])
c2.metric("Red Teams", n_red)
c3.metric("Orange Teams", n_orange)
c4.metric("Green Teams", n_green)

# Compute forfeitures and redistribution
total_forfeited = 0
results = []
for pos in range(1, 15):
    cls = team_classifications[pos]
    base_combos = LOTTERY_COMBINATIONS[pos]
    reduction_pct = COMBINATION_REDUCTION[cls]
    forfeited = round(base_combos * reduction_pct)
    remaining = base_combos - forfeited
    displacement = POSITION_DISPLACEMENT[cls]
    effective_pos = min(pos + displacement, 14)

    total_forfeited += forfeited
    results.append({
        "Pos": pos,
        "Classification": cls,
        "Base Combos": base_combos,
        "Reduction": f"-{reduction_pct:.0%}",
        "Forfeited": forfeited,
        "Remaining": remaining,
        "Displacement": f"+{displacement}" if displacement else "—",
        "Effective Pos": effective_pos,
    })

# ETP pool
etp_combos = round(total_forfeited * tier["etp_share"])
green_redistribution = total_forfeited - etp_combos

# Total combinations in the lottery
total_combos = 1000  # Standard NBA lottery
etp_pct_per_draw = etp_combos / total_combos * 100 if total_combos else 0
prob_at_least_one = (1 - (1 - etp_combos / total_combos) ** 4) * 100 if etp_combos else 0

st.markdown("---")

# ETP pool metrics
e1, e2, e3, e4 = st.columns(4)
e1.metric("Total Forfeited", f"{total_forfeited} combos")
e2.metric("ETP Pool", f"{etp_combos} combos ({tier['etp_share']:.0%})")
e3.metric("Green Redistribution", f"{green_redistribution} combos")
e4.metric("ETP Odds per Draw", f"{etp_pct_per_draw:.1f}%")

st.metric("Probability at Least 1 Top-4 Pick Redirected (across 4 draws)",
          f"{prob_at_least_one:.1f}%")

# Detailed results table
st.markdown("---")
st.subheader("Detailed Lottery Impact")
rdf = pd.DataFrame(results)

def color_row(row):
    colors = {
        "Green": "background-color: #d4edda",
        "Yellow": "background-color: #fff3cd",
        "Orange": "background-color: #ffe0cc",
        "Red": "background-color: #f8d7da",
    }
    return [colors.get(row["Classification"], "")] * len(row)

st.dataframe(
    rdf.style.apply(color_row, axis=1),
    use_container_width=True,
    hide_index=True,
)

# ── Ratchet effect visualization ────────────────────────────────────────
st.markdown("---")
st.subheader("The Ratchet Effect")
st.markdown("""
This chart shows how adding one more tanking team compounds the penalties
for **everyone already penalized**. Each additional Red team increases both
the forfeiture pool and the ETP's share of it.
""")

ratchet_rows = []
for scenario_red in range(0, 7):
    for scenario_orange in range(0, 4):
        n_f = scenario_red + scenario_orange
        if n_f >= 5 or scenario_red >= 4:
            t = ETP_TIERS[3]
        elif n_f >= 4 or scenario_red >= 3:
            t = ETP_TIERS[2]
        elif n_f >= 3:
            t = ETP_TIERS[1]
        else:
            t = ETP_TIERS[0]

        # Estimate forfeitures (assume Red teams are top 3, Orange are next)
        forf = scenario_red * 42 + scenario_orange * 15  # rough averages
        etp_c = round(forf * t["etp_share"])
        prob = (1 - (1 - etp_c / 1000) ** 4) * 100 if etp_c else 0

        ratchet_rows.append({
            "Red Teams": scenario_red,
            "Orange Teams": scenario_orange,
            "Tier": t["name"],
            "ETP Combos": etp_c,
            "Pick Redirect Prob": f"{prob:.1f}%",
        })

ratchet_df = pd.DataFrame(ratchet_rows)
# Show a focused subset
key_scenarios = ratchet_df[
    ((ratchet_df["Red Teams"] <= 5) & (ratchet_df["Orange Teams"] <= 2))
].copy()
key_scenarios = key_scenarios.sort_values(["Red Teams", "Orange Teams"])
st.dataframe(key_scenarios, use_container_width=True, hide_index=True, height=400)

# ── Edge case protocols ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("Edge Case Protocols")

with st.expander("Maximum redirection cap"):
    st.markdown("""
    No more than **2 picks** can be redirected into the ETP in any single draft.
    If ETP combinations are drawn for a 3rd pick, the drawing continues with
    the ETP's remaining combinations removed from the pool.
    """)

with st.expander("Tier boundary disputes"):
    st.markdown("""
    ETP tier determination is **fully algorithmic** based on published
    classification counts and BTCA thresholds. No human discretion exists
    in activation or tier determination. The only human judgment in the ETP
    system is the TII Review Board's role in collusion investigations.
    """)

with st.expander("Supplemental selection process"):
    st.markdown("""
    When an ETP combination is drawn:

    1. The corresponding pick (1st through 4th) is redirected from the team
       that would have received it into the ETP supplemental pool.
    2. Supplemental picks are made available to teams ranked in the **top
       quartile of Stewardship Points (SP)**, ordered by SP ranking.
    3. The #1 SP team selects first.
    4. Supplemental picks carry standard rookie scale contract obligations.
    """)

with st.expander("Anti-gaming provisions"):
    st.markdown("""
    **Provision 1:** Red/Orange teams cannot access ETP picks.

    **Provision 2: Tainted network exclusion.** Also ineligible:
    - Teams that acquired draft assets from a Red team via trade within 24 months
    - Teams that sent draft assets to a Red team within 24 months
    - Teams whose ownership group overlaps with a Red team's

    **Provision 3:** ETP access requires top-quartile SP ranking, which requires
    a full season of genuine competitive behavior.
    """)

with st.expander("Collusion forfeiture (nuclear deterrent)"):
    st.markdown("""
    If the TII Review Board determines that two or more teams engaged in
    **deliberate coordination** to manipulate TII classifications or draft
    positioning:

    - All involved teams forfeit **all draft selections** for **3 years**
    - All involved front office personnel face discipline up to lifetime bans
    - Forfeited picks distributed through ETP to top-SP teams
    """)
