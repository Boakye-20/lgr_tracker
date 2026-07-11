# memory.md — Persistent State Document
## NCC Audit Reform and LGR Tracker

This file captures the architectural decisions, codebase logic, and project
context that a person (or model) needs before touching anything. Read it with
CLAUDE.md (behavioural rules), GUIDE.md (operating manual), and FABLE5-SOP.md
(the step-by-step method for analysing and modifying this codebase).

Last refreshed: 2026-07-09.

---

## 1. What the system is

A local-file compliance tracker for Nottingham City Council (NCC) covering two
parallel workstreams:

1. **Local Audit and Improvement** — external audit obligations, Audit
   Committee programme, internal audit, annual governance, statutory
   intervention recovery (Ministerial Envoys since 24 March 2026, CSIP).
2. **Local Government Reorganisation (LGR)** — transition to new unitary
   authorities (shadow elections ~May 2027, Vesting Day ~1 April 2028).

Everything lives in one folder: `AuditTracker.xlsx` (four tabs: Dashboard,
Intelligence, Obligations, Actions) plus small Python scripts. **Deliberately
no SharePoint / Power Automate / Power Apps** — the previous version died of
that complexity. Design philosophy (GUIDE.md §11): *automate discovery, keep
judgement human, automate presentation.*

## 2. The scripts and their contract

| Script | Cadence | Reads | Writes |
| --- | --- | --- | --- |
| `setup_tracker.py` | once | tracker_data.py | creates AuditTracker.xlsx |
| `update_intelligence.py` | weekly (`run_weekly_update.bat`) | sources.json, seen_hashes.txt, 9 web sources | Intelligence tab + seen_hashes.txt only |
| `populate_tracker.py` | quarterly / on reseed | tracker_data.py | Obligations + Actions tabs (full replace), prints validation |
| `build_dashboard.py` | before meetings (`run_build_dashboard.bat`) | all tabs | deletes + rebuilds Dashboard tab |
| `build_report.py` | monthly (`run_monthly_report.bat`) | Obligations + Actions | new Word file `NCC_Obligations_Report_YYYY-MM-DD.docx` (never touches workbook) |
| `audit_logic.py` | imported | — | shared scoring/theming + the policy layer (owners, levels, triggers, action translation, S151 gateway, validation) |
| `tracker_data.py` | imported | audit_logic | canonical OB-A1..A12 + OB-L1..L7 obligations and A-001..A-009 actions — single source of truth |
| `scraper_extensions.py` | imported | web | NAO / CIPFA / Parliament Committees / EMCCA / NCC ModernGov scrapers |

Invariants:
- The scraper **never** touches Obligations/Actions and never overwrites human
  Reviewed/Notes cells.
- `sources.json` is the only tuning surface; humans never edit Python to tune.
- Workbook must be **closed in Excel** before any script runs (PermissionError
  is caught and explained).
- `seen_hashes.txt` is the dedup ledger (md5 of `url|title`). Non-material
  ("No") items are recorded there silently and never shown. Deleting the
  workbook without deleting seen_hashes ⇒ scraper adds nothing.
- Ledger is saved **only after** a successful workbook save.

## 3. Intelligence pipeline (weekly run)

`update_intelligence.py` main():
fetch (GOV.UK search terms + MHCLG org feed → watched GOV.UK collection pages
→ Parliament Bills → PSAA scrape → NAO → CIPFA → Parliament Committees →
EMCCA → NCC ModernGov) → `update_workbook()`:

1. `is_excluded()` hard pre-filter (devolved nations, other counties' LGR,
   `exclude_keywords` e.g. HMRC).
2. Hash dedup against ledger (also seeded from any Hash column values).
3. `classify_materiality()` — four keyword groups (Local / Intervention /
   Audit / Transition); ≥2 groups = **Yes**, 1 = **Unclear**, 0 = **No**
   (suppressed, ledger-only).
4. `assign_themes()` — five fixed themes.
5. Append row; "Action Signal" column flags items whose text carries
   obligation-trigger language ("must/required/shall...") as
   **Possible obligation** so the reviewer knows which Yes/Unclear items
   likely need an Obligations row.

NCC committee items get "Nottingham City Council committee paper" appended to
their score text (`_ext_to_item`) or the local-source scorer would drop them.

Intelligence columns (order matters — rows are appended positionally):
`Date Found, Title, Source, Category, Published, Material, Matched, Theme,
URL, Reviewed, Notes, Hash(hidden), Action Signal`. Never insert columns
mid-sheet; only append at the end, and mirror the change in both
`setup_tracker.build_intelligence()` and `update_intelligence.update_workbook()`.

## 4. The obligation model (the "judgement" policy, encoded in audit_logic.py)

- **Owners** are fixed to the Part 13 Key Contacts list (`OWNERS`,
  `KNOWN_OWNER_TOKENS`, `KNOWN_BODY_TOKENS`). Validation rejects unknown names.
- **Obligation levels** (Guide Part 1): Enduring (statute; never expires),
  Periodic (dated deliverable; closes on evidence), Monitoring (watch;
  never closes), plus Statutory used for hard-deadline direction items
  (e.g. OB-A2 CSIP, deadline 2026-06-24).
- **Obligation triggers** (Parts 2/10): text without "must / required /
  shall / directions require" is monitoring or context, not an obligation.
- **Action translation policy**: every obligation is translated into
  executable compliance actions via a verb taxonomy —
  Produce / Approve / Assess / Engage / Monitor. `classify_action_type()`
  picks the archetype; `derive_compliance_action()` builds a concrete,
  owned, dated action stub from an obligation row;
  `action_coverage_warnings()` enforces the Part 5 maturity rule that every
  live obligation carries at least one action row. `LEVEL_ACTION_POLICY`
  states what kind of action each level expects.
- **S151 financial gateway** (Part 9): any LGR-themed action containing
  procure/contract/vendor/capital/IT-migration keywords automatically gets
  the Section 151 sign-off note (spending controls during intervention).
- **Row validation** (Parts 5/10): `validate_obligation()` — owner known,
  target date unless Ongoing, specific source trigger, evidence described,
  Complete ⇒ evidence located and not a homepage, valid dropdown values,
  obligation text ≥5 words. A clean register still flags OB-L6 (its trigger,
  the Statutory Boundary Order, is pending — that flag is expected).

## 5. Known data/context facts (June–July 2026)

- Commissioners replaced by **Ministerial Envoys** on 24 March 2026 directions.
- **English Devolution and Community Empowerment Act 2026** has Royal Assent
  (29 April 2026, c.23); it creates the **Local Audit Office** (Bill Butler
  preferred Chair candidate). PSAA contract runs to 2027/28, then abolition.
- MHCLG LGR consultation for Nottingham(shire) live; final **Statutory
  Boundary Order** expected ~summer 2026 — its publication is the trigger
  that makes OB-L6 live and cascades new transition obligations.
- "Actionable Obligations and File Cleanup.docx" is a strategic assessment
  containing derived actions per obligation and an Intelligence cleanup list
  (8 noise items to purge, 4 Unclear items to elevate to material). It is a
  reference document, not code.

## 6. Environment gotchas

- Windows 10, system Python is **3.13**. The `.venv` was rebuilt against it
  on 2026-07-11 (the original came from another machine on Python 3.12 and
  did not run). If the folder ever moves to a new machine again, rebuild:
  delete `.venv`, `python -m venv .venv`,
  `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- Not a git repository. Backup rule: copy the folder (xlsx + sources.json +
  seen_hashes.txt are the irreplaceable three) weekly.
- openpyxl formulas in the setup-time Dashboard use `data_only=False` reads;
  `build_dashboard.py` replaces that sheet entirely with computed values.
- Dropdowns are re-applied by populate_tracker; column positions are located
  by header name, never hard-coded (except historical ranges G2:G1000 on
  Actions status).
