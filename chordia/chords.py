"""Utilidades sobre filas de acordes y conjuntos de notas."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from chordia.constants import NOTE_COLS


def row_note_list(row: pd.Series) -> list[str]:
    return [str(row.get(n, "")).strip() for n in NOTE_COLS if pd.notna(row.get(n))]


def row_note_set(row: pd.Series) -> set[str]:
    return {str(row[n]).strip() for n in NOTE_COLS if pd.notna(row.get(n))}


def filter_roots_by_alteration(notes: Iterable[str], filtro: str) -> list[str]:
    notes = list(notes)
    if filtro == "Nat.":
        return [n for n in notes if len(n) == 1]
    if filtro == "Sost.":
        return [n for n in notes if "#" in n]
    return [n for n in notes if "b" in n]
