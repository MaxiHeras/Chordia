"""Área principal según el modo activo."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chordia.chords import row_note_set
from chordia.constants import (
    MODE_DICTIONARY,
    MODE_IDENTIFIER,
    MODE_SCALE_HARMONIZATION,
    MODE_SCALES,
    ORDEN_TIPOS,
)
from chordia.config import GITHUB_RAW_BASE
from chordia.display import render_chord_detail
from chordia.scales import build_scale, detect_scale_columns, parse_scale_steps, render_scale_grid


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


def render_main_scales(scales_df: pd.DataFrame | None) -> None:
    st.header("🎼 Escalas")
    if scales_df is None:
        st.warning("No se pudo cargar la hoja de escalas.")
        return

    type_col, struct_col = detect_scale_columns(scales_df)
    if not type_col or not struct_col:
        st.warning("La hoja de escalas no tiene columnas compatibles (tipo y estructura).")
        return

    selected_types = st.session_state.get("scales_selected_types", [])
    root = st.session_state.get("scale_root", "C")
    if not selected_types:
        st.info("Seleccioná al menos un tipo de escala en el sidebar.")
        return

    tabs = st.tabs(selected_types)
    for i, scale_type in enumerate(selected_types):
        with tabs[i]:
            matches = scales_df[scales_df[type_col].astype(str).str.strip() == str(scale_type).strip()]
            if matches.empty:
                st.warning("No se encontró la escala seleccionada en la hoja.")
                continue
            row = matches.iloc[0]
            raw_structure = str(row.get(struct_col, "")).strip()
            steps = parse_scale_steps(raw_structure)
            if not steps:
                st.warning("No se pudo interpretar la estructura de la escala.")
                continue
            notes = build_scale(root, steps)
            st.subheader(f"{root} {scale_type}")
            render_scale_grid(notes, steps)
            st.markdown(
                f'<div class="scale-structure-caption">Estructura: {raw_structure}</div>',
                unsafe_allow_html=True,
            )


def render_main_scale_harmonization() -> None:
    st.header("🎶 Armonización de escalas")
    st.info("Sección en construcción. Aquí vamos a desarrollar la armonización de escalas.")


def render_main(
    modo: str,
    df: pd.DataFrame,
    raiz_sel: str,
    df_raiz: pd.DataFrame | None,
    scales_df: pd.DataFrame | None,
) -> None:
    if modo == MODE_DICTIONARY and df_raiz is not None:
        render_main_dictionary(raiz_sel, df_raiz)
    elif modo == MODE_IDENTIFIER:
        render_main_identifier(df)
    elif modo == MODE_SCALES:
        render_main_scales(scales_df)
    elif modo == MODE_SCALE_HARMONIZATION:
        render_main_scale_harmonization()
