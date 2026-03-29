"""Presentación de un acorde en la UI principal."""

from __future__ import annotations

import urllib.parse

import pandas as pd
import streamlit as st

from chordia.chords import row_note_list
from chordia.constants import DIAGRAM_COUNT


def render_chord_detail(row: pd.Series, github_raw_base: str) -> None:
    st.markdown(f"### {row['Raiz']} {row['Naturaleza']}")
    lista_n = row_note_list(row)
    st.write(f"**Notas:** {' - '.join(lista_n)}")
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"**Int_IVAN:** {row.get('Int_IVAN', 'N/A')}")
    with c2:
        st.info(f"**Int_TRAD:** {row.get('Int_TRAD', 'N/A')}")
    st.write("---")
    st.write("**Diagramas:**")
    h_items = ""
    for j in range(1, DIAGRAM_COUNT + 1):
        v = str(row.get(f"Diagrama{j}", "nan")).strip()
        if v.lower().endswith(".png"):
            nat_cod = urllib.parse.quote(str(row["Naturaleza"]))
            img_name = v.split("/")[-1].replace("#", "SOS")
            url = f"{github_raw_base}/{nat_cod}/{img_name}"
            h_items += (
                f'<div class="chord-diag-item">'
                f'<div class="chord-diag-frame"><img src="{url}" class="chord-img-web" alt=""></div>'
                f'<p class="chord-diag-caption">P{j}</p></div>'
            )
    if h_items:
        st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
