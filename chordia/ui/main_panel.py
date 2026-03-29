"""Área principal según el modo activo."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chordia.chords import match_rows_by_note_set
from chordia.constants import (
    MODE_DICTIONARY,
    MODE_IDENTIFIER,
    MODE_RELATIVE_COMPARISON,
    MODE_SCALE_HARMONIZATION,
    MODE_SCALES,
    ORDEN_TIPOS,
)
from chordia.config import GITHUB_RAW_BASE
from chordia.display import render_chord_detail
from chordia.harmonization import (
    build_harmonized_chords,
    detect_harmonization_columns,
    parse_harmony_structure,
    render_harmonization_result,
)
from chordia.relative_comparison import build_comparison_data, render_relative_comparison_html
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
    res = match_rows_by_note_set(df, notas_act)
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
    compact = st.session_state.get("mobile_content_view_mode", "completa") == "compacta"
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
            render_scale_grid(notes, steps, compact=compact)
            cap_cls = (
                "scale-structure-caption scale-structure-caption--compact"
                if compact
                else "scale-structure-caption"
            )
            st.markdown(
                f'<div class="{cap_cls}">Estructura: {raw_structure}</div>',
                unsafe_allow_html=True,
            )


def render_main_scale_harmonization(
    harmony_df: pd.DataFrame | None,
    scales_df: pd.DataFrame | None,
) -> None:
    st.header("🎶 Armonización de escalas")
    if harmony_df is None:
        st.warning("No se pudo cargar la hoja de armonización de escalas.")
        return

    type_col, struct_col, _, _ = detect_harmonization_columns(harmony_df)
    if not type_col or not struct_col:
        st.warning("La hoja de armonización no tiene columnas compatibles.")
        return
    if scales_df is None:
        st.warning("No se pudo cargar la hoja de escalas.")
        return
    scale_type_col, scale_struct_col = detect_scale_columns(scales_df)
    if not scale_type_col or not scale_struct_col:
        st.warning("La hoja de escalas no tiene columnas compatibles.")
        return

    selected_types = st.session_state.get("arm_selected_types", [])
    root = st.session_state.get("arm_root", "C")
    if not selected_types:
        st.info("Seleccioná al menos un tipo en el sidebar.")
        return

    tabs = st.tabs(selected_types)
    compact = st.session_state.get("mobile_content_view_mode", "completa") == "compacta"
    for i, scale_type in enumerate(selected_types):
        with tabs[i]:
            matches = harmony_df[harmony_df[type_col].astype(str).str.strip() == str(scale_type).strip()]
            if matches.empty:
                st.warning("No se encontró el tipo seleccionado en la hoja.")
                continue
            row = matches.iloc[0]
            harmony_structure = str(row.get(struct_col, "")).strip()
            harmony_tokens = parse_harmony_structure(harmony_structure)
            if len(harmony_tokens) != 7:
                st.warning("No se pudo interpretar la estructura de armonización (7 grados).")
                continue

            scale_match = scales_df[scales_df[scale_type_col].astype(str).str.strip() == str(scale_type).strip()]
            if scale_match.empty:
                st.warning("No se encontró la estructura de escala para este tipo.")
                continue
            raw_structure = str(scale_match.iloc[0].get(scale_struct_col, "")).strip()
            steps = parse_scale_steps(raw_structure)
            if not steps:
                st.warning("No se pudo interpretar la estructura de la escala.")
                continue
            notes, chords = build_harmonized_chords(root, steps, harmony_tokens)
            render_harmonization_result(root, scale_type, raw_structure, notes, chords, steps, compact=compact)


def render_main_relative_comparison() -> None:
    st.header("⚖️ Relativas y comparación")
    maj = st.session_state.get("rel_comp_maj_root", "C")
    mn = st.session_state.get("rel_comp_min_root", "A")
    data = build_comparison_data(maj, mn)
    compact = st.session_state.get("mobile_content_view_mode", "completa") == "compacta"
    st.caption(
        "Comparación entre la armonización de la escala mayor y las armonizaciones "
        "de la escala menor relativa (natural, armónica y melódica). "
        "En EmA y EmM, el guión largo (—) repite la calidad de la fila de arriba."
    )
    st.markdown(render_relative_comparison_html(data, compact=compact), unsafe_allow_html=True)


def render_main(
    modo: str,
    df: pd.DataFrame,
    raiz_sel: str,
    df_raiz: pd.DataFrame | None,
    scales_df: pd.DataFrame | None,
    harmony_df: pd.DataFrame | None,
) -> None:
    if modo == MODE_DICTIONARY and df_raiz is not None:
        render_main_dictionary(raiz_sel, df_raiz)
    elif modo == MODE_IDENTIFIER:
        render_main_identifier(df)
    elif modo == MODE_SCALES:
        render_main_scales(scales_df)
    elif modo == MODE_SCALE_HARMONIZATION:
        render_main_scale_harmonization(harmony_df, scales_df)
    elif modo == MODE_RELATIVE_COMPARISON:
        render_main_relative_comparison()
