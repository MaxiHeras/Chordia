"""Utilidades sobre filas de acordes y conjuntos de notas."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from chordia.constants import NOTE_COLS

NOTE_KEY_COL = "_chordia_note_key"


def row_note_list(row: pd.Series) -> list[str]:
    return [str(row.get(n, "")).strip() for n in NOTE_COLS if pd.notna(row.get(n))]


def row_note_set(row: pd.Series) -> set[str]:
    return {str(row[n]).strip() for n in NOTE_COLS if pd.notna(row.get(n))}


def add_note_key_column(df: pd.DataFrame) -> pd.DataFrame:
    """Precomputa claves de N1..N4 para búsqueda rápida en el identificador (una sola pasada al cargar)."""
    out = df.copy()
    out[NOTE_KEY_COL] = out[list(NOTE_COLS)].apply(
        lambda r: frozenset(str(r[n]).strip() for n in NOTE_COLS if pd.notna(r.get(n))),
        axis=1,
    )
    return out


def match_rows_by_note_set(df: pd.DataFrame, notas: set[str]) -> pd.DataFrame:
    target = frozenset(notas)
    if NOTE_KEY_COL in df.columns:
        return df[df[NOTE_KEY_COL] == target]
    return df[df.apply(lambda r: row_note_set(r) == notas, axis=1)]


def filter_roots_by_alteration(notes: Iterable[str], filtro: str) -> list[str]:
    notes = list(notes)
    if filtro == "Nat.":
        return [n for n in notes if len(n) == 1]
    if filtro == "Sost.":
        return [n for n in notes if "#" in n]
    return [n for n in notes if "b" in n]
