"""Área principal según el modo activo."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chordia.chords import row_note_set
from chordia.constants import MODE_DICTIONARY, MODE_IDENTIFIER, ORDEN_TIPOS
from chordia.config import GITHUB_RAW_BASE
from chordia.display import render_chord_detail


def render_main_dictionary(raiz_sel: str, df_raiz: pd.DataFrame) -> None:
    st.header(f"📖 Diccionario: {raiz_sel}")
    tipos_visibles = [t for t in ORDEN_TIPOS if t in st.session_state.seleccionados]
    if not tipos_visibles:
        st.info("Seleccioná tipos en el sidebar.")
        return
    tabs = st.tabs(tipos_visibles)
    for i, tab in enumerate(tabs):
        with tab:
            row = df_raiz[df_raiz["Naturaleza"] == tipos_visibles[i]].iloc[0]
            render_chord_detail(row, GITHUB_RAW_BASE)


def render_main_identifier(df: pd.DataFrame) -> None:
    st.header("🔍 Identificador de Acordes")
    notas_act = {n.strip() for n in st.session_state.notas_inversas}
    res = df[
        df.apply(lambda r: row_note_set(r) == notas_act, axis=1)
    ]
    if not notas_act:
        st.info("Seleccioná notas en la barra lateral.")
        return
    if res.empty:
        st.warning("Acorde no identificado.")
        return
    render_chord_detail(res.iloc[0], GITHUB_RAW_BASE)


def render_main(modo: str, df: pd.DataFrame, raiz_sel: str, df_raiz: pd.DataFrame | None) -> None:
    if modo == MODE_DICTIONARY and df_raiz is not None:
        render_main_dictionary(raiz_sel, df_raiz)
    elif modo == MODE_IDENTIFIER:
        render_main_identifier(df)
