# NCC Audit Reform and LGR Tracker

Watches the government for changes to local audit, the Local Audit Office,
devolution and Local Government Reorganisation; scores each change for how much
it matters to Nottingham City Council; and turns the ones that matter into
tracked obligations with owners, dates and evidence.

Everything lives in one spreadsheet, `AuditTracker.xlsx`, with a handful of
Python scripts around it. No SharePoint, no Power Automate, no Power Apps. That
is deliberate: those tools were the source of every problem in the previous
version.

**Full instructions: [GUIDE.md](GUIDE.md).** It assumes no prior knowledge and
covers setup, the routines, and troubleshooting. This README is just the map.

## The design

Automate discovery. Keep judgement human. Automate the presentation at the end.

The scraper finds new information, because that is repetitive. What NCC must do,
who owns it and what counts as evidence stays with a person, because that
judgement is exactly what makes the register credible to an inspector. The
dashboard and the monthly report are automated again at the end, because
formatting a consistent picture is work Python does more reliably than Excel.

## The routines

| When | What you do | How long |
| --- | --- | --- |
| Once, ever | Install Python, create the virtual environment, run `setup_tracker.py` | - |
| Weekly | Double-click `run_weekly_update.bat`, then review new items in the Intelligence tab | ~15 min |
| Before a meeting | Double-click `run_build_dashboard.bat` | ~1 min |
| Monthly | Double-click `run_monthly_report.bat`, read the Word report, send it | ~5 min |

Close `AuditTracker.xlsx` before running any of them.

## The spreadsheet

| Tab | What it holds | Who maintains it |
| --- | --- | --- |
| Dashboard | Headline tiles, charts, "Attention needed" list | Generated |
| Intelligence | Feed of new legislation and guidance | Scraper fills, you review |
| Obligations | What NCC must do (**the important one**) | You, by hand |
| Actions | Steps taken against each obligation | You, by hand |

## The files

| File | What it is | How often you touch it |
| --- | --- | --- |
| `AuditTracker.xlsx` | The spreadsheet that holds everything | Weekly |
| `sources.json` | All settings: search terms, keywords, scoring, committee pages | When tuning |
| `setup_tracker.py` | Builds the spreadsheet the first time | Once, ever |
| `update_intelligence.py` | The scraper | Weekly, via the .bat |
| `build_dashboard.py` | Rewrites the Dashboard tab | Before meetings, via the .bat |
| `build_report.py` | Makes the Word report | Monthly, via the .bat |
| `tracker_data.py` | Canonical list of obligations and actions | When adding a permanent obligation |
| `populate_tracker.py` | Re-seeds from `tracker_data.py` and validates | Quarterly |
| `audit_logic.py` | Scoring, theming, and the six-part obligation policy | Never, unless changing logic |
| `scraper_extensions.py` | Scrapers for NAO, CIPFA, Committees, EMCCA, NCC | Never |
| `sheet_format.py` | Spreadsheet formatting helpers | Never |
| `seen_hashes.txt` | The scraper's memory of what it has already seen | Never (automatic) |

## Sources scraped

Nine, each week: the GOV.UK Search API, the MHCLG department feed, watched GOV.UK
collection pages, the Parliament Bills API, PSAA, the National Audit Office,
CIPFA, Parliament Committees (PAC and HCLG), EMCCA, and NCC's own Audit and
Improvement Committee pages.

All of it is controlled through `sources.json`, so you never edit the Python.

## How relevance is scored

Each item is checked against four keyword groups: Local, Intervention, Audit,
Transition.

- Two or more groups match → **Yes** (material; review it)
- Exactly one matches → **Unclear** (worth a glance)
- None match → **No** (recorded silently in `seen_hashes.txt`, never shown)

To flag more items, broaden the keyword lists in `sources.json`. To flag fewer,
tighten them. To kill a recurring false match, add a phrase to `exclude_keywords`.

## Setup in short

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe setup_tracker.py
```

Use `python.exe -m pip` rather than `pip.exe`, because some managed laptops block newly
created executables. Python 3.10 or newer.

See [GUIDE.md](GUIDE.md) section 4 for the full walkthrough.
