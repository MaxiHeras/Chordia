"""Lógica de escalas: parseo de estructura y notación enarmónica."""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

ROMAN_DEGREES = ["I", "II", "III", "IV", "V", "VI", "VII", "I"]
NATURAL_ROOTS = ["C", "D", "E", "F", "G", "A", "B"]

_LETTER_TO_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_LETTERS = ["C", "D", "E", "F", "G", "A", "B"]
_PC_TO_SIMPLE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

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


def detect_scale_columns(df_scales: pd.DataFrame) -> tuple[str | None, str | None]:
    type_col = next((c for c in TYPE_COL_CANDIDATES if c in df_scales.columns), None)
    struct_col = next((c for c in STRUCT_COL_CANDIDATES if c in df_scales.columns), None)
    return type_col, struct_col


def roots_for_alteration(alteration: str) -> list[str]:
    if alteration == "Sost.":
        return [f"{n}#" for n in NATURAL_ROOTS]
    if alteration == "Bem.":
        return [f"{n}b" for n in NATURAL_ROOTS]
    return NATURAL_ROOTS.copy()


def _note_pitch_class(note: str) -> int:
    letter = note[0]
    acc = note[1:]
    value = _LETTER_TO_PC[letter]
    value += acc.count("#")
    value -= acc.count("b")
    return value % 12


def _pitch_class_to_spelling(letter: str, target_pc: int) -> str:
    natural = _LETTER_TO_PC[letter]
    diff = (target_pc - natural) % 12
    if diff > 6:
        diff -= 12
    if diff < -2 or diff > 2:
        # Escenarios muy atípicos: recorte para evitar notaciones ilegibles.
        diff = max(-2, min(2, diff))
    if diff == 2:
        return f"{letter}##"
    if diff == 1:
        return f"{letter}#"
    if diff == -1:
        return f"{letter}b"
    if diff == -2:
        return f"{letter}bb"
    return letter


def format_note_with_enharmonic(spelled_note: str) -> str:
    pc = _note_pitch_class(spelled_note)
    simple = _PC_TO_SIMPLE[pc]
    return spelled_note if simple == spelled_note else f"{spelled_note} ({simple})"


def parse_scale_steps(raw_structure: str) -> list[int] | None:
    text = str(raw_structure).strip().upper()
    if not text:
        return None

    text = text.replace("SEMITONO", "ST").replace("SEMI TONO", "ST")
    text = text.replace("TONO", "T")
    text = text.replace("W", "T").replace("H", "S")
    text = text.replace("½", "1/2")
    text = text.replace("Y", " ")
    text = text.replace("T 1/2", "TS").replace("T + 1/2", "TS")
    text = text.replace(",", " ").replace("-", " ").replace("+", " ")
    tokens = [tok for tok in re.split(r"\s+", text) if tok]

    values: list[int] = []
    for tok in tokens:
        if tok == "T":
            values.append(2)
            continue
        if tok in {"S", "ST"}:
            values.append(1)
            continue
        if tok == "TS":
            values.append(3)
            continue
        if tok.isdigit():
            values.append(int(tok))
            continue
        # Soporte básico de formatos fraccionados.
        if tok in {"1/2", "0.5", ".5"}:
            values.append(1)
            continue
        if tok in {"1", "1.0"}:
            values.append(2)
            continue
    if len(values) < 7:
        return None
    return values[:7]


def step_to_label(step: int) -> str:
    if step == 2:
        return "T"
    if step == 1:
        return "ST"
    if step == 3:
        return "1.5T"
    return str(step)


def build_scale(root_note: str, step_pattern: list[int]) -> list[str]:
    root_letter = root_note[0]
    letter_index = _LETTERS.index(root_letter)

    pcs = [_note_pitch_class(root_note)]
    current_pc = pcs[0]
    for step in step_pattern:
        current_pc = (current_pc + step) % 12
        pcs.append(current_pc)

    notes: list[str] = []
    for degree in range(8):
        target_letter = _LETTERS[(letter_index + degree) % 7]
        spelled = _pitch_class_to_spelling(target_letter, pcs[degree])
        notes.append(format_note_with_enharmonic(spelled))
    return notes


def render_scale_grid(notes: list[str], steps: list[int]) -> None:
    # 15 columnas: nota/intervalo alternadas, y una nota final sin intervalo.
    html = ['<div class="scale-grid">']

    # Fila 1: grados romanos sobre las notas.
    for i, deg in enumerate(ROMAN_DEGREES):
        html.append(f'<div class="scale-degree c{2 * i + 1}">{deg}</div>')

    # Fila 2: notas en cuadros.
    for i, note in enumerate(notes):
        html.append(f'<div class="scale-note c{2 * i + 1}">{note}</div>')

    # Fila 3: estructura entre notas (T/ST en cuadros).
    for i, val in enumerate(steps):
        html.append(f'<div class="scale-step c{2 * i + 2}">{step_to_label(val)}</div>')

    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

