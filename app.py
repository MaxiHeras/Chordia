"""Punto de entrada Streamlit para Chordia."""

import streamlit as st

from chordia.config import PAGE_TITLE
from chordia.data import load_chords
from chordia.session import ensure_session_defaults
from chordia.styles import inject_custom_css
from chordia.ui.main_panel import render_main
from chordia.ui.sidebar import render_sidebar


def main() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()
    ensure_session_defaults()

    df = load_chords()
    if df is None:
        st.error("No se pudieron cargar los datos. Reintentá más tarde.")
        return

    with st.sidebar:
        modo, raiz_sel, df_raiz = render_sidebar(df)

    render_main(modo, df, raiz_sel, df_raiz)


if __name__ == "__main__":
    main()
