"""Carga de datos desde Google Sheets (CSV)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chordia.chords import add_note_key_column
from chordia.config import (
    HARMONIZATION_SHEET_CANDIDATES,
    RELATIVE_COMPARISON_SHEET_CANDIDATES,
    SCALE_SHEET_CANDIDATES,
    URL_EXCEL,
    sheet_csv_url,
)

_TYPE_COL_CANDIDATES = ("Tipo", "TIPO", "Escala", "ESCALA", "Nombre", "NOMBRE")
_STRUCT_COL_CANDIDATES = (
    "Estructura",
    "ESTRUCTURA",
    "Intervalos",
    "INTERVALOS",
    "Fórmula",
    "Formula",
    "Patrón",
    "Patron",
)


@st.cache_data(ttl=600)
def load_chords(url: str = URL_EXCEL) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return add_note_key_column(df)
    except Exception:
        return None


@st.cache_data(ttl=600)
def load_scales() -> pd.DataFrame | None:
    for sheet_name in SCALE_SHEET_CANDIDATES:
        try:
            df = pd.read_csv(sheet_csv_url(sheet_name))
            df.columns = [str(c).strip() for c in df.columns]
            if not df.empty:
                return df
        except Exception:
            continue
    return None


@st.cache_data(ttl=600)
def load_relative_comparison_pairs() -> pd.DataFrame | None:
    """Hoja con columnas Mayor / Menor (orden de filas = orden en los desplegables)."""
    for sheet_name in RELATIVE_COMPARISON_SHEET_CANDIDATES:
        try:
            df = pd.read_csv(sheet_csv_url(sheet_name))
            df.columns = [str(c).strip() for c in df.columns]
            if not df.empty:
                return df
        except Exception:
            continue
    return None


@st.cache_data(ttl=600)
def load_harmonizations() -> pd.DataFrame | None:
    for sheet_name in HARMONIZATION_SHEET_CANDIDATES:
        try:
            df = pd.read_csv(sheet_csv_url(sheet_name))
            df.columns = [str(c).strip() for c in df.columns]
            has_type = any(c in df.columns for c in _TYPE_COL_CANDIDATES)
            has_structure = any(c in df.columns for c in _STRUCT_COL_CANDIDATES)
            if not df.empty and has_type and has_structure:
                return df
        except Exception:
            continue
    return None
