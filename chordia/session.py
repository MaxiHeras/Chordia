"""Estado de sesión Streamlit y callbacks del sidebar."""

from __future__ import annotations

import streamlit as st


def ensure_session_defaults() -> None:
    if "seleccionados" not in st.session_state:
        st.session_state.seleccionados = []
    if "notas_inversas" not in st.session_state:
        st.session_state.notas_inversas = set()
    if "pdf_data" not in st.session_state:
        st.session_state.pdf_data = None
    if "descargado" not in st.session_state:
        st.session_state.descargado = False
    if "filtro_alteracion" not in st.session_state:
        st.session_state.filtro_alteracion = "Nat."


def select_all_types(opciones: list[str]) -> None:
    st.session_state.seleccionados = opciones


def clear_selection_and_pdf() -> None:
    st.session_state.seleccionados = []
    st.session_state.pdf_data = None
    st.session_state.descargado = False


def toggle_identifier_note(nota: str) -> None:
    inv = st.session_state.notas_inversas
    if nota in inv:
        inv.remove(nota)
    else:
        inv.add(nota)
