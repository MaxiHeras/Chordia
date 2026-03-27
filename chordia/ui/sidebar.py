"""Barra lateral: modo diccionario / identificador y compartir."""

from __future__ import annotations

import urllib.parse
from collections.abc import Callable

import pandas as pd
import streamlit as st

from chordia.chords import filter_roots_by_alteration, row_note_set
from chordia.config import DEFAULT_APP_PUBLIC_URL, GITHUB_RAW_BASE
from chordia.constants import (
    MODE_DICTIONARY,
    MODE_IDENTIFIER,
    MODE_SCALE_HARMONIZATION,
    MODE_SCALES,
    NOTAS_MUSICALES,
    ORDEN_TIPOS,
)
from chordia.harmonization import detect_harmonization_columns
from chordia.pdf import build_harmonization_pdf, build_scales_pdf, build_selection_pdf
from chordia.scales import detect_scale_columns, roots_for_alteration
from chordia.session import clear_selection_and_pdf, select_all_types, toggle_identifier_note


def _app_public_url() -> str:
    try:
        return str(st.secrets.get("APP_PUBLIC_URL", DEFAULT_APP_PUBLIC_URL))
    except Exception:
        return DEFAULT_APP_PUBLIC_URL


def render_dictionary_sidebar(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    st.write("Filtrar Alteración:")
    f_cols = st.columns(3)
    nat = f_cols[0].checkbox("Nat.", value=(st.session_state.filtro_alteracion == "Nat."))
    sost = f_cols[1].checkbox("Sost.", value=(st.session_state.filtro_alteracion == "Sost."))
    bem = f_cols[2].checkbox("Bem.", value=(st.session_state.filtro_alteracion == "Bem."))

    if nat and st.session_state.filtro_alteracion != "Nat.":
        st.session_state.filtro_alteracion = "Nat."
        if "u_raiz" in st.session_state:
            del st.session_state.u_raiz
        st.rerun()
    elif sost and st.session_state.filtro_alteracion != "Sost.":
        st.session_state.filtro_alteracion = "Sost."
        if "u_raiz" in st.session_state:
            del st.session_state.u_raiz
        st.rerun()
    elif bem and st.session_state.filtro_alteracion != "Bem.":
        st.session_state.filtro_alteracion = "Bem."
        if "u_raiz" in st.session_state:
            del st.session_state.u_raiz
        st.rerun()
    elif not nat and not sost and not bem:
        st.session_state.filtro_alteracion = "Nat."
        if "u_raiz" in st.session_state:
            del st.session_state.u_raiz
        st.rerun()

    notas_filtradas = filter_roots_by_alteration(NOTAS_MUSICALES, st.session_state.filtro_alteracion)
    raiz_opciones = [n for n in notas_filtradas if n in df["Raiz"].unique()]
    raiz_sel = st.selectbox("Nota Raíz:", raiz_opciones)

    df_raiz = df[df["Raiz"] == raiz_sel]
    opciones = [t for t in ORDEN_TIPOS if t in df_raiz["Naturaleza"].unique()]

    if "u_raiz" not in st.session_state or st.session_state.u_raiz != raiz_sel:
        st.session_state.u_raiz = raiz_sel
        st.session_state.seleccionados = opciones
        st.session_state.pdf_data = None
        st.session_state.descargado = False

    st.multiselect("Tipo:", opciones, key="seleccionados")
    c1, c2 = st.columns(2)
    c1.button("Todo", on_click=select_all_types, args=(opciones,), use_container_width=True)
    c2.button("Limpiar", on_click=clear_selection_and_pdf, use_container_width=True)
    return raiz_sel, df_raiz


def render_identifier_sidebar() -> None:
    st.write("### Identificador")
    for i in range(0, len(NOTAS_MUSICALES), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(NOTAS_MUSICALES):
                n = NOTAS_MUSICALES[idx]
                active = n in st.session_state.notas_inversas
                with cols[j]:
                    if st.button(n, key=f"id_{n}", type="primary" if active else "secondary"):
                        toggle_identifier_note(n)
                        st.rerun()
    if st.button("🗑️ Borrar Notas", use_container_width=True):
        st.session_state.notas_inversas = set()
        st.rerun()


def render_scales_sidebar(scales_df: pd.DataFrame | None, reset_selection: bool = False) -> None:
    st.write("Filtrar Alteración:")
    f_cols = st.columns(3)
    nat = f_cols[0].checkbox(
        "Nat.",
        value=(st.session_state.filtro_alteracion_escalas == "Nat."),
        key="scales_nat",
    )
    sost = f_cols[1].checkbox(
        "Sost.",
        value=(st.session_state.filtro_alteracion_escalas == "Sost."),
        key="scales_sost",
    )
    bem = f_cols[2].checkbox(
        "Bem.",
        value=(st.session_state.filtro_alteracion_escalas == "Bem."),
        key="scales_bem",
    )

    if nat and st.session_state.filtro_alteracion_escalas != "Nat.":
        st.session_state.filtro_alteracion_escalas = "Nat."
        st.rerun()
    elif sost and st.session_state.filtro_alteracion_escalas != "Sost.":
        st.session_state.filtro_alteracion_escalas = "Sost."
        st.rerun()
    elif bem and st.session_state.filtro_alteracion_escalas != "Bem.":
        st.session_state.filtro_alteracion_escalas = "Bem."
        st.rerun()
    elif not nat and not sost and not bem:
        st.session_state.filtro_alteracion_escalas = "Nat."
        st.rerun()

    root_options = roots_for_alteration(st.session_state.filtro_alteracion_escalas)
    default_index = root_options.index(st.session_state.scale_root) if st.session_state.scale_root in root_options else 0
    prev_root = st.session_state.get("scale_root", "C")
    st.session_state.scale_root = st.selectbox("Nota Raíz:", root_options, index=default_index, key="scales_root_select")
    root_changed = st.session_state.scale_root != prev_root

    if scales_df is None:
        st.warning("No se encontró la hoja de escalas en Google Sheets.")
        st.session_state.scales_selected_types = []
        return

    type_col, _ = detect_scale_columns(scales_df)
    if not type_col:
        st.warning("No se encontró la columna de tipo de escala en la hoja.")
        st.session_state.scales_selected_types = []
        return

    scale_types = [str(x).strip() for x in scales_df[type_col].dropna().tolist() if str(x).strip()]
    scale_types = list(dict.fromkeys(scale_types))

    # Igual que en Diccionario: al entrar al modo o al cambiar raíz, seleccionar todo.
    if reset_selection or root_changed or not st.session_state.scales_selected_types:
        st.session_state.scales_selected_types = scale_types.copy()

    st.multiselect("Tipo:", scale_types, key="scales_selected_types")
    c1, c2 = st.columns(2)
    c1.button(
        "Todo",
        on_click=lambda: st.session_state.update({"scales_selected_types": scale_types}),
        use_container_width=True,
        key="scales_select_all",
    )
    c2.button(
        "Limpiar",
        on_click=lambda: st.session_state.update({"scales_selected_types": []}),
        use_container_width=True,
        key="scales_clear_all",
    )


def render_harmonization_sidebar(harmony_df: pd.DataFrame | None, reset_selection: bool = False) -> None:
    st.write("Filtrar Alteración:")
    f_cols = st.columns(3)
    nat = f_cols[0].checkbox("Nat.", value=(st.session_state.filtro_alteracion_arm == "Nat."), key="arm_nat")
    sost = f_cols[1].checkbox("Sost.", value=(st.session_state.filtro_alteracion_arm == "Sost."), key="arm_sost")
    bem = f_cols[2].checkbox("Bem.", value=(st.session_state.filtro_alteracion_arm == "Bem."), key="arm_bem")

    if nat and st.session_state.filtro_alteracion_arm != "Nat.":
        st.session_state.filtro_alteracion_arm = "Nat."
        st.rerun()
    elif sost and st.session_state.filtro_alteracion_arm != "Sost.":
        st.session_state.filtro_alteracion_arm = "Sost."
        st.rerun()
    elif bem and st.session_state.filtro_alteracion_arm != "Bem.":
        st.session_state.filtro_alteracion_arm = "Bem."
        st.rerun()
    elif not nat and not sost and not bem:
        st.session_state.filtro_alteracion_arm = "Nat."
        st.rerun()

    root_options = roots_for_alteration(st.session_state.filtro_alteracion_arm)
    default_index = root_options.index(st.session_state.arm_root) if st.session_state.arm_root in root_options else 0
    prev_root = st.session_state.get("arm_root", "C")
    st.session_state.arm_root = st.selectbox("Nota Raíz:", root_options, index=default_index, key="arm_root_select")
    root_changed = st.session_state.arm_root != prev_root

    if harmony_df is None:
        st.warning("No se encontró la hoja de armonización de escalas en Google Sheets.")
        st.session_state.arm_selected_types = []
        return

    type_col, _, _, _ = detect_harmonization_columns(harmony_df)
    if not type_col:
        st.warning("No se encontró la columna de tipo en la hoja.")
        st.session_state.arm_selected_types = []
        return

    options = [str(x).strip() for x in harmony_df[type_col].dropna().tolist() if str(x).strip()]
    options = list(dict.fromkeys(options))
    if reset_selection or root_changed or not st.session_state.arm_selected_types:
        st.session_state.arm_selected_types = options.copy()

    st.multiselect("Tipo:", options, key="arm_selected_types")
    c1, c2 = st.columns(2)
    c1.button("Todo", on_click=lambda: st.session_state.update({"arm_selected_types": options}), use_container_width=True, key="arm_select_all")
    c2.button("Limpiar", on_click=lambda: st.session_state.update({"arm_selected_types": []}), use_container_width=True, key="arm_clear_all")


def render_share_section() -> None:
    url = _app_public_url()
    st.write("---")
    st.write("📲 **Compartir App**")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(url)}"
    st.image(qr_url, caption="Escaneá para abrir", width=180)
    st.text_input("Enlace de la app:", value=url, disabled=True, help="Haz clic y arrastra para copiar")
    st.caption("by Maxi Heras - Tucumán")


def _render_pdf_controls(pdf_builder: Callable[[], bytes | None], filename: str) -> None:
    st.radio(
        "Modo de impresión PDF:",
        options=["one_per_page", "continuous"],
        format_func=lambda x: "Una hoja por tipo (por defecto)" if x == "one_per_page" else "Continuo (varios tipos por hoja)",
        key="pdf_print_mode",
        horizontal=False,
    )
    st.write("")
    placeholder = st.empty()
    if st.session_state.descargado:
        placeholder.success("✅ ¡Listo, guardado!")
    elif st.session_state.pdf_data:
        placeholder.info("✅ ¡Listo para guardar!")

    if st.button("📥 Generar PDF de Selección", use_container_width=True, key="sidebar_generate_pdf"):
        placeholder.markdown("⏳ *Preparando PDF...*")
        pdf_bytes = pdf_builder()
        if pdf_bytes:
            st.session_state.pdf_data = pdf_bytes
            st.session_state.pdf_filename = filename
            st.session_state.descargado = False
            st.rerun()
        placeholder.warning("No hay contenido disponible para generar PDF.")

    if st.session_state.pdf_data:
        st.download_button(
            "💾 GUARDAR ARCHIVO",
            bytes(st.session_state.pdf_data),
            st.session_state.get("pdf_filename", filename),
            "application/pdf",
            use_container_width=True,
            type="primary",
            on_click=lambda: st.session_state.update({"descargado": True}),
            key="sidebar_download_pdf",
        )


def _render_mobile_view_mode_switch() -> None:
    st.radio(
        "Vista móvil:",
        options=["completa", "compacta"],
        format_func=lambda x: "Completa" if x == "completa" else "Compacta",
        key="mobile_content_view_mode",
        horizontal=True,
    )


def render_sidebar(
    df: pd.DataFrame,
    scales_df: pd.DataFrame | None,
    harmony_df: pd.DataFrame | None,
) -> tuple[str, str, pd.DataFrame | None]:
    """
    Devuelve (modo, raiz_sel, df_raiz).
    En modos no-diccionario, raiz_sel es '' y df_raiz es None.
    """
    st.subheader("Seleccionar Modo")
    modo_previo = st.session_state.get("modo_actual", MODE_DICTIONARY)
    modo = st.radio(
        " ",
        [MODE_IDENTIFIER, MODE_DICTIONARY, MODE_SCALES, MODE_SCALE_HARMONIZATION],
        label_visibility="collapsed",
    )
    st.session_state.modo_actual = modo

    mode_changed = modo != modo_previo
    if mode_changed:
        if "u_raiz" in st.session_state:
            del st.session_state.u_raiz
        st.session_state.pdf_data = None
        st.session_state.descargado = False

    st.write("---")

    raiz_sel = ""
    df_raiz: pd.DataFrame | None = None

    if modo == MODE_DICTIONARY:
        raiz_sel, df_raiz = render_dictionary_sidebar(df)
        def _build_dict_pdf() -> bytes | None:
            if df_raiz is None:
                return None
            df_para_pdf = df_raiz[df_raiz["Naturaleza"].isin(st.session_state.seleccionados)]
            if df_para_pdf.empty:
                return None
            return build_selection_pdf(
                df_para_pdf,
                GITHUB_RAW_BASE,
                _app_public_url(),
                print_mode=st.session_state.get("pdf_print_mode", "one_per_page"),
            )

        _render_pdf_controls(_build_dict_pdf, f"Acordes_{raiz_sel}.pdf")
        render_share_section()
        return modo, raiz_sel, df_raiz

    if modo == MODE_SCALES:
        render_scales_sidebar(scales_df, reset_selection=mode_changed)
        def _build_scales_pdf() -> bytes | None:
            if scales_df is None:
                return None
            type_col, struct_col = detect_scale_columns(scales_df)
            if not type_col or not struct_col:
                return None
            selected_types = st.session_state.get("scales_selected_types", [])
            root = st.session_state.get("scale_root", "C")
            if not selected_types:
                return None
            return build_scales_pdf(
                scales_df=scales_df,
                selected_types=selected_types,
                root_note=root,
                app_public_url=_app_public_url(),
                type_col=type_col,
                struct_col=struct_col,
                print_mode=st.session_state.get("pdf_print_mode", "one_per_page"),
            )

        _render_pdf_controls(_build_scales_pdf, f"Escalas_{st.session_state.get('scale_root', 'C')}.pdf")
        render_share_section()
        _render_mobile_view_mode_switch()
        return modo, "", None

    if modo == MODE_SCALE_HARMONIZATION:
        render_harmonization_sidebar(harmony_df, reset_selection=mode_changed)
        def _build_harmony_pdf() -> bytes | None:
            if harmony_df is None:
                return None
            selected_types = st.session_state.get("arm_selected_types", [])
            if not selected_types:
                return None
            return build_harmonization_pdf(
                harmony_df=harmony_df,
                scales_df=scales_df,
                selected_types=selected_types,
                root_note=st.session_state.get("arm_root", "C"),
                app_public_url=_app_public_url(),
                print_mode=st.session_state.get("pdf_print_mode", "one_per_page"),
            )

        _render_pdf_controls(_build_harmony_pdf, f"Armonizacion_{st.session_state.get('arm_root', 'C')}.pdf")
        render_share_section()
        _render_mobile_view_mode_switch()
        return modo, "", None

    render_identifier_sidebar()
    def _build_identifier_pdf() -> bytes | None:
        notas_act = {n.strip() for n in st.session_state.notas_inversas}
        if not notas_act:
            return None
        res = df[df.apply(lambda r: row_note_set(r) == notas_act, axis=1)]
        if res.empty:
            return None
        return build_selection_pdf(
            res.head(1),
            GITHUB_RAW_BASE,
            _app_public_url(),
            print_mode=st.session_state.get("pdf_print_mode", "one_per_page"),
        )

    _render_pdf_controls(_build_identifier_pdf, "Identificador_de_acorde.pdf")
    render_share_section()
    return modo, "", None
