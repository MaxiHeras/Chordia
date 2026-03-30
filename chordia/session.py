"""Estado de sesión Streamlit y callbacks del sidebar."""

from __future__ import annotations

import streamlit as st

from chordia.constants import MODE_DICTIONARY, MODE_TO_URL_SLUG, URL_SLUG_TO_MODE


def ensure_session_defaults() -> None:
    if "modo_actual" not in st.session_state:
        st.session_state.modo_actual = MODE_DICTIONARY
    if "seleccionados" not in st.session_state:
        st.session_state.seleccionados = []
    if "notas_inversas" not in st.session_state:
        st.session_state.notas_inversas = set()
    if "pdf_data" not in st.session_state:
        st.session_state.pdf_data = None
    if "pdf_filename" not in st.session_state:
        st.session_state.pdf_filename = "Chordia.pdf"
    if "pdf_print_mode" not in st.session_state:
        st.session_state.pdf_print_mode = "one_per_page"
    if "descargado" not in st.session_state:
        st.session_state.descargado = False
    if "filtro_alteracion" not in st.session_state:
        st.session_state.filtro_alteracion = "Nat."
    if "filtro_alteracion_escalas" not in st.session_state:
        st.session_state.filtro_alteracion_escalas = "Nat."
    if "scale_root" not in st.session_state:
        st.session_state.scale_root = "C"
    if "scales_selected_types" not in st.session_state:
        st.session_state.scales_selected_types = []
    if "filtro_alteracion_arm" not in st.session_state:
        st.session_state.filtro_alteracion_arm = "Nat."
    if "arm_root" not in st.session_state:
        st.session_state.arm_root = "C"
    if "arm_selected_types" not in st.session_state:
        st.session_state.arm_selected_types = []
    if "filtro_alteracion_rel" not in st.session_state:
        st.session_state.filtro_alteracion_rel = "Nat."
    if "rel_comp_maj_root" not in st.session_state:
        st.session_state.rel_comp_maj_root = "C"
    if "rel_comp_min_root" not in st.session_state:
        st.session_state.rel_comp_min_root = "A"
    if "rel_comp_sidebar_mode" not in st.session_state:
        st.session_state.rel_comp_sidebar_mode = "Mayor"
    if "rel_pdf_print_mode" not in st.session_state:
        st.session_state.rel_pdf_print_mode = "current_view"
    if "mobile_content_view_mode" not in st.session_state:
        st.session_state.mobile_content_view_mode = "compacta"


def _query_param_modo_slug() -> str | None:
    raw = st.query_params.get("modo")
    if raw is None:
        return None
    if isinstance(raw, list):
        return str(raw[0]).strip().lower() if raw else None
    return str(raw).strip().lower()


def apply_mode_from_url() -> None:
    """Solo en la primera ejecución de la sesión: hidratar modo desde ?modo=...

    Si se aplicara en cada rerun, la URL vieja pisaría el modo que acaba de elegir
    el usuario en el radio (rebote al modo anterior).
    """
    if st.session_state.get("_chordia_mode_from_url_done"):
        return
    st.session_state._chordia_mode_from_url_done = True
    slug = _query_param_modo_slug()
    if not slug:
        return
    mode = URL_SLUG_TO_MODE.get(slug)
    if mode:
        st.session_state.modo_actual = mode


def sync_mode_to_url() -> None:
    """Mantiene la URL alineada con el modo actual para que el refresh conserve la pantalla."""
    modo = st.session_state.get("modo_actual")
    slug = MODE_TO_URL_SLUG.get(modo) if modo else None
    if not slug:
        return
    current = _query_param_modo_slug()
    if current != slug:
        st.query_params["modo"] = slug


def select_all_types(opciones: list[str]) -> None:
    st.session_state.seleccionados = list(opciones)


def clear_selection_and_pdf() -> None:
    st.session_state.seleccionados = []
    st.session_state.pdf_data = None
    st.session_state.pdf_filename = "Chordia.pdf"
    st.session_state.descargado = False


def select_all_scales_types(opciones: list[str]) -> None:
    """Callback con nombre (evita lambdas en on_click que fallan al cambiar de modo en Streamlit)."""
    st.session_state.scales_selected_types = list(opciones)


def clear_scales_selection_and_pdf() -> None:
    st.session_state.scales_selected_types = []
    st.session_state.pdf_data = None
    st.session_state.pdf_filename = "Chordia.pdf"
    st.session_state.descargado = False


def select_all_arm_types(opciones: list[str]) -> None:
    st.session_state.arm_selected_types = list(opciones)


def clear_arm_selection_and_pdf() -> None:
    st.session_state.arm_selected_types = []
    st.session_state.pdf_data = None
    st.session_state.pdf_filename = "Chordia.pdf"
    st.session_state.descargado = False


def toggle_identifier_note(nota: str) -> None:
    inv = st.session_state.notas_inversas
    if nota in inv:
        inv.remove(nota)
    else:
        inv.add(nota)
