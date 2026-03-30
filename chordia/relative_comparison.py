"""Relativas mayores/menores: armónicos diatónicos y tablas comparativas (menor natural, armónica, melódica)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from chordia.scales import ROMAN_DEGREES, build_scale, roots_for_alteration
from chordia.scales import _note_pitch_class  # noqa: SLF001

# Patrones en semitonos (7 intervalos entre grados consecutivos).
_MAJOR_STEPS = [2, 2, 1, 2, 2, 2, 1]
_NATURAL_MINOR_STEPS = [2, 1, 2, 2, 1, 2, 2]
_HARMONIC_MINOR_STEPS = [2, 1, 2, 2, 1, 3, 1]
_MELODIC_MINOR_STEPS = [2, 1, 2, 2, 2, 2, 1]

_DEGREES = list(range(7))


def _strip_note_label(formatted: str) -> str:
    return formatted.split("(")[0].strip()


def triad_quality_token(root_pc: int, third_pc: int, fifth_pc: int, *, prefer_sharp_dim: bool) -> str:
    """Clasifica tríada (root, tercera, quinta) como M / m / dism / aum / #dism."""
    third = (third_pc - root_pc) % 12
    fifth = (fifth_pc - root_pc) % 12
    if third == 4 and fifth == 7:
        return "M"
    if third == 3 and fifth == 7:
        return "m"
    if third == 3 and fifth == 6:
        return "#dism" if prefer_sharp_dim else "dism"
    if third == 4 and fifth == 8:
        return "aum"
    return "?"


def scale_pitch_classes(root_note: str, steps: list[int]) -> list[int]:
    """Clases de altura de los 7 grados (I–VII), sin duplicar la tónica al final."""
    current = _note_pitch_class(root_note)
    out = [current]
    for s in steps:
        current = (current + s) % 12
        out.append(current)
    return out[:7]


def _apply_special_dim_labels(qualities: list[str], kind: str) -> list[str]:
    q = qualities[:]
    if kind == "harmonic" and q[6] in ("dism",):
        q[6] = "#dism"
    if kind == "melodic":
        if q[5] in ("dism",):
            q[5] = "#dism"
        if q[6] in ("dism",):
            q[6] = "#dism"
    return q


def major_harmonization_tokens(root_major: str) -> list[str]:
    pcs = scale_pitch_classes(root_major, _MAJOR_STEPS)
    q: list[str] = []
    for i in _DEGREES:
        r, t, f = pcs[i], pcs[(i + 2) % 7], pcs[(i + 4) % 7]
        q.append(triad_quality_token(r, t, f, prefer_sharp_dim=False))
    return q


def minor_natural_tokens(root_minor: str) -> list[str]:
    pcs = scale_pitch_classes(root_minor, _NATURAL_MINOR_STEPS)
    q = [
        triad_quality_token(pcs[i], pcs[(i + 2) % 7], pcs[(i + 4) % 7], prefer_sharp_dim=False)
        for i in _DEGREES
    ]
    return q


def minor_harmonic_tokens(root_minor: str) -> list[str]:
    pcs = scale_pitch_classes(root_minor, _HARMONIC_MINOR_STEPS)
    q = [
        triad_quality_token(pcs[i], pcs[(i + 2) % 7], pcs[(i + 4) % 7], prefer_sharp_dim=(i == 6))
        for i in _DEGREES
    ]
    return _apply_special_dim_labels(q, "harmonic")


def minor_melodic_tokens(root_minor: str) -> list[str]:
    pcs = scale_pitch_classes(root_minor, _MELODIC_MINOR_STEPS)
    q = [
        triad_quality_token(pcs[i], pcs[(i + 2) % 7], pcs[(i + 4) % 7], prefer_sharp_dim=(i in (5, 6)))
        for i in _DEGREES
    ]
    return _apply_special_dim_labels(q, "melodic")


def compress_row(compared: list[str], reference: list[str]) -> list[str]:
    """Guion (—) donde el valor coincide con la fila de referencia (ya resuelta)."""
    return [("—" if compared[i] == reference[i] else compared[i]) for i in _DEGREES]


def relative_minor_from_major(major_root: str) -> str:
    notes = build_scale(major_root, _MAJOR_STEPS)
    return _strip_note_label(notes[5])


def relative_major_from_minor(minor_root: str) -> str:
    notes = build_scale(minor_root, _NATURAL_MINOR_STEPS)
    return _strip_note_label(notes[2])


def pick_root_for_pc(pc_target: int, options: list[str]) -> str:
    for o in options:
        if _note_pitch_class(o) == pc_target:
            return o
    return options[0] if options else "C"


def relative_minor_option(major_root: str, root_options: list[str]) -> str:
    m_pc = (_note_pitch_class(major_root) + 9) % 12
    return pick_root_for_pc(m_pc, root_options)


def relative_major_option(minor_root: str, root_options: list[str]) -> str:
    maj_pc = (_note_pitch_class(minor_root) + 3) % 12
    return pick_root_for_pc(maj_pc, root_options)


_MAYOR_COL_CANDIDATES = ("Mayor", "MAYOR")
_MENOR_COL_CANDIDATES = ("Menor", "MENOR", "Menor relativa", "Relativa menor")


def _sanitize_rel_sheet_cell(raw: object) -> str:
    """Quita texto aclaratorio tipo 'Cb (B)' o 'C## (D)' para coincidir con las tónicas del filtro."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if "(" in s:
        s = s.split("(", maxsplit=1)[0].strip()
    return s


def _match_sheet_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    for raw in columns:
        norm = str(raw).strip()
        for cand in candidates:
            if norm.lower() == cand.strip().lower():
                return norm
    return None


@dataclass(frozen=True)
class RelativeKeyPairs:
    """Pares leídos de Sheets: orden de filas define el orden de los desplegables."""

    majors_in_order: tuple[str, ...]
    major_to_minor: dict[str, str]
    minor_to_major: dict[str, str]


def build_relative_key_pairs(df: pd.DataFrame | None) -> RelativeKeyPairs | None:
    if df is None or df.empty:
        return None
    maj_c = _match_sheet_column(list(df.columns), _MAYOR_COL_CANDIDATES)
    men_c = _match_sheet_column(list(df.columns), _MENOR_COL_CANDIDATES)
    if not maj_c or not men_c:
        return None
    rows: list[tuple[str, str]] = []
    for _, r in df.iterrows():
        maj = _sanitize_rel_sheet_cell(r.get(maj_c))
        men = _sanitize_rel_sheet_cell(r.get(men_c))
        if maj and men:
            rows.append((maj, men))
    if not rows:
        return None
    major_to_minor: dict[str, str] = {}
    majors_order: list[str] = []
    for maj, men in rows:
        if maj not in major_to_minor:
            major_to_minor[maj] = men
            majors_order.append(maj)
    minor_to_major: dict[str, str] = {}
    for maj, men in rows:
        minor_to_major[men] = maj
    return RelativeKeyPairs(tuple(majors_order), major_to_minor, minor_to_major)


def first_major_for_filter(filtro: str, pairs: RelativeKeyPairs | None) -> str:
    allowed = roots_for_alteration(filtro)
    if pairs is not None:
        for m in pairs.majors_in_order:
            if m in allowed:
                return m
    return allowed[0]


def _rel_opts_from_sheet(
    filtro: str,
    pairs: RelativeKeyPairs,
    maj_root: str,
    min_root: str,
) -> list[str]:
    allowed = set(roots_for_alteration(filtro))
    majors = [m for m in pairs.majors_in_order if m in allowed]
    if not majors:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for m in majors:
        mn = pairs.major_to_minor.get(m, "")
        for note in (m, mn):
            if note and note not in seen:
                out.append(note)
                seen.add(note)
    for n in (maj_root, min_root):
        if n and n not in seen:
            out.append(n)
            seen.add(n)
    exp_mn = pairs.major_to_minor.get(maj_root)
    if exp_mn and exp_mn not in seen:
        out.append(exp_mn)
        seen.add(exp_mn)
    exp_maj = pairs.minor_to_major.get(min_root)
    if exp_maj and exp_maj not in seen:
        out.append(exp_maj)
        seen.add(exp_maj)
    return out


def rel_comp_root_options(
    filtro: str,
    maj_root: str,
    min_root: str,
    pairs: RelativeKeyPairs | None = None,
) -> list[str]:
    """
    Opciones del desplegable: desde la hoja Mayor/Menor si existe y hay filas del filtro,
    si no como antes (7 del filtro + enarmónicas del par teórico).
    """
    if pairs is not None:
        sheet_opts = _rel_opts_from_sheet(filtro, pairs, maj_root, min_root)
        if sheet_opts:
            return sheet_opts
    base = roots_for_alteration(filtro)
    out: list[str] = list(base)
    seen = set(base)
    for n in (
        relative_minor_from_major(maj_root),
        relative_major_from_minor(min_root),
        maj_root,
        min_root,
    ):
        if n and n not in seen:
            out.append(n)
            seen.add(n)
    return out


def sync_minor_from_major_for_options(
    major_root: str,
    filtro: str,
    min_root: str,
    pairs: RelativeKeyPairs | None = None,
) -> str:
    if pairs is not None and major_root in pairs.major_to_minor:
        spelled = pairs.major_to_minor[major_root]
        opts = rel_comp_root_options(filtro, major_root, min_root, pairs)
        if spelled in opts:
            return spelled
        return pick_root_for_pc(_note_pitch_class(spelled), opts)
    spelled = relative_minor_from_major(major_root)
    opts = rel_comp_root_options(filtro, major_root, min_root, pairs)
    if spelled in opts:
        return spelled
    return pick_root_for_pc(_note_pitch_class(spelled), opts)


def sync_major_from_minor_for_options(
    minor_root: str,
    filtro: str,
    maj_root: str,
    pairs: RelativeKeyPairs | None = None,
) -> str:
    if pairs is not None and minor_root in pairs.minor_to_major:
        spelled = pairs.minor_to_major[minor_root]
        opts = rel_comp_root_options(filtro, maj_root, minor_root, pairs)
        if spelled in opts:
            return spelled
        return pick_root_for_pc(_note_pitch_class(spelled), opts)
    spelled = relative_major_from_minor(minor_root)
    opts = rel_comp_root_options(filtro, maj_root, minor_root, pairs)
    if spelled in opts:
        return spelled
    return pick_root_for_pc(_note_pitch_class(spelled), opts)


def rel_comp_pair_is_consistent(
    maj_root: str,
    min_root: str,
    pairs: RelativeKeyPairs | None = None,
) -> bool:
    """True si el par coincide con Sheets (si aplica) o con la relativa teórica."""
    if pairs is not None and maj_root in pairs.major_to_minor:
        return _note_pitch_class(min_root) == _note_pitch_class(pairs.major_to_minor[maj_root])
    if pairs is not None and min_root in pairs.minor_to_major:
        return _note_pitch_class(maj_root) == _note_pitch_class(pairs.minor_to_major[min_root])
    return (
        _note_pitch_class(min_root) == _note_pitch_class(relative_minor_from_major(maj_root))
        or _note_pitch_class(maj_root) == _note_pitch_class(relative_major_from_minor(min_root))
    )


@dataclass
class RelativeComparisonData:
    major_root: str
    minor_root: str
    major_degrees_notes: list[str]  # 7 notas (I–VII), ya formateadas
    minor_degrees_notes: list[str]
    major_harm_row: list[str]  # EM
    minor_emn: list[str]
    minor_ema_display: list[str]
    minor_emm_display: list[str]


def build_comparison_data(major_root: str, minor_root: str) -> RelativeComparisonData:
    maj_scale = build_scale(major_root, _MAJOR_STEPS)
    min_scale_nat = build_scale(minor_root, _NATURAL_MINOR_STEPS)

    major_degrees_notes = [_strip_note_label(n) for n in maj_scale[:7]]
    minor_degrees_notes = [_strip_note_label(n) for n in min_scale_nat[:7]]

    em = major_harmonization_tokens(major_root)
    emn = minor_natural_tokens(minor_root)
    ema_full = minor_harmonic_tokens(minor_root)
    emm_full = minor_melodic_tokens(minor_root)

    ema_disp = compress_row(ema_full, emn)
    ema_resolved = [ema_full[i] if ema_disp[i] != "—" else emn[i] for i in _DEGREES]
    emm_disp = compress_row(emm_full, ema_resolved)

    return RelativeComparisonData(
        major_root=major_root,
        minor_root=minor_root,
        major_degrees_notes=major_degrees_notes,
        minor_degrees_notes=minor_degrees_notes,
        major_harm_row=em,
        minor_emn=emn,
        minor_ema_display=ema_disp,
        minor_emm_display=emm_disp,
    )


ROMAN_HEADER = ROMAN_DEGREES[:-1]

# Misma plantilla de columnas en mayor y menor para que las celdas encajen verticalmente.
_REL_COMP_COLGROUP = (
    "<colgroup>"
    '<col class="rel-comp-col-corner" />'
    '<col class="rel-comp-col-label" />'
    '<col class="rel-comp-col-data" /><col class="rel-comp-col-data" /><col class="rel-comp-col-data" />'
    '<col class="rel-comp-col-data" /><col class="rel-comp-col-data" /><col class="rel-comp-col-data" /><col class="rel-comp-col-data" />'
    "</colgroup>"
)


def quality_cell_class(token: str) -> str:
    """Clases para colorear celdas de calidad (EM, EmN, EmA, EmM)."""
    t = (token or "").strip()
    if t in ("—", "-", "–", "\u2014"):
        return "rel-comp-q rel-comp-q-same"
    if t == "M":
        return "rel-comp-q rel-comp-q-mayor"
    if t == "m":
        return "rel-comp-q rel-comp-q-menor"
    if t in ("dism", "#dism"):
        return "rel-comp-q rel-comp-q-dism"
    if t == "aum":
        return "rel-comp-q rel-comp-q-aum"
    return ""


def quality_fill_rgb(token: str) -> tuple[int, int, int]:
    """RGB 0–255 para relleno de celdas en PDF (misma leyenda que la web)."""
    t = (token or "").strip()
    if t in ("—", "-", "–", "\u2014"):
        # Gris de repetición un poco más claro para impresión en papel.
        return (170, 181, 198)
    if t == "M":
        return (143, 209, 143)
    if t == "m":
        return (254, 249, 195)
    if t in ("dism", "#dism"):
        return (254, 215, 170)
    if t == "aum":
        return (147, 197, 253)
    return (255, 255, 255)


def render_relative_comparison_html(data: RelativeComparisonData, compact: bool) -> str:
    wrap = "rel-comp-wrap rel-comp-compact" if compact else "rel-comp-wrap"

    def major_table() -> str:
        b = ['<table class="rel-comp-table">', _REL_COMP_COLGROUP]
        b.append(
            f'<tr><th class="rel-comp-corner" rowspan="4"><span class="rel-comp-vtitle">TONALIDAD MAYOR</span></th>'
            f'<th class="rel-comp-left">Raíz</th>'
        )
        for n in data.major_degrees_notes:
            b.append(f'<td class="rel-comp-cell rel-comp-strong">{n}</td>')
        b.append("</tr>")
        b.append(
            '<tr class="rel-comp-spacer-row"><th class="rel-comp-left"></th>'
            + "".join('<td class="rel-comp-cell rel-comp-spacer"></td>' for _ in range(7))
            + "</tr>",
        )
        b.append('<tr><th class="rel-comp-left">Grados</th>')
        for d in ROMAN_HEADER:
            b.append(f'<td class="rel-comp-cell rel-comp-deg">{d}</td>')
        b.append("</tr>")
        b.append('<tr><th class="rel-comp-left">EM</th>')
        for t in data.major_harm_row:
            qc = quality_cell_class(t)
            cls = f"rel-comp-cell {qc}".strip()
            b.append(f'<td class="{cls}">{t}</td>')
        b.append("</tr></table>")
        return "".join(b)

    def minor_table() -> str:
        b = ['<table class="rel-comp-table">', _REL_COMP_COLGROUP]
        b.append(
            f'<tr><th class="rel-comp-corner" rowspan="6"><span class="rel-comp-vtitle">TONALIDAD MENOR</span></th>'
            f'<th class="rel-comp-left">Raíz</th>'
        )
        for n in data.minor_degrees_notes:
            b.append(f'<td class="rel-comp-cell rel-comp-strong">{n}</td>')
        b.append("</tr>")
        b.append(
            '<tr class="rel-comp-spacer-row"><th class="rel-comp-left"></th>'
            + "".join('<td class="rel-comp-cell rel-comp-spacer"></td>' for _ in range(7))
            + "</tr>",
        )
        b.append('<tr><th class="rel-comp-left">Grados</th>')
        for d in ROMAN_HEADER:
            b.append(f'<td class="rel-comp-cell rel-comp-deg">{d}</td>')
        b.append("</tr>")
        for label, rowdata in [("EmN", data.minor_emn), ("EmA", data.minor_ema_display), ("EmM", data.minor_emm_display)]:
            b.append(f'<tr><th class="rel-comp-left">{label}</th>')
            for t in rowdata:
                display = "—" if t == "—" else t
                qc = quality_cell_class(t)
                cls = f"rel-comp-cell {qc}".strip()
                b.append(f'<td class="{cls}">{display}</td>')
            b.append("</tr>")
        b.append("</table>")
        return "".join(b)

    return f'<div class="{wrap}">{major_table()}{minor_table()}</div>'
