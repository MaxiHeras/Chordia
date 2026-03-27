"""CSS global inyectado en Streamlit."""

import streamlit as st


def inject_custom_css() -> None:
    st.markdown(
        """
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    div[data-testid="stRadio"] > div { gap: 20px; margin-top: 10px; }
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex !important; overflow-x: auto !important; gap: 15px !important; padding: 10px 0 !important; flex-wrap: nowrap !important; }
    .chord-diag-item { flex: 0 0 auto !important; width: 150px !important; text-align: center; }
    .chord-img-web { width: 100% !important; height: auto !important; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 5px !important; }
    [data-testid="stSidebar"] [data-testid="column"] { width: 32% !important; flex: 1 1 32% !important; min-width: 32% !important; }
    .stButton > button { width: 100% !important; padding: 5px 2px !important; font-size: 13px !important; min-height: 42px !important; border-radius: 6px !important; }
    .stTextInput input:disabled {
        -webkit-text-fill-color: #31333F !important;
        opacity: 1 !important;
        cursor: text !important;
        background-color: #f0f2f6 !important;
        font-family: monospace !important;
    }
    .scale-grid {
        display: grid;
        grid-template-columns:
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr) minmax(0, 0.5fr)
            minmax(0, 1fr);
        gap: 6px;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 6px;
    }
    .scale-degree {
        text-align: center;
        font-weight: 600;
        color: #6b7280;
        font-size: 0.9rem;
    }
    .scale-note {
        text-align: center;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 8px 4px;
        font-weight: 700;
        background: rgba(255,255,255,0.5);
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .scale-step {
        text-align: center;
        font-size: 0.78rem;
        color: #6b7280;
        font-weight: 600;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 4px 2px;
        background: rgba(255,255,255,0.35);
    }
    .scale-structure-caption {
        margin-top: 26px;
    }
    .c1 { grid-column: 1; } .c2 { grid-column: 2; } .c3 { grid-column: 3; } .c4 { grid-column: 4; } .c5 { grid-column: 5; }
    .c6 { grid-column: 6; } .c7 { grid-column: 7; } .c8 { grid-column: 8; } .c9 { grid-column: 9; } .c10 { grid-column: 10; }
    .c11 { grid-column: 11; } .c12 { grid-column: 12; } .c13 { grid-column: 13; } .c14 { grid-column: 14; } .c15 { grid-column: 15; }
    </style>
""",
        unsafe_allow_html=True,
    )
