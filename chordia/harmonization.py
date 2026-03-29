"""Lógica y render de Armonización de escalas."""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from chordia.scales import ROMAN_DEGREES, build_scale, parse_scale_steps, render_scale_grid

TYPE_COL_CANDIDATES = ("Tipo", "TIPO", "Escala", "ESCALA", "Nombre", "NOMBRE")
STRUCT_COL_CANDIDATES = (
    "Estructura",
    "ESTRUCTURA",
    "Intervalos",
    "INTERVALOS",
    "Fórmula",
    "Formula",
    "Patrón",
    "Patron",
)
HARMONY_COL_CANDIDATES = (
    "Armonización",
    "Armonizacion",
    "Acordes",
    "ACORDES",
    "Estructura de armonización",
    "Estructura de armonizacion",
)
DEGREE_COL_MAP = {
    "I": ("I", "Grado I", "GRADO I"),
    "II": ("II", "Grado II", "GRADO II"),
    "III": ("III", "Grado III", "GRADO III"),
    "IV": ("IV", "Grado IV", "GRADO IV"),
    "V": ("V", "Grado V", "GRADO V"),
    "VI": ("VI", "Grado VI", "GRADO VI"),
    "VII": ("VII", "Grado VII", "GRADO VII"),
}


def detect_harmonization_columns(
    df_harmony: pd.DataFrame,
) -> tuple[str | None, str | None, list[str] | None, str | None]:
    type_col = next((c for c in TYPE_COL_CANDIDATES if c in df_harmony.columns), None)
    struct_col = next((c for c in STRUCT_COL_CANDIDATES if c in df_harmony.columns), None)

    degree_cols: list[str] = []
    for degree in ("I", "II", "III", "IV", "V", "VI", "VII"):
        found = next((c for c in DEGREE_COL_MAP[degree] if c in df_harmony.columns), None)
        if not found:
            degree_cols = []
            break
        degree_cols.append(found)

    harmony_col = next((c for c in HARMONY_COL_CANDIDATES if c in df_harmony.columns), None)
    return type_col, struct_col, (degree_cols if degree_cols else None), harmony_col


def _extract_tokens_from_string(raw_value: str) -> list[str]:
    text = str(raw_value).strip()
    if not text:
        return []
    normalized = text.replace("|", "-").replace("/", "-").replace(",", "-")
    normalized = normalized.replace("—", "-").replace("–", "-")
    tokens = [t.strip() for t in normalized.split("-") if t.strip()]
    return tokens


def parse_harmony_structure(raw_value: str) -> list[str]:
    return _extract_tokens_from_string(raw_value)


def extract_harmony_tokens(row: pd.Series, degree_cols: list[str] | None, harmony_col: str | None) -> list[str]:
    if degree_cols:
        tokens = [str(row.get(col, "")).strip() for col in degree_cols]
        tokens = [t for t in tokens if t]
        if len(tokens) == 7:
            return tokens

    if harmony_col:
        tokens = _extract_tokens_from_string(str(row.get(harmony_col, "")))
        if len(tokens) >= 7:
            return tokens[:7]
    return []


def _join_note_and_quality(note: str, quality_token: str) -> str:
    q = quality_token.strip()
    if not q:
        return note
    if re.search(r"[A-G]", q):
        return q
    if q in {"M", "Maj", "MAJ"} or q.lower() in {"major", "mayor"}:
        # Mayor: se muestra solo la nota.
        return note
    return f"{note}{q}"


def build_harmonized_chords(root_note: str, steps: list[int], harmony_tokens: list[str]) -> tuple[list[str], list[str]]:
    notes = build_scale(root_note, steps)
    degree_notes = notes[:7]
    chords = [_join_note_and_quality(degree_notes[i], harmony_tokens[i]) for i in range(7)]
    return notes, chords


def _chord_label_compact(chord: str) -> str:
    """Quita el paréntesis enarmónico en compacta para que quepa en columnas estrechas."""
    return re.sub(r"\s*\([^)]*\)", "", chord).strip()


def render_harmonization_result(
    root_note: str,
    scale_type: str,
    raw_structure: str,
    notes: list[str],
    chords: list[str],
    steps: list[int],
    compact: bool = False,
) -> None:
    st.subheader(f"{root_note} {scale_type}")
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
    if compact:
        st.markdown(
            '<p class="harmony-block-title harmony-block-title--compact">'
            "<strong>Acordes de la escala armonizada</strong></p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**Acordes de la escala armonizada**")

    wrap_class = "harmony-wrap compact-mode" if compact else "harmony-wrap"
    items = [f'<div class="{wrap_class}"><div class="harmony-degrees-row">']
    for i, deg in enumerate(ROMAN_DEGREES[:-1]):
        items.append(f'<div class="harmony-degree">{deg}</div>')
    items.append("</div>")
    items.append('<div class="harmony-chords-row">')
    for i, _ in enumerate(ROMAN_DEGREES[:-1]):
        label = _chord_label_compact(chords[i]) if compact else chords[i]
        items.append(f'<div class="harmony-chord">{label}</div>')
    items.append("</div></div>")
    st.markdown("".join(items), unsafe_allow_html=True)

