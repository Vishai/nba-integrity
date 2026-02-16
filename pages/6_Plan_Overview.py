"""Plan Overview — NBA Stewardship Reform Plan rendered in-app.

Reads the markdown source document and presents it in navigable,
collapsible sections so readers can explore the full plan without
leaving the Streamlit dashboard.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

PLAN_PATH = Path(__file__).resolve().parent.parent / "NBA Stewardship Reform Plan.md"


@st.cache_data
def load_plan_sections():
    """Parse the plan markdown into titled sections split on '## ' headers."""
    text = PLAN_PATH.read_text()
    lines = text.split("\n")

    sections = []
    current_title = None
    current_lines = []

    for line in lines:
        if line.startswith("## ") and current_title is not None:
            sections.append((current_title, "\n".join(current_lines)))
            current_title = line[3:].strip()
            current_lines = []
        elif line.startswith("## "):
            # First ## header — capture everything before it as preamble title
            if current_lines:
                sections.append(("Header", "\n".join(current_lines)))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Capture final section
    if current_title and current_lines:
        sections.append((current_title, "\n".join(current_lines)))

    return sections


# ── Page content ────────────────────────────────────────────────────────
st.title("NBA Stewardship Reform Plan")
st.caption("A Framework for Competitive Integrity Through Positive Incentive Architecture")

st.markdown("""
**Version:** 1.0 — Phase 1 Working Draft
**Author:** Brandon Armstrong
**Status:** In Development

---

This page renders the complete Stewardship Reform Plan document.
Each major section is presented as an expandable panel — click any
section header to read its contents. For interactive exploration of
specific framework components, use the appendix pages in the sidebar.
""")

if not PLAN_PATH.exists():
    st.error(f"Plan document not found at `{PLAN_PATH}`")
    st.stop()

sections = load_plan_sections()

# ── Quick navigation ────────────────────────────────────────────────────
st.subheader("Document Outline")
section_labels = []
for title, _ in sections:
    if title == "Header":
        continue
    section_labels.append(title)

# Show a compact outline with roman numeral sections
cols = st.columns(3)
for i, label in enumerate(section_labels):
    cols[i % 3].markdown(f"- {label}")

st.markdown("---")

# ── Render sections ─────────────────────────────────────────────────────
# Map sections to appendix pages for cross-linking
APPENDIX_LINKS = {
    "Appendices (To Be Developed)": True,
}

for title, body in sections:
    if title == "Header":
        # This is the title + subtitle block — already rendered above
        continue

    # Determine which sections should be open by default
    # Open Preamble and Core Philosophy by default for first-time readers
    default_open = title in ("Preamble", "I. Core Philosophy")

    with st.expander(f"**{title}**", expanded=default_open):
        st.markdown(body)

# ── Footer ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
📖 **Reading guide:** This document is the canonical source for the
Stewardship Reform Plan. The interactive appendix pages (accessible via
the sidebar) provide deeper exploration of specific framework components:

| Appendix | Interactive Page |
|----------|-----------------|
| **A** — Historical Backtesting | TII Calibration Dashboard |
| **B** — SP Scoring Matrix | SP Scoring Matrix |
| **C** — SSL Prize Structure | SSL Prize Structure |
| **D** — ETP Governance | ETP Simulator |
| **E** — Scenario Walkthroughs | Scenario Walkthroughs |
| **F** — Implementation Timeline | Implementation Timeline |
""")
