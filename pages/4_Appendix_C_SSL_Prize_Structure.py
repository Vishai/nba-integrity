"""Appendix C — Stewardship Supplemental Lottery Prize Structure.

Details the rewards available to high-SP teams through the SSL system:
cap elasticity credits, trade flexibility enhancements, and supplemental
draft assets.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from tii.config import CASES

COMPUTED_DIR = Path(__file__).resolve().parent.parent / "data" / "computed"

# ── SSL prize tier definitions ──────────────────────────────────────────
SSL_TIERS = {
    "Tier 1 (Top SP)": {
        "sp_threshold": "Top 5 SP teams",
        "draft_assets": "1 additional 2nd-round pick + draft swap rights on own 1st",
        "etp_eligibility": "First priority for ETP supplemental picks (potential 1st-round talent)",
        "cap_credits": "$3M cap elasticity credit (usable against luxury tax or as trade exception)",
        "trade_flex": "Expanded trade exception window (+60 days); relaxed matching salary (125% + $250K instead of 125% + $100K)",
        "color": "#d4edda",
    },
    "Tier 2 (High SP)": {
        "sp_threshold": "SP rank 6-10",
        "draft_assets": "1 additional 2nd-round pick",
        "etp_eligibility": "Eligible for ETP supplemental picks (after Tier 1 teams select)",
        "cap_credits": "$1.5M cap elasticity credit",
        "trade_flex": "Expanded trade exception window (+30 days)",
        "color": "#d4f5d4",
    },
    "Tier 3 (Qualifying SP)": {
        "sp_threshold": "SP rank 11-15 (above median)",
        "draft_assets": "Conditional 2nd-round swap rights",
        "etp_eligibility": "Ineligible (must be top quartile SP)",
        "cap_credits": "$500K cap elasticity credit",
        "trade_flex": "Standard trade rules (no enhancement)",
        "color": "#fff3cd",
    },
    "Below Threshold": {
        "sp_threshold": "SP rank 16-30",
        "draft_assets": "None",
        "etp_eligibility": "Ineligible",
        "cap_credits": "None",
        "trade_flex": "Standard trade rules",
        "color": "#f8d7da",
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


def estimate_sp_total(case_data):
    """Quick SP estimate (reuses logic from Appendix B)."""
    sp = 0
    sas = case_data.get("SAS", {})
    ar = sas.get("absence_summary", {}).get("absence_rate", 0)
    cr = sas.get("clustering", {}).get("cluster_ratio", 0)
    if ar < 0.10 and cr < 1.5:
        sp += 25
    elif ar < 0.20:
        sp += 20
    elif ar < 0.30:
        sp += 15
    elif ar < 0.40:
        sp += 10
    elif ar < 0.50:
        sp += 5

    nrci = case_data.get("NRCI", {})
    nr_change = nrci.get("pre_post_elim", {}).get("net_rating_change", 0)
    cwp = nrci.get("q4_performance", {}).get("close_game_win_pct", 0.5)
    if nr_change > -3 and cwp > 0.40:
        sp += 20
    elif nr_change > -3:
        sp += 15
    elif nr_change > -5:
        sp += 10
    elif nr_change > -8:
        sp += 5

    ris = case_data.get("RIS", {})
    sd = ris.get("post_elim_changes", {}).get("significant_decreases", 0)
    cs = ris.get("quality_correlation", {}).get("correlation_shift", 0)
    if sd <= 1 and cs > -0.10:
        sp += 20
    elif sd <= 2:
        sp += 15
    elif sd <= 3:
        sp += 10
    elif cs > 0:
        sp += 5

    btca = case_data.get("BTCA", {})
    pct = btca.get("temporal_pattern", {}).get("post_as_pct_of_pre", 100)
    if pct >= 80:
        sp += 15
    elif pct >= 60:
        sp += 12
    elif pct >= 40:
        sp += 8
    elif pct >= 20:
        sp += 4

    # Homegrown placeholder
    arch = case_data.get("archetype", "")
    if "control" in arch.lower() or "competitive" in arch.lower():
        sp += 15
    elif "rebuild" in arch.lower():
        sp += 8
    elif "tank" in arch.lower():
        sp += 3
    else:
        sp += 10

    return sp


all_data = load_all_case_data()

# ── Page content ────────────────────────────────────────────────────────
st.title("Appendix C — SSL Prize Structure")
st.markdown("""
The **Stewardship Supplemental Lottery (SSL)** rewards franchises demonstrating
competitive integrity with three categories of meaningful assets. Unlike the
standard draft, the SSL creates a **positive incentive layer** — teams earn
tangible rewards for ethical organizational behavior.
""")

# ── Prize tiers ─────────────────────────────────────────────────────────
st.subheader("SSL Reward Tiers")

for tier_name, tier_info in SSL_TIERS.items():
    with st.expander(f"**{tier_name}** — {tier_info['sp_threshold']}"):
        c1, c2 = st.columns(2)
        c1.markdown(f"**Draft Assets:**\n\n{tier_info['draft_assets']}")
        c2.markdown(f"**ETP Supplemental Picks:**\n\n{tier_info['etp_eligibility']}")
        c3, c4 = st.columns(2)
        c3.markdown(f"**Cap Credits:**\n\n{tier_info['cap_credits']}")
        c4.markdown(f"**Trade Flexibility:**\n\n{tier_info['trade_flex']}")

# ── Cap elasticity details ──────────────────────────────────────────────
st.markdown("---")
st.subheader("Cap Elasticity Credit Mechanics")

st.markdown("""
Cap elasticity credits provide meaningful financial flexibility without
breaking the salary cap structure.

**How they work:**

1. **Earned annually** based on SSL tier qualification
2. **Applied at team's discretion** during the following offseason
3. **Single-use** — credits do not roll over year to year
4. **Three application modes** (team chooses one):

| Application Mode | Effect |
|-----------------|--------|
| **Luxury Tax Offset** | Credit reduces taxable payroll for tax calculation only |
| **Trade Exception** | Credit creates a trade exception of equal value |
| **Mid-Level Extension** | Credit added to available MLE space for re-signing own players only |

**Guardrails:**
- Credits cannot be traded or transferred between teams
- Credits cannot be combined across seasons
- Credits cannot be used to exceed the hard cap (apron)
- Credits are forfeited if the team's TII classification worsens to Orange/Red
  in the season the credit would be applied
""")

# ── Draft asset details ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("Supplemental Draft Asset Specifications")

st.markdown("""
| Asset Type | Details |
|-----------|---------|
| **Additional 2nd-round pick** | Assigned by SSL lottery odds (weighted by SP). Selection made after the standard 2nd round. |
| **Draft swap rights** | Right to swap own 1st-round pick with a team picking later (if beneficial). Only exercisable on own pick, not traded picks. |
| **Conditional 2nd-round swap** | Right to swap own 2nd-round position with next-worse-positioned team. |

**SSL Lottery Mechanics:**
- Separate lottery event conducted after the Standard Draft
- Odds weighted by SP accumulation (higher SP = better odds)
- Diminishing returns: teams in top 5 SP for 3+ consecutive years get 10%
  odds reduction per additional year to prevent runaway advantages
""")

# ── ETP supplemental pick integration ──────────────────────────────────
st.markdown("---")
st.subheader("🎯 ETP Supplemental Picks — The Marquee Prize")

st.markdown("""
The single most valuable SSL benefit is access to **ETP supplemental picks** —
first-round talent redirected from teams caught tanking. This is the mechanism
that makes sustained competitive integrity genuinely transformative for a
franchise's roster construction.

**How it works:**

When the **Emerging Talent Pool (ETP)** activates (see Appendix D), it
participates in the standard NBA Draft Lottery as its own entity. If an ETP
combination is drawn during any of the four lottery drawings (picks 1–4),
that pick is **redirected from the team that would have received it** into
a supplemental draft available exclusively to top-SP teams.

| Step | What Happens |
|------|-------------|
| 1. ETP activates | 3+ teams classified Orange/Red triggers ETP |
| 2. Forfeitures pooled | Combination reductions from penalized teams feed the ETP pool |
| 3. Lottery drawing | ETP combinations participate in the standard lottery alongside all 14 teams |
| 4. ETP combination drawn | The corresponding pick (1st–4th) is redirected to the supplemental draft |
| 5. Supplemental selection | Top-quartile SP teams select in SP rank order (#1 SP picks first) |
| 6. Rookie scale applies | Supplemental picks carry standard rookie contract obligations |

**Eligibility requirements:**
- Must be in the **top quartile of SP** (roughly top 7-8 teams league-wide)
- Must be classified **Green** (Orange/Red teams are categorically ineligible)
- Must not have acquired draft assets from a Red team in the past 24 months
  (tainted network exclusion)

**Maximum redirection cap:** No more than **2 picks** can be redirected into the
ETP in any single draft. This prevents catastrophic disruption to the draft
while maintaining meaningful enforcement.

**Why this matters:** In a severe tanking year (Tier 2+), there is a
**23–34% probability** that at least one top-4 pick is redirected. A
high-SP team could receive a lottery-caliber prospect simply by
demonstrating organizational integrity. This is the framework's most
powerful positive incentive.
""")

# ── Trade flexibility details ───────────────────────────────────────────
st.markdown("---")
st.subheader("Trade Flexibility Enhancements")

st.markdown("""
| Enhancement | Standard Rule | SSL Enhancement |
|------------|--------------|----------------|
| **Trade exception window** | 1 year from date of trade | +30 days (Tier 2) or +60 days (Tier 1) |
| **Matching salary requirement** | 125% + $100K of outgoing salary | 125% + $250K (Tier 1 only) |
| **Simultaneous trades** | Max 2 trades aggregated | No change |

These enhancements are modest but meaningful — they create additional roster
construction flexibility that compounds over time for consistently high-SP teams.
""")

# ── Apply to backtesting cases ──────────────────────────────────────────
st.markdown("---")
st.subheader("What Each Case Team Would Receive")
st.markdown("""
Based on SP estimates from the backtesting cases, here's what each team would
earn through the SSL system. In a real 30-team league, SP rankings determine
tier placement — this simulates using the 8-case subset.
""")

case_sp = []
for cid, d in sorted(all_data.items()):
    sp = estimate_sp_total(d)
    case_sp.append({"case_id": cid, "team": d["team"], "season": d["season"],
                    "archetype": d["archetype"], "sp": sp})

case_sp.sort(key=lambda x: x["sp"], reverse=True)

# Assign tiers by rank within the 8 cases
tier_names = list(SSL_TIERS.keys())
for i, cs in enumerate(case_sp):
    if i < 2:
        cs["ssl_tier"] = tier_names[0]
    elif i < 4:
        cs["ssl_tier"] = tier_names[1]
    elif i < 6:
        cs["ssl_tier"] = tier_names[2]
    else:
        cs["ssl_tier"] = tier_names[3]

ssl_rows = []
for cs in case_sp:
    tier_info = SSL_TIERS[cs["ssl_tier"]]
    ssl_rows.append({
        "Case": cs["case_id"],
        "Team": cs["team"],
        "Season": cs["season"],
        "SP Estimate": cs["sp"],
        "SSL Tier": cs["ssl_tier"],
        "Draft Assets": tier_info["draft_assets"],
        "Cap Credit": tier_info["cap_credits"],
    })

ssl_df = pd.DataFrame(ssl_rows)

def color_tier(row):
    for tier_name, tier_info in SSL_TIERS.items():
        if row["SSL Tier"] == tier_name:
            return [f"background-color: {tier_info['color']}"] * len(row)
    return [""] * len(row)

st.dataframe(
    ssl_df.style.apply(color_tier, axis=1),
    use_container_width=True,
    hide_index=True,
)

st.markdown("""
**Key takeaway:** The legitimate rebuilds (Cases F, G) and competitive teams
(Case H) earn the best SSL rewards, while obvious tankers (Cases A, B, E)
receive nothing. The framework creates a tangible asset gap between integrity
and manipulation.
""")
