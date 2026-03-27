"""Exportación a PDF con fpdf2."""

from __future__ import annotations

import urllib.parse
from io import BytesIO

import pandas as pd
import requests
from fpdf import FPDF

from chordia.chords import row_note_list
from chordia.constants import DIAGRAM_COUNT
from chordia.scales import build_scale, parse_scale_steps


class ChordiaPDF(FPDF):
    def __init__(self, app_public_url: str, **kwargs):
        super().__init__(**kwargs)
        self._app_public_url = app_public_url

    def footer(self) -> None:
        self.set_y(-30)
        qr_url = (
            "https://api.qrserver.com/v1/create-qr-code/?size=100x100&data="
            f"{urllib.parse.quote(self._app_public_url)}"
        )
        try:
            self.image(qr_url, x=175, y=self.get_y(), w=20, h=20)
        except Exception:
            pass
        self.set_y(self.get_y() + 22)
        self.set_font("helvetica", "", 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, "by Maxi Heras - Tucumán", align="R", ln=True)


def build_selection_pdf(
    dataframe_seleccionado: pd.DataFrame,
    github_raw_base: str,
    app_public_url: str,
) -> bytes:
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)

    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        pdf.set_font("helvetica", "B", 24)
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align="C")
        pdf.ln(8)
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Notas: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{' - '.join(row_note_list(row))}\n")
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Int_IVAN: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Int_TRAD: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{str(row.get('Int_TRAD', 'N/A'))}\n")
        pdf.ln(14)

        x_start, gap_x, gap_y, cols, diag_w, diag_h = 15, 8, 12, 4, 38, 45
        y_grid_top = pdf.get_y()
        count = 0
        for i in range(1, DIAGRAM_COUNT + 1):
            val = str(row.get(f"Diagrama{i}", "nan")).strip()
            if val.lower().endswith(".png"):
                nat_pdf = urllib.parse.quote(str(row["Naturaleza"]))
                img_name_pdf = val.split("/")[-1].replace("#", "SOS")
                url_img = f"{github_raw_base}/{nat_pdf}/{img_name_pdf}"
                try:
                    resp = requests.get(url_img, timeout=5)
                    if resp.status_code == 200:
                        img_data = resp.content
                        col = count % cols
                        fila = count // cols
                        pos_x = x_start + (col * (diag_w + gap_x))
                        pos_y = y_grid_top + (fila * (diag_h + gap_y))
                        pdf.image(BytesIO(img_data), x=pos_x, y=pos_y, w=diag_w, h=diag_h)
                        count += 1
                except Exception:
                    continue

    return pdf.output()


def build_scales_pdf(
    scales_df: pd.DataFrame,
    selected_types: list[str],
    root_note: str,
    app_public_url: str,
    type_col: str,
    struct_col: str,
) -> bytes:
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)

    for scale_type in selected_types:
        matches = scales_df[scales_df[type_col].astype(str).str.strip() == str(scale_type).strip()]
        if matches.empty:
            continue
        row = matches.iloc[0]
        raw_structure = str(row.get(struct_col, "")).strip()
        steps = parse_scale_steps(raw_structure)
        if not steps:
            continue
        notes = build_scale(root_note, steps)

        pdf.add_page()
        pdf.set_font("helvetica", "B", 22)
        pdf.cell(0, 16, f"{root_note} {scale_type}", border=1, ln=True, align="C")
        pdf.ln(8)
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Grados: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, "I - II - III - IV - V - VI - VII - I\n")
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Notas: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{' - '.join(notes)}\n")
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Estructura: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{raw_structure}\n")
        pdf.set_font("helvetica", "B", 11)
        pdf.write(6, "Pasos (semitonos): ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{' - '.join(str(x) for x in steps)}\n")

    return pdf.output()


def build_info_pdf(title: str, body_lines: list[str], app_public_url: str) -> bytes:
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 22)
    pdf.cell(0, 16, title, border=1, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("helvetica", "", 12)
    for line in body_lines:
        pdf.multi_cell(0, 7, line)
    return pdf.output()
