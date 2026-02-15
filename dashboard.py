"""NBA Stewardship Reform Plan — Multi-page Streamlit App.

Entrypoint / router. Run with:
    streamlit run dashboard.py
"""

import sys
from pathlib import Path

# Ensure tii package is importable from pages/
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="NBA Stewardship Reform Plan",
    page_icon="🏀",
    layout="wide",
)

# ── Define pages ─────────────────────────────────────────────────────────
pages = {
    "Appendix A": [
        st.Page("pages/0_TII_Calibration_Dashboard.py",
                title="TII Calibration Dashboard", icon="🏀", default=True),
    ],
    "Framework Appendices": [
        st.Page("pages/3_Appendix_B_SP_Scoring_Matrix.py",
                title="B — SP Scoring Matrix", icon="⭐"),
        st.Page("pages/4_Appendix_C_SSL_Prize_Structure.py",
                title="C — SSL Prize Structure", icon="🏆"),
        st.Page("pages/2_Appendix_D_ETP_Simulator.py",
                title="D — ETP Simulator", icon="🎰"),
        st.Page("pages/1_Appendix_E_Scenario_Walkthroughs.py",
                title="E — Scenario Walkthroughs", icon="📋"),
        st.Page("pages/5_Appendix_F_Implementation_Timeline.py",
                title="F — Implementation Timeline", icon="📅"),
    ],
}

pg = st.navigation(pages)
pg.run()
