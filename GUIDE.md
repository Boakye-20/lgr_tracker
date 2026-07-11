# NCC Audit Reform and LGR Tracker — Complete Guide

This guide assumes no prior knowledge. Follow it top to bottom once to set
everything up, then use the short weekly and monthly routines near the end.

---

## 1. What this system is, in one paragraph

It watches the government for changes to local audit, the Local Audit Office,
devolution, and Local Government Reorganisation. It pulls those changes into a
single spreadsheet from nine sources, scores each one for how relevant it is
to Nottingham City Council, and lets you turn the relevant ones into tracked
obligations with owners and evidence. Before any committee meeting you refresh
the dashboard to get a live picture of what is overdue and where the evidence
gaps are. Once a month it produces a Word report you can hand to the Audit
Committee or to a government inspector.

There is no SharePoint automation, no Power Automate, and no Power Apps. The
whole thing is one spreadsheet and four small scripts. That is deliberate.
Those tools were the source of every problem in the previous version.

---

## 2. The pieces and what each one does

| File | What it is | How often you touch it |
| --- | --- | --- |
| AuditTracker.xlsx | The single spreadsheet that holds everything | Every week, by hand |
| setup_tracker.py | Builds the spreadsheet the first time | Once, ever |
| update_intelligence.py | The scraper. Refreshes the feed of new items | Weekly (automatic) |
| seen_hashes.txt | The scraper's memory of every item it has already processed | Never (created automatically) |
| build_dashboard.py | Rewrites the Dashboard tab with live metrics | Before any meeting |
| build_report.py | Makes the Word report from your obligations | Monthly |
| sources.json | The settings file. Search terms, keywords, scoring, committee pages | Only when tuning |
| audit_logic.py | Shared scoring/theming rules **and** the six-part policy section: owners, obligation levels, obligation triggers, obligation-to-action translation, S151 gateway, validation | Never, unless changing logic |
| tracker_data.py | The canonical list of obligations and actions (single source of truth) | When adding a permanent obligation |
| populate_tracker.py | Re-seeds Obligations/Actions from tracker_data.py and runs the role/maturity validation check | Quarterly, or when re-seeding |
| scraper_extensions.py | Web scrapers for NAO, CIPFA, Committees, EMCCA, and NCC committee pages | Never |
| requirements.txt | The list of software libraries needed | Never |
| run_weekly_update.bat | Double-click shortcut for the weekly scrape | Weekly |
| run_build_dashboard.bat | Double-click shortcut to refresh the dashboard | Before any meeting |
| run_monthly_report.bat | Double-click shortcut for the monthly report | Monthly |

The spreadsheet has four tabs:

- **Dashboard** — headline tiles, charts, and an "Attention needed" list. Run
  `run_build_dashboard.bat` to refresh it before showing anyone.
- **Intelligence** — the feed of new legislation and guidance. The scraper fills
  this. You review it.
- **Obligations** — what NCC must do. You maintain this by hand. This is the
  important one.
- **Actions** — the steps taken against each obligation. You maintain this.

---

## 3. Sources scraped each week

The weekly update pulls from nine places automatically:

| Source | What it gets |
| --- | --- |
| GOV.UK Search API | New publications matching your search terms |
| GOV.UK department feed | Everything MHCLG publishes |
| GOV.UK watched collections | Full contents of specific tracked pages (LGR, Nottingham intervention, audit reform) |
| Parliament Bills API | Bills matching your search terms |
| PSAA website | Latest news from psaa.co.uk |
| National Audit Office | Reports and posts |
| CIPFA | Publications and guidance |
| Parliament Committees | Public Accounts Committee and HCLG Committee publications |
| EMCCA | East Midlands Combined County Authority news |
| NCC committee pages | Audit Committee and Improvement Committee meetings (ModernGov), from 2026 onward |

Everything is controlled through `sources.json` — you never edit the Python.

---

## 4. One-time setup

You only do this section once.

### 4.1 Install Python

If Python is not already on the laptop, install it from python.org. During
install, tick the box that says "Add Python to PATH". You need version 3.10 or
newer.

To check whether it is already there, open Command Prompt and type:

```
python --version
```

If you see a version number of 3.10 or higher, you are fine.

### 4.2 Put the files in a folder

Create a folder somewhere sensible, for example:

```
C:\Users\pkwart\NCC Audit Tracker\
```

Copy all the files from this package into it.

### 4.3 Create the virtual environment and install packages

A virtual environment is just a private box of libraries for this project so it
does not interfere with anything else. Open Command Prompt, then:

```
cd "C:\Users\pkwart\NCC Audit Tracker"
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Note: use `python.exe -m pip` rather than `pip.exe` directly, as some managed
laptops block newly created executables.

### 4.4 Build the spreadsheet

```
.venv\Scripts\python.exe setup_tracker.py
```

This creates AuditTracker.xlsx with all four tabs, the dashboard, and the full
obligation set already filled in for you — OB-A1 to OB-A11 (audit and
improvement) and OB-L1 to OB-L6 (LGR), each with a named owner, theme, risk,
target date, and obligation level, plus the OB-A11 sub-actions in the Actions
tab. Open it and have a look.

### 4.5 Check the obligations and confirm ownership

The obligations come pre-populated with owners from the Key Contacts list
(Operating Guide Part 13), so you are not starting from blanks. Open the
Obligations tab and confirm with John that the owners and target dates are
right for how the work is actually split. To check the register is complete and
internally consistent at any time, run:

```
.venv\Scripts\python.exe populate_tracker.py
```

It re-seeds the Obligations and Actions tabs from `tracker_data.py` and prints a
validation report flagging any blank/unrecognised owners, missing dates, or
missing evidence. A clean register flags only OB-L6, which is meant to be
flagged until the Statutory Boundary Order is published.

That is setup finished.

---

## 5. The weekly routine (about fifteen minutes)

### 5.1 Run the scraper

Make sure AuditTracker.xlsx is **closed**, then double-click
`run_weekly_update.bat`. A black window appears, runs for a minute or two, and
tells you how many new items it added from each source.

### 5.2 Review the new items

Before opening the workbook, read the last block of the black window: it now
ends with a per-source summary of what was added and a "review these first"
list of items whose text contains obligation language (must / required /
shall).

Open AuditTracker.xlsx, go to the Intelligence tab. Use the filter on the
Material column to show only items marked **Yes**. These are the ones the system
thinks NCC should care about. The **Action Signal** column (last column) marks
the items that talk like obligations — e.g. "Possible obligation (Produce)" —
and names the action type they would translate into (see section 8). Start
with those. For each one:

- If it genuinely creates something NCC must do, go to the Obligations tab and
  add a row for it (see section 7).
- Either way, set the Reviewed column to **Yes** so it drops off your review
  list next week.
- Add a short note in the Notes column if useful, for example "raised as OB-006"
  or "no action needed, monitoring only".

Items marked Unclear are worth a glance — they matched on one theme but not
enough to be confident, so a quick human eye sorts the useful from the noise.

You will not see any items marked **No**. Non-material items are no longer
written to the Intelligence sheet at all — the scraper records them silently in
`seen_hashes.txt` so they are never shown and never come back. This keeps the
sheet to the things that actually warrant a look (Yes and Unclear only).

That is the whole weekly job.

---

## 6. Refreshing the dashboard (before any meeting)

Close AuditTracker.xlsx, then double-click `run_build_dashboard.bat`. It
rewrites the Dashboard tab with:

- Five colour-coded headline tiles (total obligations, overdue, due in 30 days,
  complete, evidence gaps) — red means action needed, green means all clear
- Three charts: obligations by status, by theme, and by risk
- Action progress summary (average completion, overdue count, evidence coverage)
- Intelligence summary (total items, material items, awaiting review)
- An "Attention needed" list naming the specific obligations that are late or
  due soon, with owner and date

This is the tab to open when John or an inspector asks for the current picture.

---

## 7. The monthly routine (five minutes)

Once a month, before the Audit Committee cycle, double-click
`run_monthly_report.bat`. It produces a Word file named with today's date. It
opens with an executive summary and an **Attention needed** list (overdue
obligations, items due within 30 days, evidence gaps, and live obligations
with no recorded action), then lists every obligation grouped by theme with
its source, owner, level, status, evidence, and its actions — each action
showing its due date and flagged if overdue or missing an evidence link.
Open it, read it through, and send or print it.

The dashboard gives a quick visual summary. The Word report is the formal
document that demonstrates NCC's grip on its obligations in detail. You need
both: the dashboard for the meeting itself, the report for the papers.

---

## 8. How to add an obligation

On the Obligations tab, add a new row:

- **Obligation ID** — next number in sequence, for example OB-006.
- **Obligation** — one or two sentences on what NCC must do.
- **Source / Trigger** — the legislation or guidance that created it. Copy the
  title from the Intelligence tab.
- **Theme** — pick one of the five themes used elsewhere.
- **Owner** — the named person responsible.
- **Risk Rating** — High, Medium, or Low (dropdown).
- **Target Date** — when it must be done.
- **Status** — Not started, In progress, Complete, Blocked, or Ongoing (dropdown).
- **Evidence Required** — what proof will show it was done.
- **Evidence Location** — where that proof lives, once it exists.
- **Sign Off By** — who confirms completion.

To record work done against an obligation, add rows to the Actions tab and put
the obligation's ID in the Parent Obligation ID column. Fill in the Evidence
Link column when the work is done — that is what removes the item from the
evidence gaps count on the dashboard.

### How an obligation becomes actions — the categorisation policy

An obligation is only under control once it has been translated into at least
one specific, executable action: a verb, a named owner, a date, and the
evidence that closes it. The system encodes this as five action types
(`audit_logic.py`, Policy 4), chosen by the leading verbs in the obligation:

| Action type | Trigger verbs (examples) | What "done" looks like |
| --- | --- | --- |
| Produce | produce, publish, prepare, respond to, establish | The deliverable exists and the evidence is filed |
| Approve | agree, endorse, approve, sign off | The approval is given and minuted |
| Assess | review, assess, benchmark, gap analysis, plan for | The assessment is complete and findings reported |
| Engage | cooperate, work with, coordinate, brief | The engagement happened and is recorded |
| Monitor | monitor, track, watch, embed | The committee-cycle check happened and is recorded |

Each obligation level expects a particular shape of action:

- **Enduring** — a recurring Produce action each reporting cycle; the duty
  itself never closes.
- **Statutory** — a dated Produce action plus an Approve action, both done
  before the statutory deadline.
- **Periodic** — at least one dated action that delivers the evidence, after
  which the obligation closes.
- **Monitoring** — a standing Monitor action reviewed each committee cycle;
  never closes, but each review must be recorded.

You do not have to work this out by hand. Running `populate_tracker.py` checks
that every live obligation has at least one action row and, for any that do
not, prints a ready-made suggested action (correct type, owner, due date, and
the S151 note where the financial gateway applies) that you can paste into the
Actions tab and refine. The same check drives the "NO ACTION RECORDED" line in
the monthly report, and the weekly scraper uses the same verb taxonomy to mark
new intelligence with the action type it would translate into.

---

## 9. Tuning the system

Everything adjustable lives in **sources.json**. You never edit the Python.

- To watch for a new topic, add a phrase to `govuk_search_terms`.
- To follow a new collection page, add its path to `watched_govuk_paths`.
- To change what counts as relevant, edit the keyword lists under `materiality_rules`.
  Scoring is simple: each item is checked against four keyword groups (Local,
  Intervention, Audit, Transition). Match **two or more** groups and it is
  flagged **Yes**; match **exactly one** and it is **Unclear**; match **none**
  and it is **No** (recorded silently, not shown). So to make the system flag
  more items as Yes, broaden the keyword lists; to flag fewer, tighten them.
- To stop a known category of false matches, add a phrase to `exclude_keywords`
  under `exclusion_rules`. Anything whose title contains one of these is dropped
  before scoring — this is how HMRC tax-tribunal cases (which match
  "commissioner" in its legal sense) are kept out of the feed.
- To disable a source (e.g. CIPFA), set `"enabled": false` in its section.
- To watch another NCC committee, add a line to the `ncc_committees.pages` list
  with the committee name and its "Browse meetings" URL
  (`ieListMeetings.aspx?CommitteeId=NNN`). The `since_date` there controls how
  far back meetings are pulled (set to 2026-01-01 so the old back-catalogue is
  skipped).

After any change, just run the weekly update again.

### Re-seeding and validating the obligations

The obligations and actions themselves live in `tracker_data.py`. To add an
obligation that should survive a re-seed or a fresh rebuild, add it there and
run `python populate_tracker.py`. That command also runs the role and maturity
validation (recognised owners, dates, evidence) and prints anything that needs
tidying. The owner names it accepts come from the Key Contacts list — use them
exactly.

---

## 10. If something goes wrong

| Problem | Fix |
| --- | --- |
| "Cannot save AuditTracker.xlsx" | Close the file in Excel and run again |
| setup_tracker.py says file already exists | Normal — it is already set up. Do not run again. |
| The scraper added zero items | Usually normal — nothing new since last run. If it happens every week for a month, check internet access to gov.uk and parliament.uk. |
| A watched path reports a 404 in the window | That page moved on GOV.UK. Remove it from `watched_govuk_paths` in sources.json. |
| A source (NAO, CIPFA etc.) shows 0 items | Normal — keyword filter found nothing new. Not an error. |
| You want to start completely fresh | Delete AuditTracker.xlsx **and seen_hashes.txt**, then run setup_tracker.py again. (If you keep seen_hashes.txt, the scraper treats everything as already seen and adds nothing.) You will lose all obligations, so only do this deliberately. |
| The scraper keeps showing the same noise item | Add a phrase from its title to `exclude_keywords` in sources.json (see section 9). To remove a copy already in the sheet, delete that row by hand. |

---

## 11. Why it is built this way

The previous version tried to push data automatically into SharePoint lists
through Power Automate. That chain had too many fragile links: triggers that
fired at the wrong time, file references that broke, and column name mismatches
that failed silently. It cost weeks and never ran reliably.

This version automates only the part that should be automated, which is finding
new information. The judgement about what NCC must do, who owns it, and what
counts as evidence stays with a person, because that judgement is exactly what
makes the obligations register credible to an inspector. The dashboard and
reporting are automated at the end because producing a consistent, well-formatted
picture of the current state is repetitive work that Python does more reliably
than Excel formulas.

Automate discovery. Keep judgement human. Automate the presentation at the end.
That is the whole design philosophy.
