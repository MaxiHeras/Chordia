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
from chordia.relative_comparison import ROMAN_HEADER, build_comparison_data, quality_fill_rgb
from chordia.scales import ROMAN_DEGREES, build_scale, detect_scale_columns, parse_scale_steps, step_to_label


class ChordiaPDF(FPDF):
    def __init__(self, app_public_url: str, **kwargs):
        super().__init__(**kwargs)
        self._app_public_url = app_public_url

    def footer(self) -> None:
        self.set_y(-30)
        qr_x = 174
        qr_w = 20
        qr_url = (
            "https://api.qrserver.com/v1/create-qr-code/?size=100x100&data="
            f"{urllib.parse.quote(self._app_public_url)}"
        )
        try:
            self.image(qr_url, x=qr_x, y=self.get_y(), w=qr_w, h=qr_w)
        except Exception:
            pass
        self.set_y(self.get_y() + 22)
        self.set_font("helvetica", "", 9)
        self.set_text_color(128, 128, 128)
        caption = "by Maxi Heras - Tucumán"
        text_w = self.get_string_width(caption) + 1.5
        qr_center_x = qr_x + (qr_w / 2)
        min_x = self.l_margin
        max_x = self.w - self.r_margin - text_w
        text_x = min(max(qr_center_x - (text_w / 2), min_x), max_x)
        self.set_x(text_x)
        self.cell(text_w, 5, caption, align="C", ln=True)


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
    # Layout (mm): mismo margen izquierdo para texto y rejilla; mismo hueco vertical
    # entre líneas de datos, entre bloque texto y diagramas, y entre filas de diagramas.
    _MARGIN_X = 15
    _TEXT_LINE_H = 6
    _GAP_AFTER_TITLE = 8
    _VERTICAL_RHYTHM = 12
    _GAP_X = 8
    _COLS = 4
    _DIAG_W, _DIAG_H = 38, 45

    diag_values: list[str] = []
    for i in range(1, DIAGRAM_COUNT + 1):
        val = str(row.get(f"Diagrama{i}", "nan")).strip()
        if val.lower().endswith(".png"):
            diag_values.append(val)

    diag_rows = max(1, (len(diag_values) + _COLS - 1) // _COLS) if diag_values else 1
    row_stride = _DIAG_H + _VERTICAL_RHYTHM
    needed_height = 70 + (diag_rows * row_stride)
    _ensure_space(pdf, needed_height, print_mode)

    pdf.set_font("helvetica", "B", 24)
    pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align="C")
    pdf.ln(_GAP_AFTER_TITLE)
    pdf.set_x(_MARGIN_X)
    pdf.set_font("helvetica", "B", 11)
    pdf.write(_TEXT_LINE_H, "Notas: ")
    pdf.set_font("helvetica", "", 11)
    pdf.write(_TEXT_LINE_H, f"{' - '.join(row_note_list(row))}\n")
    pdf.set_x(_MARGIN_X)
    pdf.set_font("helvetica", "B", 11)
    pdf.write(_TEXT_LINE_H, "Int_IVAN: ")
    pdf.set_font("helvetica", "", 11)
    pdf.write(_TEXT_LINE_H, f"{str(row.get('Int_IVAN', 'N/A'))}\n")
    pdf.set_x(_MARGIN_X)
    pdf.set_font("helvetica", "B", 11)
    pdf.write(_TEXT_LINE_H, "Int_TRAD: ")
    pdf.set_font("helvetica", "", 11)
    pdf.write(_TEXT_LINE_H, f"{str(row.get('Int_TRAD', 'N/A'))}\n")
    pdf.ln(_VERTICAL_RHYTHM)

    x_start, gap_x, gap_y, cols, diag_w, diag_h = _MARGIN_X, _GAP_X, _VERTICAL_RHYTHM, _COLS, _DIAG_W, _DIAG_H
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
                pos_y = y_grid_top + (fila * row_stride)
                pdf.image(BytesIO(img_data), x=pos_x, y=pos_y, w=diag_w, h=diag_h)
                count += 1
        except Exception:
            continue

    # Separación visual entre secciones en modo continuo.
    if print_mode == "continuous":
        pdf.set_y(max(pdf.get_y(), y_grid_top + (diag_rows * row_stride)))
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


def build_relative_comparison_pdf(
    major_root: str,
    minor_root: str,
    app_public_url: str,
    print_mode: str = "current_view",
) -> bytes:
    """Una página con tablas mayor / menor relativas (como la vista principal)."""
    data = build_comparison_data(major_root, minor_root)
    pdf = ChordiaPDF(app_public_url, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=35)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    # Helvetica estandar: evitar guiones Unicode (p. ej. U+2014) que rompen la exportacion.
    pdf.cell(0, 10, "Relativas y comparacion", border=0, ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        0,
        6,
        f"Mayor: {data.major_root} - Menor relativa: {data.minor_root}",
        ln=True,
        align="C",
    )
    pdf.ln(4)

    total_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_label = 20.0
    cell_w = (total_w - col_label) / 7.0
    h_row = 6.0
    left = pdf.l_margin

    _spacer_fill = (248, 250, 252)

    def row_line(
        label: str,
        cells: list[str],
        *,
        colorize: bool = False,
        band_fill: bool = False,
    ) -> None:
        pdf.set_x(left)
        pdf.set_font("helvetica", "B", 8)
        if band_fill and not colorize:
            pdf.set_fill_color(*_spacer_fill)
            pdf.cell(col_label, h_row, label, border=1, fill=True)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_label, h_row, label, border=1)
        pdf.set_font("helvetica", "", 8)
        for c in cells:
            txt = c.replace("—", "-")
            if colorize:
                r, g, b = quality_fill_rgb(c)
                pdf.set_fill_color(r, g, b)
                pdf.cell(cell_w, h_row, txt, border=1, align="C", fill=True)
            elif band_fill:
                pdf.set_fill_color(*_spacer_fill)
                pdf.cell(cell_w, h_row, txt, border=1, align="C", fill=True)
            else:
                pdf.set_fill_color(255, 255, 255)
                pdf.cell(cell_w, h_row, txt, border=1, align="C", fill=False)
        pdf.ln(h_row)

    show_root_row = print_mode != "without_root"
    title_h = 7 if show_root_row else 6
    gap_between_tables = 7 if show_root_row else 5

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, title_h, "Tonalidad mayor", ln=True)
    pdf.set_font("helvetica", "", 8)
    if show_root_row:
        row_line("Raíz", data.major_degrees_notes)
        row_line("", [""] * 7, band_fill=True)
    row_line("Grados", list(ROMAN_HEADER))
    row_line("EM", data.major_harm_row, colorize=True)
    pdf.ln(gap_between_tables)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, title_h, "Tonalidad menor", ln=True)
    pdf.set_font("helvetica", "", 8)
    if show_root_row:
        row_line("Raíz", data.minor_degrees_notes)
        row_line("", [""] * 7, band_fill=True)
    row_line("Grados", list(ROMAN_HEADER))
    row_line("EmN", data.minor_emn, colorize=True)
    row_line("EmA", data.minor_ema_display, colorize=True)
    row_line("EmM", data.minor_emm_display, colorize=True)

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
