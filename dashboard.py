"""TII Calibration Dashboard — Streamlit app for tuning scoring thresholds.

Includes:
  - Full explanations of every metric for non-technical users
  - Supplemental indicators (DPI, Margin Profile, Veteran Shelving, Lineup Overhaul)
  - Live re-scoring as sliders change
"""

import sys
import os
import json
from pathlib import Path

# Ensure tii package is importable
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np

from tii.config import get_all_cases, CLASSIFICATIONS
from tii.case_prefs import is_pinned, is_hidden, set_pref

# Try SQLite cache first (local dev), fall back to JSON exports (Streamlit Cloud)
COMPUTED_DIR = Path(__file__).parent / "data" / "computed"
try:
    from tii import cache
    _USE_CACHE = True
except Exception:
    _USE_CACHE = False

# ── Page setup ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TII Calibration Dashboard",
    page_icon="🏀",
    layout="wide",
)

st.title("🏀 Tanking Integrity Index — Calibration Dashboard")

RUN_MODE = os.getenv("RUN_MODE", "local").strip().lower()
IS_LOCAL_MODE = RUN_MODE == "local"
IS_CLOUD_MODE = RUN_MODE == "cloud"

# ══════════════════════════════════════════════════════════════════════════
# HOW IT WORKS (expandable)
# ══════════════════════════════════════════════════════════════════════════
with st.expander("📖 How to read this dashboard — Start here if you're new", expanded=False):
    st.markdown("""
### What is the TII?

The **Tanking Integrity Index (TII)** is a 0–100 score that measures how likely
an NBA team is deliberately losing games to get a better draft pick. Higher
scores = more suspicious behavior.

### The 4 Core Components

The TII is a weighted average of four independent signals:

| Component | What it measures | Weight | Why it matters |
|-----------|-----------------|--------|----------------|
| **SAS** (Star Availability Score) | Are star players mysteriously sitting out? | 30% | Tanking teams rest healthy stars to lose more games |
| **NRCI** (Net Rating Collapse Index) | Did the team suddenly get much worse? | 25% | Tanking teams show a sharp performance cliff, especially after playoff elimination |
| **RIS** (Rotation Integrity Score) | Did the coach stop playing good players? | 25% | Tanking teams bench veterans and play unproven players after elimination |
| **BTCA** (Bottom-Tier Clustering) | How does this team compare historically? | 20% | Puts the team's record in context: are they historically bad, or just bad? |

### The Classification System

| Color | Score Range | Meaning |
|-------|------------|---------|
| 🟢 **Green** | 0–25 | Legitimately bad or injury-wrecked. No integrity concern. |
| 🟡 **Yellow** | 26–50 | Some concerning signals but could be explained by circumstances. |
| 🟠 **Orange** | 51–75 | Strong evidence of deliberate losing. Warrants investigation. |
| 🔴 **Red** | 76–100 | Blatant competitive integrity failure. League should intervene. |

### How to use the sliders

The **sidebar** on the left has sliders that let you adjust:
1. **Weights** — How much each component matters in the final score
2. **Boundaries** — Where the Green/Yellow/Orange/Red cutoff lines are
3. **Thresholds** — The internal sensitivity of each component

Move any slider and watch the scoreboard update in real-time. The goal is
to find settings where **known tankers score Red** and **legitimate rebuilds
score Green**.

### What are the "Supplemental Indicators"?

Below the main scores, you'll find additional context that doesn't factor
into the TII score but helps you understand what happened:
- **Draft position** — Where the team ended up picking
- **Veteran shelving** — Stars who stopped playing post-elimination
- **Roster churn** — How many players were traded at the deadline
- **Margin profile** — Were the losses blowouts or competitive?
""")


# ── Load all raw component data once ────────────────────────────────────
@st.cache_data
def load_all_case_data():
    """Load SAS, NRCI, RIS, BTCA, and supplemental raw data for every active case.

    Tries SQLite cache first (local dev), falls back to JSON exports (Streamlit Cloud).
    """
    out = {}
    for cid, cfg in get_all_cases().items():
        if cfg.get("skip"):
            continue
        row = {"case_id": cid, "team": cfg["team_name"], "season": cfg["season"],
               "archetype": cfg["archetype"], "expected": cfg["expected_classification"]}

        # Try loading from JSON export first, then SQLite cache
        json_path = COMPUTED_DIR / f"case_{cid}.json"
        if json_path.exists():
            all_metrics = json.loads(json_path.read_text())
            for metric in ("SAS", "NRCI", "RIS", "BTCA", "supplemental"):
                row[metric] = all_metrics.get(metric, {})
        elif _USE_CACHE:
            for metric in ("SAS", "NRCI", "RIS", "BTCA", "supplemental"):
                stored = cache.load_computed(cid, metric)
                row[metric] = stored["data"] if stored else {}
        else:
            for metric in ("SAS", "NRCI", "RIS", "BTCA", "supplemental"):
                row[metric] = {}

        out[cid] = row
    return out

all_data = load_all_case_data()

if not all_data:
    st.error("No computed data found. Run `python tii.py compute --all` first.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Weight & Threshold Sliders
# ══════════════════════════════════════════════════════════════════════════
st.sidebar.header("⚖️ Component Weights")
st.sidebar.caption("Must sum to 1.0. Adjust to change relative importance.")

w_sas = st.sidebar.slider("SAS weight", 0.0, 1.0, 0.30, 0.05, key="w_sas",
                           help="Star Availability Score — are stars being rested?")
w_nrci = st.sidebar.slider("NRCI weight", 0.0, 1.0, 0.25, 0.05, key="w_nrci",
                            help="Net Rating Collapse — did performance crater?")
w_ris = st.sidebar.slider("RIS weight", 0.0, 1.0, 0.25, 0.05, key="w_ris",
                           help="Rotation Integrity — did the coach stop playing good players?")
w_btca = st.sidebar.slider("BTCA weight", 0.0, 1.0, 0.20, 0.05, key="w_btca",
                            help="Bottom-Tier Clustering — is this historically bad?")

weight_sum = round(w_sas + w_nrci + w_ris + w_btca, 2)
if abs(weight_sum - 1.0) > 0.01:
    st.sidebar.warning(f"Weights sum to **{weight_sum}** — should be 1.0")
else:
    st.sidebar.success(f"Weights sum to {weight_sum} ✓")

weights = {"SAS": w_sas, "NRCI": w_nrci, "RIS": w_ris, "BTCA": w_btca}

# ── Classification boundaries ───────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("🎯 Classification Boundaries")
st.sidebar.caption("Drag to change where Green/Yellow/Orange/Red cutoffs land.")

green_max = st.sidebar.slider("Green ceiling (→ Yellow starts)", 5, 50, 25, 1)
yellow_max = st.sidebar.slider("Yellow ceiling (→ Orange starts)", green_max + 1, 75, 50, 1)
orange_max = st.sidebar.slider("Orange ceiling (→ Red starts)", yellow_max + 1, 95, 75, 1)

def classify(score):
    if score <= green_max:
        return "🟢 Green"
    elif score <= yellow_max:
        return "🟡 Yellow"
    elif score <= orange_max:
        return "🟠 Orange"
    else:
        return "🔴 Red"

def classify_plain(score):
    if score <= green_max:
        return "Green"
    elif score <= yellow_max:
        return "Yellow"
    elif score <= orange_max:
        return "Orange"
    else:
        return "Red"


# ══════════════════════════════════════════════════════════════════════════
# SAS THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("---")
st.sidebar.header("1️⃣ SAS Thresholds")
st.sidebar.caption("Star Availability: when do absences become suspicious?")

sas_absence_low = st.sidebar.slider(
    "Absence rate — start flagging at", 0.05, 0.30, 0.10, 0.01, key="sas_abs_lo",
    help="% of games missed by qualified starters. 10% = ~8 games in an 82-game season.")
sas_absence_mid = st.sidebar.slider(
    "Absence rate — moderate", 0.15, 0.50, 0.25, 0.01, key="sas_abs_mid",
    help="25% = ~20 games missed. This starts looking intentional.")
sas_absence_high = st.sidebar.slider(
    "Absence rate — high", 0.30, 0.80, 0.50, 0.01, key="sas_abs_hi",
    help="50%+ = half the season missed. Very suspicious unless there's a real injury.")
sas_cluster_flag = st.sidebar.slider(
    "Cluster ratio flag", 1.0, 5.0, 2.0, 0.25, key="sas_clust",
    help="Ratio of post-elimination absences to pre-elimination. 2.0 = stars miss 2x as many games after being eliminated.")
sas_skew_flag = st.sidebar.slider(
    "Loss/Win absence skew flag", 1.0, 4.0, 1.5, 0.25, key="sas_skew",
    help="Are stars missing more games in losses than wins? 1.5 = 50% more absences in losses.")

# ══════════════════════════════════════════════════════════════════════════
# NRCI THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("---")
st.sidebar.header("2️⃣ NRCI Thresholds")
st.sidebar.caption("Net Rating Collapse: how steep is the performance drop?")

nrci_decline_mid = st.sidebar.slider(
    "Rolling NR decline — moderate", 3.0, 15.0, 5.0, 0.5, key="nrci_dec_mid",
    help="Net rating decline over a 15-game window. 5 points = going from average to below average.")
nrci_decline_high = st.sidebar.slider(
    "Rolling NR decline — severe", 8.0, 25.0, 10.0, 0.5, key="nrci_dec_hi",
    help="10-point drop = from competitive to bottom of the league.")
nrci_decline_max = st.sidebar.slider(
    "Rolling NR decline — max flag", 10.0, 30.0, 15.0, 0.5, key="nrci_dec_max",
    help="15+ point drop = nearly unprecedented. Something is very wrong.")
nrci_collapse_mild = st.sidebar.slider(
    "Post-elim NR change — mild", -1.0, -8.0, -3.0, 0.5, key="nrci_col_mild",
    help="Net rating change after elimination. -3 = modest decline.")
nrci_collapse_mod = st.sidebar.slider(
    "Post-elim NR change — moderate", -3.0, -12.0, -5.0, 0.5, key="nrci_col_mod",
    help="-5 = clear performance drop after being eliminated.")
nrci_collapse_severe = st.sidebar.slider(
    "Post-elim NR change — severe", -5.0, -20.0, -8.0, 0.5, key="nrci_col_sev",
    help="-8+ = dramatic collapse. Team plays like they've given up.")
nrci_close_wp_suspicious = st.sidebar.slider(
    "Close game win% — suspicious below", 0.20, 0.55, 0.35, 0.01, key="nrci_cwp",
    help="Win rate in close games. Below .350 suggests the team isn't trying to win tight games.")

# ══════════════════════════════════════════════════════════════════════════
# RIS THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("---")
st.sidebar.header("3️⃣ RIS Thresholds")
st.sidebar.caption("Rotation Integrity: did the lineup change suspiciously?")

ris_sig_decrease_mod = st.sidebar.slider(
    "Sig minute decreases — moderate", 1, 6, 3, 1, key="ris_sd_mod",
    help="# of rotation players who lost 20%+ of their minutes after elimination.")
ris_sig_decrease_high = st.sidebar.slider(
    "Sig minute decreases — high", 3, 8, 5, 1, key="ris_sd_hi",
    help="5+ players losing major minutes = wholesale rotation overhaul.")
ris_corr_shift_flag = st.sidebar.slider(
    "Correlation shift flag", -0.50, 0.0, -0.15, 0.05, key="ris_corr",
    help="Do better players still get more minutes? Negative shift = meritocracy breaking down.")
ris_new_player_pts = st.sidebar.slider(
    "Points per new rotation player", 1, 10, 5, 1, key="ris_npp",
    help="How many points each new rotation player adds to the score.")

# ══════════════════════════════════════════════════════════════════════════
# BTCA THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("---")
st.sidebar.header("4️⃣ BTCA Thresholds")
st.sidebar.caption("Bottom-Tier Clustering: historical context for the team's record.")

btca_post_asb_flag = st.sidebar.slider(
    "Post-ASB as % of pre — flag below", 20, 90, 50, 5, key="btca_asb",
    help="Win rate after All-Star break as a percentage of before. Below 50% = team collapsed after ASB.")
btca_post_elim_wr = st.sidebar.slider(
    "Post-elim win rate — flag below", 0.05, 0.50, 0.20, 0.01, key="btca_wr",
    help="Win rate after mathematical elimination. Below .200 = barely winning any games.")


# ══════════════════════════════════════════════════════════════════════════
# SCORING FUNCTIONS (parameterised by slider values)
# ══════════════════════════════════════════════════════════════════════════

def score_sas(data):
    if not data:
        return 0.0
    score = 0.0
    summ = data.get("absence_summary", {})
    ar = summ.get("absence_rate", 0)
    if ar > sas_absence_high:
        score += 30 + min((ar - sas_absence_high) * 100, 10)
    elif ar > sas_absence_mid:
        score += 15 + (ar - sas_absence_mid) / max(sas_absence_high - sas_absence_mid, 0.01) * 15
    elif ar > sas_absence_low:
        score += (ar - sas_absence_low) / max(sas_absence_mid - sas_absence_low, 0.01) * 15

    clust = data.get("clustering", {})
    ratio = clust.get("cluster_ratio", 0)
    if ratio >= sas_cluster_flag * 1.5:
        score += 30
    elif ratio >= sas_cluster_flag:
        score += 20 + (ratio - sas_cluster_flag) / max(sas_cluster_flag * 0.5, 0.01) * 10
    elif ratio >= 1.0:
        score += (ratio - 1.0) / max(sas_cluster_flag - 1.0, 0.01) * 20

    dist = data.get("distribution", {})
    lr = dist.get("loss_absence_rate", 0)
    wr = dist.get("win_absence_rate", 0)
    if lr > 0 and wr > 0:
        skew = lr / wr
        if skew >= sas_skew_flag * 1.33:
            score += 30
        elif skew >= sas_skew_flag:
            score += 15 + (skew - sas_skew_flag) / max(sas_skew_flag * 0.33, 0.01) * 15
        elif skew >= 1.0:
            score += (skew - 1.0) / max(sas_skew_flag - 1.0, 0.01) * 15

    return min(round(score, 1), 100)


def score_nrci(data):
    if not data or data.get("error"):
        return 0.0
    score = 0.0
    rolling = data.get("rolling_net_rating", {})
    decline = rolling.get("max_decline", 0)
    if decline >= nrci_decline_max:
        score += 35
    elif decline >= nrci_decline_high:
        score += 20 + (decline - nrci_decline_high) / max(nrci_decline_max - nrci_decline_high, 0.01) * 15
    elif decline >= nrci_decline_mid:
        score += 5 + (decline - nrci_decline_mid) / max(nrci_decline_high - nrci_decline_mid, 0.01) * 15

    ppe = data.get("pre_post_elim", {})
    nr_change = ppe.get("net_rating_change", 0)
    if nr_change < nrci_collapse_severe:
        score += 35
    elif nr_change < nrci_collapse_mod:
        score += 20 + (abs(nr_change) - abs(nrci_collapse_mod)) / max(abs(nrci_collapse_severe) - abs(nrci_collapse_mod), 0.01) * 15
    elif nr_change < nrci_collapse_mild:
        score += 10 + (abs(nr_change) - abs(nrci_collapse_mild)) / max(abs(nrci_collapse_mod) - abs(nrci_collapse_mild), 0.01) * 10
    elif nr_change < 0:
        score += abs(nr_change) / max(abs(nrci_collapse_mild), 0.01) * 10

    q4 = data.get("q4_performance", {})
    close_wp = q4.get("close_game_win_pct", 0.5)
    if close_wp < nrci_close_wp_suspicious - 0.15:
        score += 30
    elif close_wp < nrci_close_wp_suspicious:
        score += 15 + (nrci_close_wp_suspicious - close_wp) / 0.15 * 15
    elif close_wp < nrci_close_wp_suspicious + 0.10:
        score += (nrci_close_wp_suspicious + 0.10 - close_wp) / 0.10 * 15

    return min(round(score, 1), 100)


def score_ris(data):
    if not data or data.get("error"):
        return 0.0
    score = 0.0
    changes = data.get("post_elim_changes", {})
    sd = changes.get("significant_decreases", 0)
    if sd >= ris_sig_decrease_high:
        score += 35
    elif sd >= ris_sig_decrease_mod:
        score += 20 + (sd - ris_sig_decrease_mod) / max(ris_sig_decrease_high - ris_sig_decrease_mod, 1) * 15
    elif sd >= 1:
        score += sd / max(ris_sig_decrease_mod, 1) * 20

    new_players = len(changes.get("new_rotation_players", []))
    score += min(new_players * ris_new_player_pts, 20)

    corr = data.get("quality_correlation", {})
    cs = corr.get("correlation_shift", 0)
    if cs < ris_corr_shift_flag * 2:
        score += 25
    elif cs < ris_corr_shift_flag:
        score += 10 + (abs(cs) - abs(ris_corr_shift_flag)) / max(abs(ris_corr_shift_flag), 0.01) * 15
    elif cs < 0:
        score += abs(cs) / max(abs(ris_corr_shift_flag), 0.01) * 10

    exp = data.get("experimentation", {})
    ei = exp.get("experimentation_increase", 0)
    if ei >= 2.0:
        score += 20
    elif ei >= 1.0:
        score += 10 + (ei - 1.0) * 10
    elif ei > 0:
        score += ei * 10

    return min(round(score, 1), 100)


def score_btca(data):
    if not data or data.get("error"):
        return 0.0
    score = 0.0

    lc = data.get("league_context", {})
    deviation = abs(lc.get("deviation_from_baseline", 0))
    if deviation >= 2.0:
        score += 30
    elif deviation >= 1.0:
        score += 15 + (deviation - 1.0) * 15
    else:
        score += deviation * 15

    tp = data.get("temporal_pattern", {})
    pct = tp.get("post_as_pct_of_pre", 100)
    if pct < btca_post_asb_flag * 0.6:
        score += 40
    elif pct < btca_post_asb_flag:
        score += 25 + (btca_post_asb_flag - pct) / max(btca_post_asb_flag * 0.4, 1) * 15
    elif pct < btca_post_asb_flag * 1.4:
        score += (btca_post_asb_flag * 1.4 - pct) / max(btca_post_asb_flag * 0.4, 1) * 25

    cc = data.get("calendar_correlation", {})
    periods = cc.get("periods", {})
    post = periods.get("Post-elimination", {})
    pewr = post.get("win_rate", 0.5)
    if pewr < btca_post_elim_wr * 0.5:
        score += 30
    elif pewr < btca_post_elim_wr:
        score += 15 + (btca_post_elim_wr - pewr) / max(btca_post_elim_wr * 0.5, 0.01) * 15
    elif pewr < btca_post_elim_wr + 0.10:
        score += (btca_post_elim_wr + 0.10 - pewr) / 0.10 * 15

    return min(round(score, 1), 100)


# ══════════════════════════════════════════════════════════════════════════
# MAIN SCOREBOARD
# ══════════════════════════════════════════════════════════════════════════

rows = []
for cid, d in all_data.items():
    sas = score_sas(d["SAS"])
    nrci = score_nrci(d["NRCI"])
    ris = score_ris(d["RIS"])
    btca = score_btca(d["BTCA"])

    composite = round(sas * w_sas + nrci * w_nrci + ris * w_ris + btca * w_btca, 1)
    cls = classify(composite)
    cls_plain = classify_plain(composite)
    expected = d["expected"]

    match_parts = [e.strip() for e in expected.split("/")]
    match = cls_plain in match_parts

    rows.append({
        "Case": cid,
        "Team": d["team"],
        "Season": d["season"],
        "SAS": sas,
        "NRCI": nrci,
        "RIS": ris,
        "BTCA": btca,
        "TII": composite,
        "Class": cls,
        "Expected": expected,
        "Match": "✅" if match else "❌",
    })

df = pd.DataFrame(rows)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
matches = sum(1 for r in rows if r["Match"] == "✅")
col1.metric("Cases Matching", f"{matches} / {len(rows)}")
col2.metric("Avg TII", f"{df['TII'].mean():.1f}")
col3.metric("Max TII", f"{df['TII'].max():.1f}")
col4.metric("Min TII", f"{df['TII'].min():.1f}")

st.markdown("---")

# Main scoreboard table
st.subheader("📊 All Cases — Live Scoring")

# Filters (defaults keep the view small)
show_dynamic = st.checkbox("Include dynamic cases", value=True)
show_only_pinned = st.checkbox("Show only pinned", value=False)
max_rows = st.slider("Max rows", 5, 100, 15, 5)

filtered_df = df.copy()

# Hide cases explicitly hidden
filtered_df = filtered_df[~filtered_df["Case"].apply(is_hidden)]

if not show_dynamic:
    # Built-in cases are single-letter IDs (A-H)
    filtered_df = filtered_df[filtered_df["Case"].str.len() == 1]

if show_only_pinned:
    filtered_df = filtered_df[filtered_df["Case"].apply(is_pinned)]

# Allow explicit selection (optional)
selected_cases = st.multiselect(
    "Filter cases (optional)",
    options=list(filtered_df["Case"].values),
    default=[],
)
if selected_cases:
    filtered_df = filtered_df[filtered_df["Case"].isin(selected_cases)]

# Sort: pinned first, then by TII desc
filtered_df = filtered_df.assign(_pinned=filtered_df["Case"].apply(is_pinned))
filtered_df = filtered_df.sort_values(by=["_pinned", "TII"], ascending=[False, False]).drop(columns=["_pinned"])

filtered_df = filtered_df.head(max_rows)

st.dataframe(
    filtered_df.style.apply(
        lambda row: [
            "background-color: #d4edda" if row["Match"] == "✅" else "background-color: #f8d7da"
        ]
        * len(row),
        axis=1,
    ),
    use_container_width=True,
    hide_index=True,
    height=350,
)

# ══════════════════════════════════════════════════════════════════════════
# PER-CASE DETAIL VIEW
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("🔎 Case Deep Dive")

selected_case = st.selectbox(
    "Select case",
    options=list(filtered_df["Case"].values) if len(filtered_df) > 0 else list(all_data.keys()),
    format_func=lambda c: f"Case {c}: {all_data[c]['team']} — {all_data[c]['season']}",
)

if selected_case:
    # Pin/hide controls
    cpin1, cpin2, cpin3 = st.columns([1, 1, 6])
    with cpin1:
        if st.button("📌 Pin" if not is_pinned(selected_case) else "📍 Unpin"):
            set_pref(selected_case, "pinned", not is_pinned(selected_case))
            st.rerun()
    with cpin2:
        if st.button("🙈 Hide"):
            set_pref(selected_case, "hidden", True)
            st.rerun()

    d = all_data[selected_case]
    row = [r for r in rows if r["Case"] == selected_case][0]
    supp = d.get("supplemental", {})

    # ── Header metrics ──────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SAS", f"{row['SAS']:.1f}",
              help="Star Availability Score (0-100). High = stars mysteriously absent.")
    c2.metric("NRCI", f"{row['NRCI']:.1f}",
              help="Net Rating Collapse Index (0-100). High = performance cratered.")
    c3.metric("RIS", f"{row['RIS']:.1f}",
              help="Rotation Integrity Score (0-100). High = lineup overhaul after elimination.")
    c4.metric("BTCA", f"{row['BTCA']:.1f}",
              help="Bottom-Tier Clustering (0-100). High = historically bad in context.")
    c5.metric("Composite", f"{row['TII']:.1f}", delta=row["Class"])

    st.caption(f"**Archetype:** {d['archetype']} | **Expected:** {d['expected']} | {row['Match']}")

    # ── Detailed component explanation tabs ──────────────────────────────
    tab_sas, tab_nrci, tab_ris, tab_btca, tab_supp = st.tabs([
        "⭐ SAS — Star Availability",
        "📉 NRCI — Performance Collapse",
        "🔄 RIS — Rotation Changes",
        "📊 BTCA — Historical Context",
        "🔍 Supplemental Indicators",
    ])

    # ── SAS tab ─────────────────────────────────────────────────────────
    with tab_sas:
        st.markdown("""
        **What this measures:** Whether the team's best players are sitting out
        more than expected, especially after the team is eliminated from
        playoff contention.

        *Think of it like this:* If a team's star suddenly starts "resting" or
        having mystery injuries right when the team has nothing to play for,
        that's a red flag.
        """)

        sas_d = d["SAS"]
        summ = sas_d.get("absence_summary", {})
        clust = sas_d.get("clustering", {})
        dist = sas_d.get("distribution", {})

        m1, m2, m3 = st.columns(3)
        m1.metric("Absence Rate",
                  f"{summ.get('absence_rate', 0):.1%}",
                  help="% of possible star-player game appearances that were missed")
        m2.metric("Cluster Ratio",
                  f"{clust.get('cluster_ratio', 0):.1f}x",
                  help="How many times more often stars miss games AFTER elimination vs before")
        lr = dist.get('loss_absence_rate', 0)
        wr = dist.get('win_absence_rate', 0)
        skew = round(lr / wr, 2) if wr > 0 else 0
        m3.metric("Loss/Win Skew",
                  f"{skew:.2f}x",
                  help="Ratio: are stars absent more in losses? >1.5 = suspicious")

        # Show qualified players
        qp = sas_d.get("qualified_players", [])
        if qp:
            st.markdown("**Qualified players** (25+ min/game starters):")
            qp_df = pd.DataFrame(qp)
            cols_show = ["player_name", "avg_minutes", "games_played", "games_missed",
                        "post_elim_missed", "loss_games_missed", "win_games_missed"]
            cols_show = [c for c in cols_show if c in qp_df.columns]
            st.dataframe(
                qp_df[cols_show].rename(columns={
                    "player_name": "Player",
                    "avg_minutes": "Avg Min",
                    "games_played": "GP",
                    "games_missed": "Missed",
                    "post_elim_missed": "Missed Post-Elim",
                    "loss_games_missed": "Missed in L",
                    "win_games_missed": "Missed in W",
                }),
                use_container_width=True, hide_index=True,
            )

    # ── NRCI tab ────────────────────────────────────────────────────────
    with tab_nrci:
        st.markdown("""
        **What this measures:** Whether the team's actual on-court performance
        (points scored vs. allowed per 100 possessions) collapsed, especially
        after playoff elimination.

        *Think of it like this:* Win-loss record can be noisy, but net rating
        (offense minus defense per 100 possessions) measures actual quality of
        play. A sharp drop signals the team stopped trying.
        """)

        nrci_d = d["NRCI"]
        if nrci_d.get("error"):
            st.warning(f"NRCI not available: {nrci_d['error']}")
        else:
            rolling = nrci_d.get("rolling_net_rating", {})
            ppe = nrci_d.get("pre_post_elim", {})
            q4 = nrci_d.get("q4_performance", {})

            m1, m2, m3 = st.columns(3)
            m1.metric("Max Decline (15-game window)",
                      f"{rolling.get('max_decline', 0):.1f} pts",
                      help="Biggest drop in rolling 15-game net rating from peak to trough")
            m2.metric("Post-Elim NR Change",
                      f"{ppe.get('net_rating_change', 0):+.1f}",
                      help="Difference in avg net rating after elimination vs before")
            m3.metric("Close Game Win %",
                      f"{q4.get('close_game_win_pct', 0):.1%}",
                      help="Win rate in games decided by 8 or fewer net rating points")

            # Season trajectory
            st.markdown(f"""
            **Season trajectory:**
            First 15 games NR: **{rolling.get('first_15_net_rating', '--')}** →
            Last 15 games NR: **{rolling.get('last_15_net_rating', '--')}**
            (Peak: {rolling.get('peak_rolling', '--')} at game {rolling.get('peak_game', '--')},
            Trough: {rolling.get('trough_rolling', '--')} at game {rolling.get('trough_game', '--')})
            """)

            if ppe.get("pre_elim_games"):
                st.markdown(f"""
                **Pre vs Post Elimination:**
                | Period | Games | Net Rating | Off Rating | Def Rating |
                |--------|-------|-----------|-----------|-----------|
                | Pre-elimination | {ppe.get('pre_elim_games', '--')} | {ppe.get('pre_elim_net_rating', '--')} | {ppe.get('pre_elim_off_rating', '--')} | {ppe.get('pre_elim_def_rating', '--')} |
                | Post-elimination | {ppe.get('post_elim_games', '--')} | {ppe.get('post_elim_net_rating', '--')} | {ppe.get('post_elim_off_rating', '--')} | {ppe.get('post_elim_def_rating', '--')} |
                """)

    # ── RIS tab ─────────────────────────────────────────────────────────
    with tab_ris:
        st.markdown("""
        **What this measures:** Whether the coach dramatically changed who
        plays after elimination — benching good players and giving minutes
        to unproven ones.

        *Think of it like this:* Every team experiments a little late in the
        season. But if 5+ starters suddenly lose 20%+ of their minutes and
        unknown players take their spots, that's a rotation overhaul designed
        to lose.
        """)

        ris_d = d["RIS"]
        if ris_d.get("error"):
            st.warning(f"RIS not available: {ris_d['error']}")
        else:
            changes = ris_d.get("post_elim_changes", {})
            corr = ris_d.get("quality_correlation", {})
            exp = ris_d.get("experimentation", {})

            m1, m2, m3 = st.columns(3)
            m1.metric("Players with major minute cuts",
                      changes.get("significant_decreases", 0),
                      help="Rotation players who lost 20%+ of their minutes after elimination")
            m2.metric("New rotation players",
                      len(changes.get("new_rotation_players", [])),
                      help="Players who entered the top-8 rotation ONLY after elimination")
            m3.metric("Merit correlation shift",
                      f"{corr.get('correlation_shift', 0):+.3f}",
                      help="Change in correlation between player quality and minutes. Negative = worse players getting more time")

            # Show rotation changes table
            ch_list = changes.get("changes", [])
            if ch_list:
                st.markdown("**Rotation changes (top-8 pre-elimination players):**")
                ch_df = pd.DataFrame(ch_list)
                st.dataframe(
                    ch_df.rename(columns={
                        "player_name": "Player",
                        "pre_avg_min": "Pre-Elim Min",
                        "post_avg_min": "Post-Elim Min",
                        "min_change": "Change",
                        "pct_change": "% Change",
                        "post_games": "Post GP",
                    }),
                    use_container_width=True, hide_index=True,
                )

            new_rot = changes.get("new_rotation_players", [])
            if new_rot:
                st.markdown("**New rotation players (post-elimination only):**")
                st.dataframe(pd.DataFrame(new_rot), use_container_width=True, hide_index=True)

    # ── BTCA tab ────────────────────────────────────────────────────────
    with tab_btca:
        st.markdown("""
        **What this measures:** How the team's losing fits into historical
        context, and whether the losing accelerated at specific calendar
        milestones (trade deadline, All-Star break, elimination).

        *Think of it like this:* Some teams are just bad. But tanking teams
        show a pattern: competitive before the trade deadline, then collapse
        after dealing their veterans for picks.
        """)

        btca_d = d["BTCA"]
        if btca_d.get("error"):
            st.warning(f"BTCA not available: {btca_d['error']}")
        else:
            lc = btca_d.get("league_context", {})
            tp = btca_d.get("temporal_pattern", {})
            cc = btca_d.get("calendar_correlation", {})

            m1, m2, m3 = st.columns(3)
            m1.metric("Final Record",
                      lc.get("team_record", "--"),
                      help="Team's win-loss record for the season")
            m2.metric("Post-ASB Win Rate",
                      f"{tp.get('post_asb_win_pct', 0):.1%}" if tp.get('post_asb_win_pct') else "--",
                      help="Win rate after the All-Star break")
            pct_of_pre = tp.get('post_as_pct_of_pre', None)
            m3.metric("Post-ASB % of Pre",
                      f"{pct_of_pre:.0f}%" if pct_of_pre else "--",
                      help="Post-ASB win rate as % of pre-ASB. Below 50% = dramatic collapse")

            # Calendar progression
            periods = cc.get("periods", {})
            if periods:
                st.markdown("**Win rate by calendar period:**")
                period_rows = []
                for period_name, period_data in periods.items():
                    period_rows.append({
                        "Period": period_name,
                        "Record": period_data.get("record", "--"),
                        "Win Rate": f"{period_data.get('win_rate', 0):.1%}",
                        "Games": period_data.get("games", 0),
                    })
                st.dataframe(pd.DataFrame(period_rows), use_container_width=True, hide_index=True)

            # Bottom-6 context
            b6 = lc.get("bottom_6_teams", [])
            if b6:
                st.markdown("**Bottom 6 teams this season:**")
                for team_name, wins in b6:
                    marker = " ← this team" if wins == lc.get("team_wins") else ""
                    st.text(f"  {team_name}: {wins} wins{marker}")

    # ── Supplemental indicators tab ─────────────────────────────────────
    with tab_supp:
        st.markdown("""
        **These indicators don't factor into the TII score** but provide
        important context that helps distinguish tanking from legitimate
        rebuilding. They address blind spots in the core 4 components.
        """)

        if not supp:
            st.info("Supplemental data not computed yet. Run `python tii.py compute --all` to generate.")
        else:
            # Draft Position
            dpi = supp.get("draft_pick_incentive", {})
            if dpi and not dpi.get("error"):
                st.markdown("---")
                st.markdown("#### 🎯 Draft Pick Incentive")
                st.markdown("""
                *Where did the team end up in the draft lottery? Teams with
                worse records get better picks, creating an incentive to lose.*
                """)
                d1, d2, d3 = st.columns(3)
                d1.metric("Draft Position",
                          f"#{dpi.get('draft_position', '?')}",
                          help="1 = worst record (best lottery odds)")
                d2.metric("In Bottom 5?",
                          "Yes 🚩" if dpi.get("in_bottom_5") else "No ✓",
                          help="Bottom 5 records get the best lottery odds")
                d3.metric("Wins Gap to Next Better",
                          f"{dpi.get('wins_gap_to_next_better', '?')} wins",
                          help="How many more wins would have moved them up (worse draft position)")

            # Veteran Shelving
            vsi = supp.get("veteran_shelving", {})
            if vsi and not vsi.get("error"):
                st.markdown("---")
                st.markdown("#### 🪑 Veteran Shelving")
                st.markdown("""
                *Did any veterans who were playing significant minutes suddenly
                get benched after elimination? This catches cases like Al Horford
                in OKC where a player is technically available but doesn't play.*
                """)
                v1, v2, v3 = st.columns(3)
                v1.metric("Total Players Used",
                          vsi.get("total_players_used", 0),
                          help="Total unique players who appeared in games")
                v2.metric("Regular Rotation Size",
                          vsi.get("regular_rotation_size", 0),
                          help="Players who played 40%+ of games with 15+ min/game")
                v3.metric("Shelved Post-Elim",
                          vsi.get("shelved_count", 0),
                          help="Players who had 15+ min pre-elimination but <5 min after")

                shelved = vsi.get("shelved_post_elim", [])
                if shelved:
                    st.markdown("**Players shelved after elimination:**")
                    st.dataframe(
                        pd.DataFrame(shelved).rename(columns={
                            "player_name": "Player",
                            "pre_avg_min": "Pre-Elim Min",
                            "post_avg_min": "Post-Elim Min",
                            "pre_games": "Pre GP",
                            "post_games": "Post GP",
                            "minutes_drop": "Min Drop",
                        }),
                        use_container_width=True, hide_index=True,
                    )

            # Margin of Defeat Profile
            mdp = supp.get("margin_profile", {})
            if mdp and not mdp.get("error"):
                st.markdown("---")
                st.markdown("#### 📏 Margin of Defeat Profile")
                st.markdown("""
                *Are the losses competitive or blowouts? A high blowout rate
                combined with a worsening trajectory suggests the team isn't
                trying to keep games close.*
                """)
                md1, md2, md3, md4 = st.columns(4)
                md1.metric("Avg Loss Margin",
                          f"{mdp.get('avg_loss_margin', 0):+.1f}",
                          help="Average net rating in losses (more negative = bigger blowouts)")
                md2.metric("Blowout Loss %",
                          f"{mdp.get('blowout_loss_pct', 0):.0%}",
                          help="% of losses that were blowouts (net rating < -15)")
                md3.metric("1st→2nd Half Trajectory",
                          f"{mdp.get('trajectory', 0):+.1f}",
                          help="Change in net rating from first half to second half of season. Negative = got worse.")
                post_m = mdp.get('post_elim_avg_margin')
                pre_m = mdp.get('pre_elim_avg_margin')
                if post_m is not None and pre_m is not None:
                    md4.metric("Post-Elim Margin",
                              f"{post_m:+.1f}",
                              delta=f"{post_m - pre_m:+.1f} vs pre",
                              help="Average net rating after elimination")
                else:
                    md4.metric("Post-Elim Margin", "--")

            # Lineup Overhaul / Trade Deadline
            loi = supp.get("lineup_overhaul", {})
            if loi and not loi.get("error"):
                td = loi.get("trade_deadline", {})
                if td:
                    st.markdown("---")
                    st.markdown("#### 🔄 Trade Deadline Roster Churn")
                    st.markdown(f"""
                    *How many meaningful rotation players were traded away at the
                    deadline? Dealing veterans for picks is a classic tanking move.*

                    Trade deadline: **{td.get('date', '--')}**
                    """)
                    t1, t2, t3 = st.columns(3)
                    t1.metric("Meaningful Players Departed",
                              td.get("meaningful_departed", 0),
                              help="Rotation players (10+ min/game) who left at the deadline")
                    t2.metric("Meaningful Players Arrived",
                              td.get("meaningful_arrived", 0),
                              help="New rotation players acquired at the deadline")
                    t3.metric("Total Roster Churn",
                              td.get("roster_churn", 0),
                              help="Total players who departed + arrived around the deadline")

                    departed = td.get("departed_players", [])
                    if departed:
                        st.markdown("**Key departures:**")
                        for dp in departed:
                            st.text(f"  {dp['player_name']} ({dp['avg_min_before']} min/game)")

                    arrived = td.get("arrived_players", [])
                    if arrived:
                        st.markdown("**Key arrivals:**")
                        for ap in arrived:
                            st.text(f"  {ap['player_name']} ({ap['avg_min_after']} min/game)")

    # ── Bar chart showing component breakdown ───────────────────────────
    st.markdown("---")
    st.subheader("📊 Component Breakdown")
    chart_df = pd.DataFrame({
        "Component": ["SAS", "NRCI", "RIS", "BTCA"],
        "Raw Score": [row["SAS"], row["NRCI"], row["RIS"], row["BTCA"]],
        "Weighted": [
            round(row["SAS"] * w_sas, 1),
            round(row["NRCI"] * w_nrci, 1),
            round(row["RIS"] * w_ris, 1),
            round(row["BTCA"] * w_btca, 1),
        ],
    })
    st.bar_chart(chart_df.set_index("Component"))


# ══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION BOUNDARY VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📏 Classification Boundaries")

boundary_df = pd.DataFrame(rows)
boundary_df = boundary_df.sort_values("TII", ascending=False)

for _, r in boundary_df.iterrows():
    bar_width = int(r["TII"])
    st.markdown(
        f"**Case {r['Case']}** ({r['Team']} {r['Season']}): "
        f"`{'█' * (bar_width // 2)}{'░' * ((100 - bar_width) // 2)}` "
        f"**{r['TII']:.1f}** {r['Class']} {r['Match']}"
    )

st.caption(
    f"Boundaries: 🟢 0-{green_max} | 🟡 {green_max+1}-{yellow_max} | "
    f"🟠 {yellow_max+1}-{orange_max} | 🔴 {orange_max+1}-100"
)


# ══════════════════════════════════════════════════════════════════════════
# GLOSSARY
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
with st.expander("📚 Glossary — Key terms explained"):
    st.markdown("""
| Term | Definition |
|------|-----------|
| **Net Rating** | Points scored minus points allowed per 100 possessions. The best single measure of how good a team actually is. League average is ~0. Elite teams are +8 to +12. Terrible teams are -8 to -12. |
| **Offensive/Defensive Rating** | Points scored (or allowed) per 100 possessions. Higher offensive rating = better offense. Lower defensive rating = better defense. |
| **Pace** | Number of possessions per 48 minutes. Higher pace = faster-playing team. |
| **True Shooting %** | A shooting efficiency metric that accounts for 2-pointers, 3-pointers, and free throws. League average is around 57%. |
| **Usage Rate** | Percentage of team possessions a player uses while on court. Stars typically have 25-30%+ usage. |
| **Qualified Player** | For SAS purposes: a player averaging 25+ minutes per game. These are the team's core players whose absences most impact winning. |
| **Mathematical Elimination** | The point in the season where a team cannot possibly win enough remaining games to catch the last playoff spot. |
| **All-Star Break (ASB)** | Mid-February break in the season. A natural dividing line — teams that collapse after ASB may be tanking. |
| **Trade Deadline** | Date (usually early February) after which teams cannot trade players until the offseason. Teams often dump veterans for picks before this date. |
| **Rolling Window** | A 15-game moving average. Smooths out game-to-game noise to show trends. |
| **Correlation Shift** | Change in the statistical relationship between player quality and playing time. If it goes negative, the coach is giving minutes to worse players — a sign of tanking. |
| **Blowout** | A game where the net rating was worse than -15. These are not competitive games. |
| **Close Game** | A game where the net rating was between -8 and +8. These are competitive games where effort matters most. |
| **Cluster Ratio** | The ratio of star absences after elimination to before. A ratio of 2.0 means stars miss twice as many games post-elimination. |
""")
