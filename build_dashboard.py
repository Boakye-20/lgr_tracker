"""
Rebuilds the Dashboard sheet in AuditTracker.xlsx.

Visual theme: Nottingham City Council Corporate Identity Guidelines.
  - Primary accent: NCC lime green (#78BE20)
  - Title / dark text: NCC near-black navy (#231F20)
  - Alert colours: red / amber as needed
  - Clean white background, no gridlines

Run just before showing the tracker to anyone. Close the workbook first.
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date, datetime

from openpyxl import load_workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

WORKBOOK = "AuditTracker.xlsx"

# ── NCC brand palette ────────────────────────────────────────────────────────
NCC_GREEN  = "78BE20"   # corporate lime green
NCC_DARK   = "231F20"   # near-black (body text / title)
NCC_NAVY   = "00205B"   # deep navy (secondary accent)
NCC_LGREY  = "F4F4F4"   # tile / row background
NCC_MGREY  = "DDDDDD"   # border / rule
RED        = "C0392B"
AMBER      = "D4820A"
GREEN_OK   = "27AE60"
WHITE      = "FFFFFF"

# ── Fonts ────────────────────────────────────────────────────────────────────
F_TITLE    = Font(name="Calibri", color=NCC_DARK,  bold=True,  size=18)
F_SUBTITLE = Font(name="Calibri", color="777777",  italic=True, size=9)
F_SECTION  = Font(name="Calibri", color=WHITE,     bold=True,  size=10)
F_TILE_NUM = Font(name="Calibri", color=WHITE,     bold=True,  size=26)
F_TILE_LBL = Font(name="Calibri", color=WHITE,     bold=True,  size=8)
F_COL_HDR  = Font(name="Calibri", color=WHITE,     bold=True,  size=9)
F_BODY     = Font(name="Calibri", color=NCC_DARK,  size=9)
F_BODY_B   = Font(name="Calibri", color=NCC_DARK,  bold=True,  size=9)
F_ALERT_R  = Font(name="Calibri", color=RED,       bold=True,  size=9)
F_ALERT_A  = Font(name="Calibri", color=AMBER,     bold=True,  size=9)
F_OK       = Font(name="Calibri", color=GREEN_OK,  italic=True, size=9)

# ── Borders ──────────────────────────────────────────────────────────────────
_THIN  = Side(style="thin",   color=NCC_MGREY)
_MED   = Side(style="medium", color=NCC_GREEN)
BORD_THIN  = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
BORD_BOT_G = Border(bottom=Side(style="medium", color=NCC_GREEN))

# ── Fills ────────────────────────────────────────────────────────────────────
def fill(hex_colour):
    return PatternFill("solid", fgColor=hex_colour)


# ── Helpers ──────────────────────────────────────────────────────────────────
def parse_date(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def read_rows(ws):
    headers = [c.value for c in ws[1]]
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        out.append(dict(zip(headers, row)))
    return out


def normalise_dates(ws, col_header):
    headers = [c.value for c in ws[1]]
    if col_header not in headers:
        return
    col = headers.index(col_header) + 1
    for r in range(2, ws.max_row + 1):
        cell = ws.cell(r, col)
        parsed = parse_date(cell.value)
        if parsed is not None:
            cell.value = parsed
            cell.number_format = "yyyy-mm-dd"


def _col(n):
    return get_column_letter(n)


def _merge(ws, c1, r1, c2, r2):
    ws.merge_cells(f"{_col(c1)}{r1}:{_col(c2)}{r2}")


def _cell(ws, col, row, value=None, *, font=None, fill_hex=None,
          align_h="left", align_v="center", wrap=False, border=None, fmt=None):
    c = ws.cell(row=row, column=col, value=value)
    if font:
        c.font = font
    if fill_hex:
        c.fill = fill(fill_hex)
    c.alignment = Alignment(horizontal=align_h, vertical=align_v,
                            wrap_text=wrap)
    if border:
        c.border = border
    if fmt:
        c.number_format = fmt
    return c


def draw_tile(ws, col, row, label, value, colour):
    """3-row tile: accent bar / big number / label."""
    _merge(ws, col, row,   col + 1, row)
    _merge(ws, col, row+1, col + 1, row+1)
    _merge(ws, col, row+2, col + 1, row+2)

    _cell(ws, col, row,   fill_hex=NCC_GREEN)          # green cap
    _cell(ws, col, row+1, value=value,  font=F_TILE_NUM,
          fill_hex=colour, align_h="center")
    _cell(ws, col, row+2, value=label,  font=F_TILE_LBL,
          fill_hex=colour, align_h="center")

    ws.row_dimensions[row].height   = 5
    ws.row_dimensions[row+1].height = 36
    ws.row_dimensions[row+2].height = 14


def section_bar(ws, col_start, col_end, row, label):
    """Full-width green section header bar."""
    _merge(ws, col_start, row, col_end, row)
    _cell(ws, col_start, row, value=label, font=F_SECTION,
          fill_hex=NCC_GREEN, align_h="left")
    ws.row_dimensions[row].height = 18


def col_header_row(ws, col_start, row, labels, colour=NCC_NAVY):
    """Dark header row for a table."""
    for i, lbl in enumerate(labels):
        _cell(ws, col_start + i, row, value=lbl,
              font=F_COL_HDR, fill_hex=colour, align_h="left",
              border=BORD_THIN)
    ws.row_dimensions[row].height = 16


def data_row(ws, col_start, row, values, zebra=False):
    bg = NCC_LGREY if zebra else WHITE
    for i, v in enumerate(values):
        _cell(ws, col_start + i, row, value=v,
              font=F_BODY, fill_hex=bg, border=BORD_THIN)
    ws.row_dimensions[row].height = 14


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    try:
        wb = load_workbook(WORKBOOK)
    except FileNotFoundError:
        print(f"'{WORKBOOK}' not found. Run setup_tracker.py first.")
        sys.exit(1)
    except PermissionError:
        print(f"Cannot open '{WORKBOOK}'. Close it in Excel and run again.")
        sys.exit(1)

    normalise_dates(wb["Obligations"], "Target Date")
    normalise_dates(wb["Actions"], "Due Date")
    normalise_dates(wb["Actions"], "Start Date")

    obligations = read_rows(wb["Obligations"])
    actions     = read_rows(wb["Actions"])
    intel       = read_rows(wb["Intelligence"])
    today       = date.today()

    # ── Obligation metrics ───────────────────────────────────────────────────
    total_ob    = len(obligations)
    complete_ob = sum(1 for o in obligations if o.get("Status") == "Complete")
    high_risk   = sum(1 for o in obligations
                      if o.get("Risk Rating") == "High"
                      and o.get("Status") != "Complete")
    overdue_ob, due_soon_ob = [], []
    for o in obligations:
        t = parse_date(o.get("Target Date"))
        if t and o.get("Status") != "Complete":
            if t < today:
                overdue_ob.append(o)
            elif (t - today).days <= 30:
                due_soon_ob.append(o)

    status_order = ["Not started", "In progress", "Complete", "Blocked", "Ongoing"]
    status_counts = Counter(o.get("Status") or "Not started" for o in obligations)
    risk_counts   = Counter(o.get("Risk Rating") or "Not rated" for o in obligations)
    theme_counts  = Counter(o.get("Theme") or "Other" for o in obligations)

    # ── Action metrics ───────────────────────────────────────────────────────
    total_ac     = len(actions)
    complete_ac  = [a for a in actions if a.get("Status") == "Complete"]
    evid_gaps    = [a for a in complete_ac if not a.get("Evidence Link")]
    evid_pct     = (round(100 * (len(complete_ac) - len(evid_gaps)) / len(complete_ac))
                    if complete_ac else 100)
    overdue_ac   = [a for a in actions
                    if parse_date(a.get("Due Date"))
                    and a.get("Status") not in ("Complete", "Cancelled")
                    and parse_date(a.get("Due Date")) < today]
    pct_vals     = [a["Percent Complete"] for a in actions
                    if isinstance(a.get("Percent Complete"), (int, float))]
    avg_prog     = round(sum(pct_vals) / len(pct_vals)) if pct_vals else 0

    # ── Intelligence metrics ─────────────────────────────────────────────────
    intel_total    = len(intel)
    intel_material = sum(1 for i in intel if i.get("Material") == "Yes")
    intel_unrev    = sum(1 for i in intel if not i.get("Reviewed"))
    intel_recent   = sum(1 for i in intel
                         if i.get("Material") == "Yes"
                         and parse_date(i.get("Date Found"))
                         and (today - parse_date(i.get("Date Found"))).days <= 30)

    # ── Rebuild sheet ────────────────────────────────────────────────────────
    if "Dashboard" in wb.sheetnames:
        del wb["Dashboard"]
    ws = wb.create_sheet("Dashboard", 0)
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90

    # ── Column widths — spread across the full sheet ────────────────────────
    col_widths = {
        1:  3,   # A  spacer
        2:  28,  # B  content
        3:  13,  # C  value
        4:  5,   # D  gap
        5:  28,  # E  content
        6:  13,  # F  value
        7:  5,   # G  gap
        8:  28,  # H  content
        9:  13,  # I  value
        10: 5,   # J  gap
        11: 22,  # K  content
        12: 12,  # L  value
        13: 5,   # M  trailing gap
    }
    LAST_COL = 13   # rightmost column used by section bars / header
    for c, w in col_widths.items():
        ws.column_dimensions[_col(c)].width = w

    # ════════════════════════════════════════════════════════════════════════
    # HEADER  (rows 1-5)
    # ════════════════════════════════════════════════════════════════════════
    ws.row_dimensions[1].height = 6

    # Green accent stripe
    for c in range(1, LAST_COL + 1):
        _cell(ws, c, 2, fill_hex=NCC_GREEN)
    ws.row_dimensions[2].height = 4

    _merge(ws, 2, 3, LAST_COL, 3)
    _cell(ws, 2, 3, "NCC Audit Reform and LGR Obligations Tracker",
          font=F_TITLE)
    ws.row_dimensions[3].height = 28

    _merge(ws, 2, 4, LAST_COL, 4)
    _cell(ws, 2, 4,
          f"Live status snapshot  ·  Refreshed {today.strftime('%d %B %Y')}",
          font=F_SUBTITLE)
    ws.row_dimensions[4].height = 14

    ws.row_dimensions[5].height = 8

    # ════════════════════════════════════════════════════════════════════════
    # KPI TILES  (rows 6-8)
    # ════════════════════════════════════════════════════════════════════════
    tiles = [
        (2,  "OBLIGATIONS",    total_ob,         NCC_NAVY),
        (5,  "OVERDUE",        len(overdue_ob),  RED   if overdue_ob  else GREEN_OK),
        (8,  "DUE IN 30 DAYS", len(due_soon_ob), AMBER if due_soon_ob else GREEN_OK),
        (11, "COMPLETE",       complete_ob,      GREEN_OK),
    ]
    for col, lbl, val, colour in tiles:
        draw_tile(ws, col, 6, lbl, val, colour)

    ws.row_dimensions[9].height = 10

    # ════════════════════════════════════════════════════════════════════════
    # OBLIGATIONS BREAKDOWN  (rows 10-28)
    # ════════════════════════════════════════════════════════════════════════
    section_bar(ws, 2, LAST_COL, 10, "  OBLIGATIONS OVERVIEW")
    ws.row_dimensions[10].height = 18
    ws.row_dimensions[11].height = 6

    # --- By Status (cols B-C) ---
    _cell(ws, 2, 12, "Obligations by Status", font=F_BODY_B)
    ws.row_dimensions[12].height = 14
    col_header_row(ws, 2, 13, ["Status", "Count"])
    status_pairs = [(s, status_counts.get(s, 0)) for s in status_order]
    for i, (name, cnt) in enumerate(status_pairs):
        data_row(ws, 2, 14 + i, [name, cnt], zebra=(i % 2 == 1))

    # --- By Risk (cols E-F) ---
    _cell(ws, 5, 12, "Obligations by Risk", font=F_BODY_B)
    col_header_row(ws, 5, 13, ["Risk Rating", "Count"])
    risk_order = ["High", "Medium", "Low"]
    for i, r in enumerate(risk_order):
        data_row(ws, 5, 14 + i, [r, risk_counts.get(r, 0)], zebra=(i % 2 == 1))

    # --- By Theme (cols H-I) ---
    _cell(ws, 8, 12, "Obligations by Theme", font=F_BODY_B)
    col_header_row(ws, 8, 13, ["Theme", "Count"])
    theme_pairs = sorted(theme_counts.items(), key=lambda x: -x[1])
    for i, (name, cnt) in enumerate(theme_pairs):
        data_row(ws, 8, 14 + i, [name, cnt], zebra=(i % 2 == 1))

    # charts row
    chart_row = 19

    # Status bar chart — vertical bars, value labels on each bar
    sc = BarChart()
    sc.title    = "Obligations by Status"
    sc.height   = 9
    sc.width    = 14
    sc.legend   = None
    sc.grouping = "clustered"
    sc.type     = "col"
    sc.add_data(Reference(ws, min_col=3, min_row=13, max_row=18),
                titles_from_data=True)
    sc.set_categories(Reference(ws, min_col=2, min_row=14, max_row=18))
    sc.series[0].graphicalProperties.solidFill = NCC_GREEN
    sc.series[0].graphicalProperties.line.solidFill = NCC_GREEN
    sc.dLbls = DataLabelList()
    sc.dLbls.showVal     = True
    sc.dLbls.showCatName = False
    sc.dLbls.showSerName = False
    ws.add_chart(sc, f"B{chart_row}")

    # Risk pie chart — slices labelled with category name + percentage
    pc = PieChart()
    pc.title  = "Obligations by Risk"
    pc.height = 9
    pc.width  = 12
    pc.add_data(Reference(ws, min_col=6, min_row=13, max_row=16),
                titles_from_data=True)
    pc.set_categories(Reference(ws, min_col=5, min_row=14, max_row=16))
    slice_colours = [RED, AMBER, GREEN_OK]
    for idx, hex_c in enumerate(slice_colours):
        pt = DataPoint(idx=idx)
        pt.graphicalProperties.solidFill = hex_c
        pt.graphicalProperties.line.noFill = True
        pc.series[0].dPt.append(pt)
    pc.dLbls = DataLabelList()
    pc.dLbls.showCatName = True
    pc.dLbls.showPercent = True
    pc.dLbls.showVal     = False
    pc.dLbls.showSerName = False
    ws.add_chart(pc, f"E{chart_row}")

    # Theme bar chart — horizontal so long theme names are fully readable
    tc = BarChart()
    tc.title  = "Obligations by Theme"
    tc.height = 9
    tc.width  = 14
    tc.legend = None
    tc.type   = "bar"   # horizontal — categories appear on left Y-axis
    n_themes  = len(theme_pairs)
    tc.add_data(Reference(ws, min_col=9, min_row=13, max_row=13 + n_themes),
                titles_from_data=True)
    tc.set_categories(Reference(ws, min_col=8, min_row=14, max_row=13 + n_themes))
    tc.series[0].graphicalProperties.solidFill = NCC_NAVY
    tc.series[0].graphicalProperties.line.solidFill = NCC_NAVY
    # Ensure both axes render — openpyxl can silently drop them
    tc.x_axis.delete = False
    tc.y_axis.delete = False
    tc.dLbls = DataLabelList()
    tc.dLbls.showVal     = True
    tc.dLbls.showCatName = False
    tc.dLbls.showSerName = False
    ws.add_chart(tc, f"H{chart_row}")

    # ════════════════════════════════════════════════════════════════════════
    # ACTIONS & INTELLIGENCE  (rows 30-38)
    # ════════════════════════════════════════════════════════════════════════
    ai_top = 40
    ws.row_dimensions[ai_top - 1].height = 8
    section_bar(ws, 2, LAST_COL, ai_top, "  ACTIONS & INTELLIGENCE FEED")

    # Actions table
    col_header_row(ws, 2, ai_top + 1, ["Action Summary", "Count"])
    action_lines = [
        ("Total actions",      total_ac),
        ("In progress",        sum(1 for a in actions if a.get("Status") == "In progress")),
        ("Complete",           len(complete_ac)),
        ("Overdue",            len(overdue_ac)),
        ("Avg. progress",      f"{avg_prog}%"),
        ("Evidence coverage",  f"{evid_pct}%"),
    ]
    for i, (lbl, val) in enumerate(action_lines):
        data_row(ws, 2, ai_top + 2 + i, [lbl, val], zebra=(i % 2 == 1))

    # Intelligence table
    col_header_row(ws, 5, ai_top + 1, ["Intelligence Feed", "Count"])
    intel_lines = [
        ("Items captured",        intel_total),
        ("Flagged material",       intel_material),
        ("Material (last 30 days)", intel_recent),
        ("Awaiting review",        intel_unrev),
    ]
    for i, (lbl, val) in enumerate(intel_lines):
        data_row(ws, 5, ai_top + 2 + i, [lbl, val], zebra=(i % 2 == 1))

    # ════════════════════════════════════════════════════════════════════════
    # ATTENTION NEEDED  (rows 40+)
    # ════════════════════════════════════════════════════════════════════════
    attn_top = 52
    ws.row_dimensions[attn_top - 1].height = 8
    section_bar(ws, 2, LAST_COL, attn_top, "  ATTENTION NEEDED")

    col_header_row(ws, 2, attn_top + 1,
                   ["ID", "Obligation", "", "Owner", "Target", "Status"])

    flagged = [(o, "Overdue") for o in overdue_ob] + \
              [(o, "Due soon") for o in due_soon_ob]

    if not flagged:
        _merge(ws, 2, attn_top + 2, 7, attn_top + 2)
        _cell(ws, 2, attn_top + 2,
              "Nothing overdue or due within 30 days — all obligations on track.",
              font=F_OK, fill_hex=WHITE)
        ws.row_dimensions[attn_top + 2].height = 14
    else:
        for i, (o, why) in enumerate(flagged):
            r = attn_top + 2 + i
            bg = NCC_LGREY if i % 2 == 1 else WHITE
            target = parse_date(o.get("Target Date"))
            why_font = F_ALERT_R if why == "Overdue" else F_ALERT_A

            _cell(ws, 2, r, o.get("Obligation ID", ""), font=F_BODY_B,
                  fill_hex=bg, border=BORD_THIN)
            _merge(ws, 3, r, 4, r)
            _cell(ws, 3, r, (o.get("Obligation") or "")[:80], font=F_BODY,
                  fill_hex=bg, border=BORD_THIN, wrap=True)
            _cell(ws, 5, r, o.get("Owner") or "Unassigned", font=F_BODY,
                  fill_hex=bg, border=BORD_THIN)
            _cell(ws, 6, r, target.strftime("%d %b %Y") if target else "",
                  font=F_BODY, fill_hex=bg, border=BORD_THIN)
            _cell(ws, 7, r, why, font=why_font, fill_hex=bg,
                  border=BORD_THIN, align_h="center")
            ws.row_dimensions[r].height = 28

    # ── Footer ───────────────────────────────────────────────────────────────
    footer_row = attn_top + 3 + max(len(flagged), 1) + 1
    ws.row_dimensions[footer_row].height = 4
    for c in range(1, LAST_COL + 1):
        _cell(ws, c, footer_row, fill_hex=NCC_GREEN)

    try:
        wb.save(WORKBOOK)
    except PermissionError:
        print(f"Cannot save '{WORKBOOK}'. Close it in Excel and run again.")
        sys.exit(1)

    print(f"Dashboard refreshed for {today.strftime('%d %B %Y')}.")
    print(f"  Obligations: {total_ob}  Overdue: {len(overdue_ob)}  Due soon: {len(due_soon_ob)}")
    print(f"  Actions: {total_ac}  Overdue: {len(overdue_ac)}  Evidence coverage: {evid_pct}%")
    print(f"  Intelligence: {intel_total} captured, {intel_material} material, {intel_unrev} awaiting review")


if __name__ == "__main__":
    main()
