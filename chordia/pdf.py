"""Exportación a PDF con fpdf2."""

from __future__ import annotations

import urllib.parse
from io import BytesIO

import pandas as pd
import requests
from fpdf import FPDF

from chordia.chords import row_note_list
from chordia.constants import DIAGRAM_COUNT
from chordia.harmonization import (
    build_harmonized_chords,
    detect_harmonization_columns,
    parse_harmony_structure,
)
from chordia.relative_comparison import ROMAN_HEADER, build_comparison_data
from chordia.scales import ROMAN_DEGREES, build_scale, detect_scale_columns, parse_scale_steps, step_to_label


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


def _ensure_space(pdf: ChordiaPDF, needed_height: float, print_mode: str) -> None:
    if pdf.page_no() == 0:
        pdf.add_page()
        if print_mode == "one_per_page":
            return
    if print_mode == "one_per_page":
        pdf.add_page()
        return
    available = pdf.h - pdf.b_margin - pdf.get_y()
    if needed_height > available:
        pdf.add_page()


def _draw_chord_section(
    pdf: ChordiaPDF,
    row: pd.Series,
    github_raw_base: str,
    print_mode: str,
) -> None:
    diag_values: list[str] = []
    for i in range(1, DIAGRAM_COUNT + 1):
        val = str(row.get(f"Diagrama{i}", "nan")).strip()
        if val.lower().endswith(".png"):
            diag_values.append(val)

    # Altura aproximada para decidir salto de página en modo continuo.
    diag_rows = max(1, (len(diag_values) + 3) // 4) if diag_values else 1
    needed_height = 70 + (diag_rows * 57)
    _ensure_space(pdf, needed_height, print_mode)

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
    for val in diag_values:
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

    # Separación visual entre secciones en modo continuo.
    if print_mode == "continuous":
        pdf.set_y(max(pdf.get_y(), y_grid_top + (diag_rows * (diag_h + gap_y))))
        pdf.ln(8)


def build_selection_pdf(
    dataframe_seleccionado: pd.DataFrame,
    github_raw_base: str,
    app_public_url: str,
    print_mode: str = "one_per_page",
) -> bytes:
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)

    for _, row in dataframe_seleccionado.iterrows():
        _draw_chord_section(pdf, row, github_raw_base, print_mode)

    return pdf.output()


def build_scales_pdf(
    scales_df: pd.DataFrame,
    selected_types: list[str],
    root_note: str,
    app_public_url: str,
    type_col: str,
    struct_col: str,
    print_mode: str = "one_per_page",
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

        # Reserva para sección completa; si no entra en continuo, salta página.
        _ensure_space(pdf, 86, print_mode)
        pdf.set_font("helvetica", "B", 22)
        pdf.cell(0, 16, f"{root_note} {scale_type}", border=1, ln=True, align="C")
        pdf.ln(10)

        # Ajuste dinámico para que siempre entren 8 notas + 7 intervalos.
        total_width = pdf.w - pdf.l_margin - pdf.r_margin
        left = pdf.l_margin
        note_w = 21.0
        gap_w = (total_width - (note_w * 8)) / 7.0
        if gap_w < 7.0:
            note_w = 19.0
            gap_w = (total_width - (note_w * 8)) / 7.0
        if gap_w < 6.0:
            note_w = 17.5
            gap_w = (total_width - (note_w * 8)) / 7.0

        y_deg = pdf.get_y()
        y_note = y_deg + 7
        y_step = y_note + 11

        # Grados romanos arriba de cada nota.
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(80, 80, 80)
        for i, deg in enumerate(ROMAN_DEGREES):
            x_note = left + i * (note_w + gap_w)
            pdf.set_xy(x_note, y_deg)
            pdf.cell(note_w, 5, deg, align="C")

        # Notas en cajas.
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(20, 20, 20)
        for i, note in enumerate(notes):
            x_note = left + i * (note_w + gap_w)
            pdf.rect(x_note, y_note, note_w, 8.5)
            pdf.set_xy(x_note + 0.4, y_note + 1.5)
            pdf.cell(note_w - 0.8, 4, note, align="C")

        # T / ST en cajas entre notas.
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(90, 90, 90)
        for i, step in enumerate(steps):
            x_step = left + i * (note_w + gap_w) + note_w
            pdf.rect(x_step, y_step, gap_w, 6.0)
            pdf.set_xy(x_step, y_step + 1.3)
            pdf.cell(gap_w, 3.5, step_to_label(step), align="C")

        pdf.set_y(y_step + 18)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(0, 6, f"Estructura: {raw_structure}")
        if print_mode == "continuous":
            pdf.ln(8)

    return pdf.output()


def build_relative_comparison_pdf(major_root: str, minor_root: str, app_public_url: str) -> bytes:
    """Una página con tablas mayor / menor relativas (como la vista principal)."""
    data = build_comparison_data(major_root, minor_root)
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Relativas y comparación", border=0, ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, f"Mayor: {data.major_root} — Menor relativa: {data.minor_root}", ln=True, align="C")
    pdf.ln(4)

    total_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_label = 20.0
    cell_w = (total_w - col_label) / 7.0
    h_row = 6.0
    left = pdf.l_margin

    def row_line(label: str, cells: list[str]) -> None:
        pdf.set_x(left)
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(col_label, h_row, label, border=1)
        pdf.set_font("helvetica", "", 8)
        for c in cells:
            pdf.cell(cell_w, h_row, c.replace("—", "-"), border=1, align="C")
        pdf.ln(h_row)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, "Tonalidad mayor", ln=True)
    pdf.set_font("helvetica", "", 8)
    row_line("Raíz", data.major_degrees_notes)
    row_line("", [""] * 7)
    row_line("Grados", list(ROMAN_HEADER))
    row_line("EM", data.major_harm_row)
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, "Tonalidad menor (relativa)", ln=True)
    pdf.set_font("helvetica", "", 8)
    row_line("Raíz", data.minor_degrees_notes)
    row_line("", [""] * 7)
    row_line("Grados", list(ROMAN_HEADER))
    row_line("EmN", data.minor_emn)
    row_line("EmA", data.minor_ema_display)
    row_line("EmM", data.minor_emm_display)

    pdf.set_font("helvetica", "I", 7)
    pdf.set_text_color(90, 90, 90)
    pdf.ln(3)
    pdf.multi_cell(0, 4, "EmA/EmM: el guión indica la misma calidad que en la fila de referencia inmediata (tabla compacta).")
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


def build_harmonization_pdf(
    harmony_df: pd.DataFrame,
    scales_df: pd.DataFrame,
    selected_types: list[str],
    root_note: str,
    app_public_url: str,
    print_mode: str = "one_per_page",
) -> bytes:
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)

    type_col, struct_col, _, _ = detect_harmonization_columns(harmony_df)
    if not type_col or not struct_col:
        return pdf.output()
    scale_type_col, scale_struct_col = detect_scale_columns(scales_df)
    if not scale_type_col or not scale_struct_col:
        return pdf.output()

    for scale_type in selected_types:
        matches = harmony_df[harmony_df[type_col].astype(str).str.strip() == str(scale_type).strip()]
        if matches.empty:
            continue
        row = matches.iloc[0]
        harmony_structure = str(row.get(struct_col, "")).strip()
        harmony_tokens = parse_harmony_structure(harmony_structure)
        if len(harmony_tokens) != 7:
            continue

        scale_match = scales_df[scales_df[scale_type_col].astype(str).str.strip() == str(scale_type).strip()]
        if scale_match.empty:
            continue
        raw_structure = str(scale_match.iloc[0].get(scale_struct_col, "")).strip()
        steps = parse_scale_steps(raw_structure)
        if not steps:
            continue
        notes, chords = build_harmonized_chords(root_note, steps, harmony_tokens)

        _ensure_space(pdf, 118, print_mode)
        pdf.set_font("helvetica", "B", 22)
        pdf.cell(0, 16, f"{root_note} {scale_type}", border=1, ln=True, align="C")
        pdf.ln(9)

        total_width = pdf.w - pdf.l_margin - pdf.r_margin
        left = pdf.l_margin
        note_w = 21.0
        gap_w = (total_width - (note_w * 8)) / 7.0
        if gap_w < 6.0:
            note_w = 18.0
            gap_w = (total_width - (note_w * 8)) / 7.0
        y_deg = pdf.get_y()
        y_note = y_deg + 7
        y_step = y_note + 11

        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(80, 80, 80)
        for i, deg in enumerate(ROMAN_DEGREES):
            x_note = left + i * (note_w + gap_w)
            pdf.set_xy(x_note, y_deg)
            pdf.cell(note_w, 5, deg, align="C")

        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(20, 20, 20)
        for i, note in enumerate(notes):
            x_note = left + i * (note_w + gap_w)
            pdf.rect(x_note, y_note, note_w, 8.5)
            pdf.set_xy(x_note + 0.4, y_note + 1.5)
            pdf.cell(note_w - 0.8, 4, note, align="C")

        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(90, 90, 90)
        for i, step in enumerate(steps):
            x_step = left + i * (note_w + gap_w) + note_w
            pdf.rect(x_step, y_step, gap_w, 6.0)
            pdf.set_xy(x_step, y_step + 1.3)
            pdf.cell(gap_w, 3.5, step_to_label(step), align="C")

        pdf.set_y(y_step + 18)
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 6, f"Estructura: {raw_structure}")
        pdf.ln(3)
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 7, "Acordes de la escala armonizada", ln=True)

        chord_y = pdf.get_y() + 2
        chord_w = (total_width - (6 * 6)) / 7.0
        for i in range(7):
            x = left + i * (chord_w + 6)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_xy(x, chord_y)
            pdf.cell(chord_w, 4, ROMAN_DEGREES[i], align="C")
            pdf.rect(x, chord_y + 5.5, chord_w, 8.5)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_xy(x + 0.2, chord_y + 7.1)
            pdf.cell(chord_w - 0.4, 4, chords[i], align="C")

        pdf.set_y(chord_y + 20)
        if print_mode == "continuous":
            pdf.ln(8)

    return pdf.output()
