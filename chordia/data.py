"""Carga de datos desde Google Sheets (CSV)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chordia.config import SCALE_SHEET_CANDIDATES, URL_EXCEL, sheet_csv_url


@st.cache_data(ttl=600)
def load_chords(url: str = URL_EXCEL) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df
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
