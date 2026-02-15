"""Appendix E — Scenario Walkthroughs.

Uses the 8 computed backtesting cases to illustrate how different
organizational behaviors produce different outcomes under the framework.
Maps each case to one of the 5 SRP archetypes.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from tii.config import CASES

st.set_page_config(page_title="Appendix E — Scenario Walkthroughs", page_icon="📋", layout="wide")

COMPUTED_DIR = Path(__file__).resolve().parent.parent / "data" / "computed"

# ── Archetype definitions from the SRP ──────────────────────────────────
ARCHETYPES = {
    "The Legitimate Rebuild": {
        "description": (
            "A young, developing team losing games because they lack talent. "
            "This team plays its best available players, runs competitive rotations, "
            "and loses because better teams beat them."
        ),
        "expected_tii": "Green (0-25)",
        "expected_sp": "High — full SSL eligibility",
        "framework_outcome": (
            "Retains full draft lottery odds. Receives redistributed combinations "
            "from penalized teams. Eligible for SSL rewards and ETP supplemental picks. "
            "**The best possible outcome under the framework.**"
        ),
        "cases": ["F"],
        "key_signal": "Low scores across all 4 TII components despite a bad record.",
    },
    "The Obvious Tank": {
        "description": (
            "An organization that possesses competitive-level talent but deliberately "
            "suppresses it — sitting healthy players, deploying anti-competitive lineups, "
            "engineering late-season collapses."
        ),
        "expected_tii": "Orange/Red (51-100)",
        "expected_sp": "Low — SSL ineligible",
        "framework_outcome": (
            "Combination reduction (15-30%), position displacement (1-2 spots), "
            "SSL ineligibility, contributes to ETP activation threshold. "
            "**Worst-record team with Red TII has roughly 6th-worst odds.**"
        ),
        "cases": ["A", "B", "E"],
        "key_signal": "High SAS (stars sitting), high RIS (rotation overhaul), temporal clustering of losses.",
    },
    "The Mid-Season Pivot": {
        "description": (
            "A team that was competitive early but made a deliberate strategic shift "
            "mid-season — often triggered by trades, injuries, or front office decisions — "
            "and then showed organizational patterns consistent with manufacturing losses."
        ),
        "expected_tii": "Orange (51-75)",
        "expected_sp": "Low — SSL ineligible",
        "framework_outcome": (
            "Flagged by NRCI (performance cliff post-pivot), RIS (rotation overhaul "
            "after deadline trades), and BTCA (calendar-correlated losing pattern). "
            "The trade itself is not penalized — the post-trade behavior is."
        ),
        "cases": ["C"],
        "key_signal": "Dramatic NRCI collapse post-trade deadline, massive RIS disruption.",
    },
    "The Injury-Devastated Contender": {
        "description": (
            "A team with legitimate championship-level talent that loses its best "
            "players to injury. The organization continues to compete with remaining "
            "players and does not manipulate outcomes."
        ),
        "expected_tii": "Green (0-25)",
        "expected_sp": "High — full SSL eligibility",
        "framework_outcome": (
            "TII correctly clears this team. SAS excludes verified injuries. "
            "NRCI recalibrates expected performance for lost talent. "
            "RIS shows rotation adaptation, not manipulation. "
            "**Framework distinguishes bad luck from bad behavior.**"
        ),
        "cases": ["G"],
        "key_signal": "Injuries explain the record. No suspicious organizational patterns.",
    },
    "The Ambiguous Rebuild": {
        "description": (
            "A team in a gray zone — the record is terrible, the roster has been "
            "overhauled, and some organizational decisions look suspicious but could "
            "also be explained by legitimate rebuilding constraints."
        ),
        "expected_tii": "Yellow (26-50)",
        "expected_sp": "Reduced — partial SSL eligibility",
        "framework_outcome": (
            "Yellow classification means: no lottery penalty, no position displacement, "
            "but reduced SSL rewards. The team is on the watchlist. "
            "Public reporting provides transparency. "
            "**The framework applies scrutiny without punishment for ambiguous cases.**"
        ),
        "cases": ["D", "H"],
        "key_signal": "Some concerning signals (elevated BTCA, moderate SAS) but nothing definitive.",
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


def simple_score(component, data):
    """Simplified scoring using default thresholds (matches dashboard defaults)."""
    if not data or data.get("error"):
        return 0.0
    if component == "SAS":
        s = 0.0
        ar = data.get("absence_summary", {}).get("absence_rate", 0)
        if ar > 0.50:
            s += 30 + min((ar - 0.50) * 100, 10)
        elif ar > 0.25:
            s += 15 + (ar - 0.25) / 0.25 * 15
        elif ar > 0.10:
            s += (ar - 0.10) / 0.15 * 15
        cr = data.get("clustering", {}).get("cluster_ratio", 0)
        if cr >= 3.0:
            s += 30
        elif cr >= 2.0:
            s += 20 + (cr - 2.0) * 10
        elif cr >= 1.0:
            s += (cr - 1.0) * 20
        lr = data.get("distribution", {}).get("loss_absence_rate", 0)
        wr = data.get("distribution", {}).get("win_absence_rate", 0)
        if lr > 0 and wr > 0:
            skew = lr / wr
            if skew >= 2.0:
                s += 30
            elif skew >= 1.5:
                s += 15 + (skew - 1.5) / 0.5 * 15
            elif skew >= 1.0:
                s += (skew - 1.0) / 0.5 * 15
        return min(round(s, 1), 100)
    elif component == "NRCI":
        s = 0.0
        decline = data.get("rolling_net_rating", {}).get("max_decline", 0)
        if decline >= 15:
            s += 35
        elif decline >= 10:
            s += 20 + (decline - 10) / 5 * 15
        elif decline >= 5:
            s += 5 + (decline - 5) / 5 * 15
        nr_change = data.get("pre_post_elim", {}).get("net_rating_change", 0)
        if nr_change < -8:
            s += 35
        elif nr_change < -5:
            s += 20 + (abs(nr_change) - 5) / 3 * 15
        elif nr_change < -3:
            s += 10 + (abs(nr_change) - 3) / 2 * 10
        elif nr_change < 0:
            s += abs(nr_change) / 3 * 10
        cwp = data.get("q4_performance", {}).get("close_game_win_pct", 0.5)
        if cwp < 0.20:
            s += 30
        elif cwp < 0.35:
            s += 15 + (0.35 - cwp) / 0.15 * 15
        elif cwp < 0.45:
            s += (0.45 - cwp) / 0.10 * 15
        return min(round(s, 1), 100)
    elif component == "RIS":
        s = 0.0
        sd = data.get("post_elim_changes", {}).get("significant_decreases", 0)
        if sd >= 5:
            s += 35
        elif sd >= 3:
            s += 20 + (sd - 3) / 2 * 15
        elif sd >= 1:
            s += sd / 3 * 20
        np_ = len(data.get("post_elim_changes", {}).get("new_rotation_players", []))
        s += min(np_ * 5, 20)
        cs = data.get("quality_correlation", {}).get("correlation_shift", 0)
        if cs < -0.30:
            s += 25
        elif cs < -0.15:
            s += 10 + (abs(cs) - 0.15) / 0.15 * 15
        elif cs < 0:
            s += abs(cs) / 0.15 * 10
        ei = data.get("experimentation", {}).get("experimentation_increase", 0)
        if ei >= 2.0:
            s += 20
        elif ei >= 1.0:
            s += 10 + (ei - 1.0) * 10
        elif ei > 0:
            s += ei * 10
        return min(round(s, 1), 100)
    elif component == "BTCA":
        s = 0.0
        dev = abs(data.get("league_context", {}).get("deviation_from_baseline", 0))
        if dev >= 2.0:
            s += 30
        elif dev >= 1.0:
            s += 15 + (dev - 1.0) * 15
        else:
            s += dev * 15
        pct = data.get("temporal_pattern", {}).get("post_as_pct_of_pre", 100)
        if pct < 30:
            s += 40
        elif pct < 50:
            s += 25 + (50 - pct) / 20 * 15
        elif pct < 70:
            s += (70 - pct) / 20 * 25
        pewr = data.get("calendar_correlation", {}).get("periods", {}).get("Post-elimination", {}).get("win_rate", 0.5)
        if pewr < 0.10:
            s += 30
        elif pewr < 0.20:
            s += 15 + (0.20 - pewr) / 0.10 * 15
        elif pewr < 0.30:
            s += (0.30 - pewr) / 0.10 * 15
        return min(round(s, 1), 100)
    return 0.0


def classify_color(score):
    if score <= 25:
        return "Green"
    elif score <= 50:
        return "Yellow"
    elif score <= 75:
        return "Orange"
    return "Red"


all_data = load_all_case_data()

# ── Page content ────────────────────────────────────────────────────────
st.title("Appendix E — Scenario Walkthroughs")
st.markdown("""
How different organizational behaviors produce different outcomes under the
Stewardship Reform Plan. Each archetype below is illustrated by one or more
real historical case studies from Appendix A, with live TII component data.
""")

for archetype_name, info in ARCHETYPES.items():
    with st.expander(f"**{archetype_name}**", expanded=False):
        st.markdown(f"**Definition:** {info['description']}")

        col1, col2 = st.columns(2)
        col1.markdown(f"**Expected TII:** {info['expected_tii']}")
        col2.markdown(f"**Expected SP:** {info['expected_sp']}")

        st.markdown(f"**Key detection signal:** {info['key_signal']}")

        st.markdown("---")
        st.markdown(f"**Framework outcome:** {info['framework_outcome']}")

        # Show real case data for this archetype
        st.markdown("---")
        st.markdown("**Historical case studies:**")

        for cid in info["cases"]:
            if cid not in all_data:
                st.caption(f"Case {cid}: data not yet computed")
                continue
            d = all_data[cid]
            st.markdown(f"##### Case {cid}: {d['team']} ({d['season']})")
            st.caption(f"Archetype: {d['archetype']} | Expected: {d['expected']}")

            sas = simple_score("SAS", d["SAS"])
            nrci = simple_score("NRCI", d["NRCI"])
            ris = simple_score("RIS", d["RIS"])
            btca = simple_score("BTCA", d["BTCA"])
            composite = round(sas * 0.30 + nrci * 0.25 + ris * 0.25 + btca * 0.20, 1)
            cls = classify_color(composite)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("SAS", f"{sas:.1f}")
            c2.metric("NRCI", f"{nrci:.1f}")
            c3.metric("RIS", f"{ris:.1f}")
            c4.metric("BTCA", f"{btca:.1f}")
            c5.metric("TII", f"{composite:.1f}", delta=cls)

            # Narrative: what the framework sees
            record = d["BTCA"].get("league_context", {}).get("team_record", "?")
            nr_change = d["NRCI"].get("pre_post_elim", {}).get("net_rating_change", 0)
            shelved = d.get("supplemental", {}).get("veteran_shelving", {}).get("shelved_count", 0)
            sd = d["RIS"].get("post_elim_changes", {}).get("significant_decreases", 0)

            st.markdown(f"""
            **What the framework sees:** Record {record}.
            Net rating change after elimination: **{nr_change:+.1f}**.
            Rotation players with major minute cuts: **{sd}**.
            Veterans shelved post-elimination: **{shelved}**.
            Classification: **{cls}** ({composite:.1f}/100).
            """)

# ── Summary comparison table ────────────────────────────────────────────
st.markdown("---")
st.subheader("Cross-Archetype Comparison")
st.markdown("""
The table below shows how the framework differentiates between the five
organizational archetypes. The key insight: **record alone does not determine
classification.** A 19-63 team (Case A) and a 16-66 team (Case F) can receive
completely different TII outcomes based on *how* they lost.
""")

summary_rows = []
for arch_name, info in ARCHETYPES.items():
    for cid in info["cases"]:
        if cid not in all_data:
            continue
        d = all_data[cid]
        sas = simple_score("SAS", d["SAS"])
        nrci = simple_score("NRCI", d["NRCI"])
        ris = simple_score("RIS", d["RIS"])
        btca = simple_score("BTCA", d["BTCA"])
        composite = round(sas * 0.30 + nrci * 0.25 + ris * 0.25 + btca * 0.20, 1)
        cls = classify_color(composite)
        record = d["BTCA"].get("league_context", {}).get("team_record", "?")
        summary_rows.append({
            "Archetype": arch_name,
            "Case": cid,
            "Team": d["team"],
            "Season": d["season"],
            "Record": record,
            "SAS": sas,
            "NRCI": nrci,
            "RIS": ris,
            "BTCA": btca,
            "TII": composite,
            "Class": cls,
        })

if summary_rows:
    sdf = pd.DataFrame(summary_rows)
    st.dataframe(sdf, use_container_width=True, hide_index=True)
