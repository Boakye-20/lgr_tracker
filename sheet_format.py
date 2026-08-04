"""
Table formatting for the data sheets (Obligations, Actions, Intelligence).

Why this exists: the long free-text columns (Obligation, Notes, Source / Trigger)
spill sideways over their neighbours when a cell has no wrapping. On the
Obligations sheet that meant obligation text visually covering the Evidence
Location column, so blank evidence cells looked populated. On an audit tracker
that is worse than ugly — it reads as assurance that is not there.

Wrapping keeps every value inside its own cell; the borders and banding then
make the row boundaries obvious once the rows are tall.

populate_tracker.py rewrites Obligations and Actions from scratch and
update_intelligence.py appends to Intelligence, so both call this afterwards to
put the formatting back.
"""

from __future__ import annotations

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
BAND_FILL = PatternFill("solid", fgColor="F2F5FA")
BODY_FONT = Font(size=10)

_EDGE = Side(style="thin", color="B4C6E7")
BORDER = Border(left=_EDGE, right=_EDGE, top=_EDGE, bottom=_EDGE)

# Roughly three lines at 10pt (Excel gives ~12.75 points per line), plus padding.
# Excel only auto-fits a wrapped row when its height is unset, so capping the
# tall rows means fixing every row — there is no "auto-fit up to a maximum".
# Long values are still complete in the cell, just clipped visually; click the
# cell and read the formula bar, or widen the row, to see the rest.
ROW_HEIGHT = 40

# Width per column name. Anything not listed falls back to DEFAULT_WIDTH.
# Long prose columns are kept narrow enough that wrapping actually kicks in —
# a very wide column just recreates the sprawl in a different shape.
WIDTHS = {
    "Obligation ID": 11,
    "Action ID": 10,
    "Parent Obligation ID": 12,
    "Obligation": 46,
    "Linked Actions": 16,
    "Action": 46,
    "Source \\ Trigger": 28,
    "Source / Trigger": 28,
    "Theme": 16,
    "Owner": 22,
    "Risk Rating": 9,
    "Target Date": 11,
    "Start Date": 10,
    "Due Date": 10,
    "Status": 12,
    "Percent Complete": 9,
    "Evidence Required": 30,
    "Evidence Location": 28,
    "Evidence Link": 28,
    "Sign Off By": 18,
    "Last Updated": 11,
    "Notes": 40,
    "Obligation Level": 12,
    # Intelligence
    "Date Found": 11,
    "Title": 46,
    "Published": 10,
    "Material": 9,
    "Matched": 18,
    "URL": 26,
    "Reviewed": 9,
    "Hash": 12,
    "Action Signal": 18,
    "Category": 14,
    "Source": 16,
}
DEFAULT_WIDTH = 18

# Columns whose content is short and reads better centred.
CENTRED = {
    "Risk Rating", "Status", "Percent Complete", "Obligation Level",
    "Material", "Reviewed", "Target Date", "Start Date", "Due Date",
    "Published", "Date Found", "Last Updated",
}


def format_data_sheet(ws, freeze_col: str = "C") -> None:
    """
    Apply the table treatment to a header-plus-rows sheet.

    freeze_col defaults to "C" so the first TWO columns stay pinned — on these
    sheets that is the ID plus the thing it names (Obligation / Action / Title).
    Freezing only column A left the ID visible while the text scrolled away, so
    on a 369-character-wide sheet you ended up looking at nothing but the
    evidence columns and could not tell which row you were on.
    """
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    if not any(headers):
        return

    for idx, name in enumerate(headers, start=1):
        letter = get_column_letter(idx)
        ws.column_dimensions[letter].width = WIDTHS.get(name, DEFAULT_WIDTH)
        cell = ws.cell(1, idx)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[1].height = 30

    for row in range(2, ws.max_row + 1):
        banded = (row % 2 == 0)
        for idx, name in enumerate(headers, start=1):
            cell = ws.cell(row, idx)
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = Alignment(
                vertical="top",
                horizontal="center" if name in CENTRED else "left",
                wrap_text=True,
            )
            if banded:
                cell.fill = BAND_FILL
        ws.row_dimensions[row].height = ROW_HEIGHT

    # Freeze the header and the ID column so context survives scrolling, and
    # give every column a filter for triage.
    ws.freeze_panes = f"{freeze_col}2"

    # Excel saves the SCROLL POSITION separately from the freeze, and restores it
    # on open. The Obligations sheet had been saved at topLeftCell "I1", so it
    # reopened parked on Evidence Required / Evidence Location and looked as
    # though the ID and obligation columns had vanished. Reset the view to the
    # top-left every time, or a stray scroll gets baked in permanently.
    view = ws.sheet_view
    view.topLeftCell = "A1"
    if view.pane is not None:
        view.pane.topLeftCell = f"{freeze_col}2"
    for sel in view.selection or []:
        if sel.pane == "bottomRight":
            sel.activeCell = sel.sqref = f"{freeze_col}2"

    ws.auto_filter.ref = (
        f"A1:{get_column_letter(ws.max_column)}{max(ws.max_row, 1)}"
    )
