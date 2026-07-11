# [Fable 5 SOP - Thought Process]

Standard Operating Procedure for analysing and modifying this codebase (or any
small, human-in-the-loop compliance tracker). Written by Fable 5 after the
July 2026 workflow overhaul; intended to be followed step-by-step by future
models or maintainers. Read alongside `memory.md` (system state) and
`CLAUDE.md` (behavioural rules).

---

## Phase 1 — How to analyse the codebase

1. **Map the custom surface first.** List project files excluding `.venv`,
   `__pycache__`, and binaries. Here that yields nine Python files, two
   guides, one config (`sources.json`), and one workbook. Everything else is
   a dependency or an artefact.
2. **Read the human-facing guide before any code** (`GUIDE.md`). It states
   the design intent — *automate discovery, keep judgement human, automate
   presentation* — and any change that violates that intent is wrong even if
   the code is clean.
3. **Read the shared-logic module next** (`audit_logic.py`), because every
   other script imports from it; then the canonical data (`tracker_data.py`);
   then each entry-point script in the order the user runs them (setup →
   weekly → dashboard → monthly).
4. **Read supporting artefacts by the cheapest route available.** When the
   venv could not run python-docx, the Word document was read by unzipping it
   and stripping XML tags with the stdlib. Never skip a document whose title
   overlaps the task — here the "Actionable Obligations" docx defined the
   entire target model.
5. **Record invariants immediately, not just structure.** The ones that bite:
   Intelligence rows are appended positionally so columns must never be
   inserted mid-sheet; the seen-hash ledger is saved only after a successful
   workbook save; the scraper must never touch human-owned cells (Reviewed,
   Notes) or the Obligations/Actions tabs.

## Phase 2 — The analytical framework for mapping an obligation to an action

1. **Locate the seam.** Obligations were already classified by *level*
   (Enduring / Periodic / Monitoring — i.e. when the work recurs), but
   nothing encoded *what kind of work* satisfies them. That missing
   dimension is exactly the obligation→action translation.
2. **Derive the taxonomy from the data, not from theory.** List the leading
   verbs of every real obligation and action in the register, then cluster
   them into archetypes that each have an observable completion state:
   - **Produce** (produce, publish, prepare, respond to, establish) → the
     deliverable exists and the evidence is filed.
   - **Approve** (agree, endorse, approve, sign off) → the approval is given
     and minuted.
   - **Assess** (review, assess, benchmark, gap analysis, plan for) → the
     assessment is complete and findings are reported.
   - **Engage** (cooperate, work with, coordinate, brief) → the engagement
     happened and is recorded.
   - **Monitor** (monitor, track, watch, embed) → the committee-cycle check
     happened and is recorded.
   Precedence runs in that order: a concrete deliverable always beats
   watching. Default to Assess when no verb matches — the first executable
   step of unclear work is always to scope it.
3. **Make derivation mechanical.** An executable action = archetype template
   + the obligation's own *Evidence Required* (so "done" is defined) + the
   same owner + the target date as due date + the Section 151 note attached
   automatically where the Part 9 financial gateway matches. Emit exactly one
   suggested action and let the human refine it — judgement stays human.
4. **Tie each obligation level to an action expectation** so coverage
   warnings say what is missing, not just that something is:
   Enduring → recurring Produce each cycle; Statutory → dated Produce +
   Approve before the deadline; Periodic → one dated action that delivers
   the evidence; Monitoring → a standing Monitor action per committee cycle.
5. **Enforce, don't just define.** A policy nothing checks is documentation.
   `action_coverage_warnings()` runs on every reseed
   (`populate_tracker.py`) and feeds the monthly report's "NO ACTION
   RECORDED" line.
6. **Push the model upstream.** The same trigger-word + archetype logic tags
   incoming intelligence (the Action Signal column), so the categorisation
   applies at intake, mid-cycle, and at reporting — one taxonomy, three
   touchpoints.

## Phase 3 — Implementation discipline

1. **Preserve every existing public function signature.** Three scripts
   import from `audit_logic`; add functions, never mutate contracts.
2. **Never insert spreadsheet columns mid-sheet.** Rows are appended
   positionally; new columns go last, with the header auto-added to existing
   workbooks on first run, and mirrored in `setup_tracker.py` for fresh
   builds.
3. **Every changed line must trace to the request.** Pre-existing defects
   found along the way (a broken venv, a stale COUNTIF range) are reported
   to the user, not silently fixed.
4. **Match the existing voice.** Comments and console output in this project
   are written for a non-programmer operator; new output follows that
   register ("review these first", not stack-trace jargon).

## Phase 4 — Verification protocol

1. **Never verify against live data.** Copy `AuditTracker.xlsx`,
   `seen_hashes.txt`, and `sources.json` to a scratch directory and run
   every entry point there (scripts use relative filenames, so cwd controls
   which copy they touch).
2. **Exercise every entry point, including one full live scrape.** Compile
   checks and unit-style fakes first (inject synthetic items into
   `update_workbook` to test classification and column handling), then the
   real network run.
3. **Inspect the artefacts, not the exit codes.** Open the generated Word
   report and read its paragraphs; open the workbook and read the cells the
   change should have written.
4. **Only touch the real environment for its normal operations** (venv
   rebuild, dashboard refresh), and back up before any destructive change to
   user data.

## Environment notes for whoever runs this next

- Windows 10; system Python 3.13. If the `.venv` came from another machine,
  rebuild it: delete `.venv`, then `python -m venv .venv` and
  `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- In Git Bash, POSIX-style `PYTHONPATH` gets mangled (`C:\c\Users\...`);
  pass Windows-style paths with `MSYS_NO_PATHCONV=1`, and set
  `PYTHONIOENCODING=utf-8` when printing sheet contents.
- The workbook must be closed in Excel before any script runs.
