"""Carga de datos desde Google Sheets (CSV)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chordia.config import URL_EXCEL


@st.cache_data(ttl=600)
def load_chords(url: str = URL_EXCEL) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        return None
