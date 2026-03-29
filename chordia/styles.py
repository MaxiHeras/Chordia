"""CSS global inyectado en Streamlit."""

import streamlit as st


def inject_custom_css() -> None:
    st.markdown(
        """
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    /* Aire bajo la barra de Streamlit (toolbar + safe area en móvil). */
    .block-container { padding-top: 2.75rem !important; padding-bottom: 0rem !important; }
    .main .block-container { padding-top: 2.75rem !important; }
    [data-testid="block-container"] { padding-top: 2.75rem !important; }
    .main h1, .main h2, .main h3 { padding-top: 0.35rem !important; margin-top: 0.5rem !important; }
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
        min-width: 840px;
    }
    .scale-grid-wrap {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .scale-degree {
        text-align: center;
        font-weight: 600;
        color: var(--text-color, #6b7280);
        font-size: 0.9rem;
    }
    .scale-note {
        text-align: center;
        border: 1px solid var(--border-color, #D1D5DB);
        border-radius: 8px;
        padding: 8px 4px;
        font-weight: 700;
        background: var(--secondary-background-color, rgba(255,255,255,0.65));
        color: var(--text-color, inherit);
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .scale-step {
        text-align: center;
        font-size: 0.78rem;
        color: var(--text-color, #6b7280);
        font-weight: 600;
        border: 1px solid var(--border-color, #D1D5DB);
        border-radius: 8px;
        padding: 4px 2px;
        background: var(--secondary-background-color, rgba(255,255,255,0.35));
    }
    .scale-structure-caption {
        margin-top: 26px;
        color: var(--text-color, inherit);
    }
    .harmony-degrees-row {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 6px 10px;
        margin-top: 8px;
        margin-bottom: 4px;
        min-width: 680px;
    }
    .harmony-chords-row {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 8px 10px;
        margin-top: 0;
        margin-bottom: 8px;
        min-width: 680px;
    }
    .harmony-wrap {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .harmony-degree {
        text-align: center;
        font-weight: 600;
        color: var(--text-color, #6b7280);
        font-size: 0.9rem;
    }
    .harmony-chord {
        text-align: center;
        border: 1px solid var(--border-color, #D1D5DB);
        border-radius: 8px;
        padding: 8px 4px;
        font-weight: 700;
        background: var(--secondary-background-color, rgba(255,255,255,0.5));
        color: var(--text-color, inherit);
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .c1 { grid-column: 1; } .c2 { grid-column: 2; } .c3 { grid-column: 3; } .c4 { grid-column: 4; } .c5 { grid-column: 5; }
    .c6 { grid-column: 6; } .c7 { grid-column: 7; } .c8 { grid-column: 8; } .c9 { grid-column: 9; } .c10 { grid-column: 10; }
    .c11 { grid-column: 11; } .c12 { grid-column: 12; } .c13 { grid-column: 13; } .c14 { grid-column: 14; } .c15 { grid-column: 15; }

    /* Compacta: NO comprimir el grid al ancho del celular (eso aplasta "Eb", intervalos, etc.). Scroll horizontal como la vista completa. */
    .scale-grid-wrap.compact-mode {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    .harmony-wrap.compact-mode {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    .scale-grid-wrap.compact-mode .scale-grid {
        min-width: 720px;
        gap: 10px 8px;
        align-items: stretch;
        grid-template-columns:
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr) minmax(3.35rem, 0.52fr)
            minmax(3.35rem, 1fr);
    }
    .harmony-wrap.compact-mode .harmony-degrees-row,
    .harmony-wrap.compact-mode .harmony-chords-row {
        min-width: 640px;
        gap: 8px 8px;
    }
    .harmony-wrap.compact-mode .harmony-degree,
    .harmony-wrap.compact-mode .harmony-chord {
        white-space: normal;
        word-break: break-word;
        line-height: 1.05;
    }
    .scale-grid-wrap.compact-mode .scale-step {
        white-space: nowrap;
        word-break: normal;
        line-height: 1.2;
        font-size: 0.74rem;
        padding: 6px 5px;
        min-width: 3.35rem;
        box-sizing: border-box;
    }
    .scale-grid-wrap.compact-mode .scale-note {
        white-space: nowrap;
        word-break: normal;
        line-height: 1.2;
        min-height: 44px;
        font-size: 0.88rem;
        padding: 8px 6px;
        min-width: 3.1rem;
        box-sizing: border-box;
    }
    .scale-grid-wrap.compact-mode .scale-degree {
        font-size: 0.78rem;
        line-height: 1.25;
        padding-bottom: 2px;
    }
    .harmony-wrap.compact-mode .harmony-degree {
        font-size: 0.78rem;
    }
    .harmony-wrap.compact-mode .harmony-chord {
        min-height: 38px;
        font-size: 0.76rem;
        padding: 6px 5px;
        line-height: 1.15;
    }

    @media (max-width: 768px) {
        .block-container { padding-top: 2.35rem !important; }
        .main .block-container { padding-top: 2.35rem !important; }
        [data-testid="block-container"] { padding-top: 2.35rem !important; }
        .scale-grid { min-width: 760px; gap: 5px; }
        .scale-note { min-height: 38px; font-size: 0.85rem; padding: 6px 3px; }
        .scale-degree { font-size: 0.8rem; }
        .scale-step { font-size: 0.72rem; padding: 3px 2px; }
        .scale-structure-caption { margin-top: 18px; font-size: 0.82rem; }
        .harmony-degrees-row, .harmony-chords-row { min-width: 620px; gap: 6px 8px; }
        .harmony-degree { font-size: 0.8rem; }
        .harmony-chord { min-height: 34px; font-size: 0.82rem; padding: 6px 3px; }
    }

    @media (max-width: 430px) {
        .scale-grid-wrap.compact-mode .scale-note {
            font-size: 0.78rem;
            min-height: 38px;
            padding: 6px 5px;
        }
        .scale-grid-wrap.compact-mode .scale-step {
            font-size: 0.7rem;
            min-width: 3.15rem;
            padding: 5px 4px;
        }
        .scale-grid-wrap.compact-mode .scale-degree {
            font-size: 0.74rem;
        }
        .harmony-wrap.compact-mode .harmony-chord {
            font-size: 0.6rem;
            min-height: 27px;
        }
    }

    .rel-comp-wrap {
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
        margin-top: 12px;
        margin-bottom: 16px;
    }
    .rel-comp-table {
        border-collapse: collapse;
        table-layout: fixed;
        width: 100%;
        min-width: 640px;
        font-size: 0.92rem;
        margin-bottom: 20px;
    }
    .rel-comp-col-corner { width: 52px; min-width: 52px; max-width: 52px; }
    .rel-comp-col-label { width: 62px; min-width: 62px; max-width: 62px; }
    /* Las 7 columnas de datos sin ancho explícito reparten el mismo trozo en layout fijo. */
    .rel-comp-col-data { width: auto; }
    .rel-comp-table th, .rel-comp-table td {
        border: 1px solid var(--border-color, #cbd5e1);
        padding: 8px 6px;
        text-align: center;
        vertical-align: middle;
    }
    .rel-comp-corner {
        background: var(--secondary-background-color, #f1f5f9);
        color: var(--text-color, #0f172a);
        font-weight: 700;
        font-size: 0.72rem;
        line-height: 1.15;
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        white-space: nowrap;
    }
    .rel-comp-vtitle {
        display: inline-block;
        letter-spacing: 0.04em;
    }
    .rel-comp-left {
        background: var(--secondary-background-color, #f8fafc);
        color: var(--text-color, #0f172a);
        font-weight: 600;
        text-align: left !important;
        font-size: 0.82rem;
        overflow: hidden;
    }
    .rel-comp-cell {
        font-weight: 600;
        background: var(--background-color, #ffffff);
        color: var(--text-color, #0f172a);
    }
    .rel-comp-spacer-row th.rel-comp-left,
    .rel-comp-table td.rel-comp-spacer {
        background: var(--secondary-background-color, #f8fafc) !important;
    }
    .rel-comp-spacer-row td.rel-comp-spacer {
        border-color: var(--border-color, #e2e8f0);
    }
    .rel-comp-strong {
        color: var(--text-color, #0f172a);
    }
    .rel-comp-deg {
        color: var(--text-color, #64748b);
        font-weight: 700;
    }
    .rel-comp-q {
        font-weight: 700;
    }
    .rel-comp-q-mayor { background: #8fd18f !important; color: #052e16; }
    .rel-comp-q-menor { background: #fef08a !important; color: #713f12; }
    .rel-comp-q-dism { background: #fdba74 !important; color: #0f172a; }
    .rel-comp-q-aum { background: #93c5fd !important; color: #0f172a; }
    .rel-comp-q-same { background: #94a3b8 !important; color: #0f172a; }
    .rel-comp-compact .rel-comp-table {
        font-size: 0.78rem;
        min-width: 0;
    }
    .rel-comp-compact .rel-comp-col-corner {
        width: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        font-size: 0.65rem;
        padding: 4px 2px !important;
    }
    .rel-comp-compact .rel-comp-col-label {
        width: 54px !important;
        min-width: 54px !important;
        max-width: 54px !important;
    }
    .rel-comp-compact .rel-comp-q {
        font-size: 0.68rem;
        letter-spacing: -0.03em;
        white-space: nowrap;
    }
    .rel-comp-compact .rel-comp-table th,
    .rel-comp-compact .rel-comp-table td {
        padding: 5px 3px;
    }

    /* Tema oscuro del SO: refuerzo si Streamlit sigue en claro (poco habitual). Tablas usan variables de tema arriba. */
    @media (prefers-color-scheme: dark) {
        .stTextInput input:disabled {
            -webkit-text-fill-color: #e2e8f0 !important;
            background-color: #1e293b !important;
            border-color: #475569 !important;
            color: #e2e8f0 !important;
        }
    }
    </style>
""",
        unsafe_allow_html=True,
    )
