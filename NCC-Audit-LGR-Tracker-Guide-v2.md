# NCC Audit Reform and LGR Obligations Tracker — Complete Operating Guide (v2)

*For the Audit and Risk Trainee responsible for maintaining AuditTracker.xlsx*

---

## Overview

This guide explains exactly where to find every piece of information needed to populate and maintain the NCC Audit Reform and LGR Obligations Tracker, what to look for when reviewing sources, how to judge whether something is a real obligation, and how to keep the tracker at its most mature and useful state over time. It covers both the Local Audit side and the Local Government Reorganisation side, as these are the two workstreams your manager has asked you to track.

The tracker already has the right structure — Intelligence, Obligations, Actions, Dashboard — and the full Python toolkit (update_intelligence.py, build_dashboard.py, build_report.py, audit_logic.py, sources.json). Two newer files complete it: **tracker_data.py** (the single source of truth for the seeded obligations and actions) and **populate_tracker.py** (refreshes the Obligations and Actions tabs from that file and runs an automated role/maturity check). What this guide does is give you the operating knowledge to fill it with the right content, tune it correctly, and keep it genuinely useful to John, to the Audit Committee, and to any inspector who looks at it.

> **What changed in this build (read this first).** Four things are new since the original guide:
> 1. **The Obligations and Actions tabs are now pre-populated** with the full obligation set from Part 7 (OB-A1–A11 plus OB-L1–L6 LGR, with named owners, themes, risk, target dates, and the OB-A11 sub-actions). You no longer start from five blank-owner seeds.
> 2. **An "Obligation Level" column** (Enduring / Periodic / Monitoring — see Part 1) has been added to the Obligations tab as a dropdown.
> 3. **NCC committee pages are now scraped automatically.** The Audit Committee and Improvement Committee meeting lists feed straight into the Intelligence tab — you no longer have to check them by hand for new meetings (see Sources 2 and 4).
> 4. **Roles and quality are now enforced in code.** `audit_logic.py` knows the Part 13 owners, classifies obligation levels, detects the Section 151 spending gateway (Part 9), and validates every obligation against the Part 5 maturity rules. Running `populate_tracker.py` prints a list of anything that falls short. See the new Part 16.

---

## Part 1: Understanding What You Are Tracking

### Two workstreams, one tracker

Your tracker covers two parallel reform tracks.

**Local Audit and Improvement** covers the council's external audit obligations, the Audit Committee's work programme, internal audit, annual governance, and the improvement duties arising from the statutory intervention. This is about proving the council has financial controls, proper governance, and is recovering as required.

**Local Government Reorganisation (LGR)** covers the council's transition obligations as Nottingham and Nottinghamshire move toward new unitary authorities. This is about safe and legal transition planning, working with other councils, cooperating with Ministerial Envoys, and eventually delivering a day-one-ready new authority.

These two tracks often overlap. For example, the council's obligation to develop an internal audit plan covering LGR transition risk sits in both workstreams at once.

### Three levels of obligation

Every obligation in your tracker sits at one of three levels. Understanding this will stop you from writing obligations that are either too vague to be useful or too narrow to last more than a fortnight.

**Enduring duties** — these come from legislation, statutory directions, or standing best value requirements. They do not change unless Parliament or the Secretary of State acts. Examples: the duty to have internal audit, publish accounts, and meet the Best Value duty under the Local Government Act 1999.

**Periodic obligations** — these arise from specific committee decisions, management responses, or CSIP delivery milestones. They last until the action is done and evidenced. Examples: respond to external audit findings by a given committee date; prepare a CSIP within three months of the 24 March 2026 directions.

**Monitoring obligations** — these are things the council must keep watching and responding to as they develop. Examples: track the Local Audit Office transition; monitor LGR timetable milestones. These do not close but need regular review and updating.

---

## Part 2: Where to Find Everything — Source by Source

### Source 1: GOV.UK Statutory Directions (most important for legal triggers)

**What it is:** The formal legal requirement placed on Nottingham City Council by the Secretary of State. Everything else flows from this.

**Exactly where to go:**
- Current directions (24 March 2026): https://www.gov.uk/government/publications/nottingham-city-council-directions-made-under-the-local-government-act-1999-24-march-2026
- Explanatory memorandum (24 March 2026): https://www.gov.uk/government/publications/nottingham-city-council-explanatory-memorandum-24-march-2026
- Full statutory intervention collection: https://www.gov.uk/government/collections/statutory-intervention-nottingham-city-council-minded-to-decision
- Ministerial Envoy appointment letter: https://www.gov.uk/government/publications/nottingham-city-council-ministerial-envoy-appointment-letter
- Letter to Chief Executive (24 March 2026): https://www.gov.uk/government/publications/nottingham-city-council-letter-to-chief-executive-24-march-2026

**What to look for:** Read for sentences containing "must", "required", "shall", "directions require", or "the Authority is required to". These are your obligation triggers. The 24 March 2026 directions specifically require the council to: establish the Continuous Improvement Committee; prepare and agree the CSIP within three months; embed improvements in financial stability, scrutiny, risk, internal audit, and service delivery; continue LGR work with other Nottinghamshire councils; and cooperate with Ministerial Envoys.

**How the scraper watches this:** Your sources.json already watches the statutory intervention collection via `watched_govuk_paths`:
```
/government/collections/statutory-intervention-nottingham-city-council-minded-to-decision
```
New publications in that collection will appear in the Intelligence tab automatically. However, read the full direction documents yourself — the scraper picks up the title and URL but cannot extract the "must" sentences for you.

**How often to check manually:** Check whenever there is a news item about Nottingham and government intervention, or every quarter. Directions do not change frequently but when they do it is significant.

**Obligation level:** Creates enduring duties and periodic obligations.

---

### Source 2: Improvement Committee Papers (best for council response to directions)

**What it is:** The Improvement Committee is the new statutory committee established under the 24 March 2026 directions. Its papers translate the directions into council commitments and show the governance structure for oversight.

**Exactly where to go:**
- 4 June 2026 public reports pack: https://committee.nottinghamcity.gov.uk/documents/g11742/Public%20reports%20pack%2004th-Jun-2026%2014.00%20Improvement%20Committee.pdf
- Committee calendar (for future meetings): https://committee.nottinghamcity.gov.uk/mgCalendarMonthView.aspx?bcr=1

**What to look for:**
- The "Recommendations" box in each report — this is what the committee is being asked to approve.
- The "Background" and "Legal" sections — these cite the specific directions and translate them into what the council says it will do.
- Named officers (Senior Accountable Officers and Responsible Delivery Leads) — these become owners in your Obligations tab.
- The list of appendices — the CSIP and Detailed Delivery Plan are both appendices here.
- Any committee recommendations made at the meeting — these become new obligations or actions.

**How the scraper watches this:** The Improvement Committee's meeting list is now scraped automatically via the `ncc_committees` block in sources.json (committee ID 1175). New meetings appear in the Intelligence tab flagged Material = Yes, with the meeting date. The scraper picks up that a meeting exists and links to its document list — it does not read the PDFs inside, so you still open the reports pack yourself to find the "must" sentences, recommendations, and appendices.

**How often to check:** The committee meets approximately twice a year. The scraper will surface each new meeting for you; still read the papers before and after each meeting. Next meeting expected November 2026 (already showing in the feed).

**Obligation level:** Creates periodic obligations and evidence of delivery.

---

### Source 3: The CSIP and Detailed Delivery Plan (best for themes, owners, and milestones)

**What it is:** The Continuous Service Improvement Plan is the council's master improvement document, structured around seven priority service improvement areas and nine cross-cutting programmes. The Detailed Delivery Plan (Appendix 2) contains key activities, named officers, and delivery dates.

**Exactly where to go:**
- CSIP (Appendix 1): Attached to the 4 June 2026 Improvement Committee report.
- Detailed Delivery Plan (Appendix 2): Also attached to that report. Ask John for the current working version.

**What to look for:**
- The nine cross-cutting improvement programmes — these map directly to tracker themes, especially: Financial Sustainability and Management; Risk Management and Internal Audit; Governance, Scrutiny and Decision Making; and Local Government Reorganisation.
- The objective for Risk Management and Internal Audit explicitly says internal audit must align with Local Audit Office standards and guidance, and there must be synergy with external assurance. This is a direct obligation for your tracker.
- Named Senior Accountable Officers (SAOs) — for Finance it is S Fair; for Internal Audit it is L Dowdican; for LGR it sits under the Chief Executive and Director of Policy.
- Outcome measures and targets — useful for your Evidence Required field because you can say "improvement in outcome X by date Y".
- The governance cycle (monthly CSIB, six-monthly Improvement Committee) — tie your review dates to these.

**How often to check:** The CSIP is a live document expected to be refreshed annually. Check after each Improvement Committee meeting and whenever a new version is published.

**Obligation level:** Creates periodic obligations with named owners and measurable evidence.

---

### Source 4: Audit Committee Minutes, Recommendation Tracker, and Work Programme (best for audit-specific obligations and evidence)

**What it is:** The Audit Committee is the council's primary assurance committee. Its minutes contain resolutions that often create direct follow-up obligations. The Recommendation Tracker logs what the committee has asked for and whether it has been done. The Work Programme shows when items will return to committee.

**Exactly where to go:**
- Committee papers and minutes: https://committee.nottinghamcity.gov.uk/mgCommitteeDetails.aspx?ID=145
- Minutes of 20 February 2026: file attached as Minutes.pdf
- Recommendation Tracker: file attached as Recommendation-Tracker.pdf
- Work Programme 2026/27: file attached as Draft-Work-Programme-2627.pdf

**What to look for in the Minutes:**
- The "Resolved" sections — every resolution is a committee instruction that should exist somewhere in the tracker.
- Examples from the 20 February 2026 minutes: recommendation to clarify Table 5 in the Treasury Management Report; briefing on UN PRI and UNGP legal advice; recommendations to approve strategies at City Council on 2 March 2026.

**What to look for in the Recommendation Tracker:**
- Rows where Progress Status is "Pending" — these are live obligations.
- The Key Contacts column — these are your owners.
- The due date in the status field — this becomes your Target Date.

**What to look for in the Work Programme:**
- Every item has a Committee Objective column and a Director/Author column. Use these to set theme, owner, and review date.
- Items due in June and July 2026 include: IT Assurance Report, Information Governance Assurance Report, Exemption from Contract Procedure Rules Annual Report, Capital Programme Assurance, Audit Committee Annual Report, Terms of Reference, and Draft Statement of Accounts.

**How the scraper watches this:** The Audit Committee meeting list is now scraped automatically via the `ncc_committees` block in sources.json (committee ID 145). Each new meeting appears in the Intelligence tab flagged Material = Yes, with its date. As with the Improvement Committee, the scraper finds the meeting and links to its papers but does not read inside the PDFs — open the agenda, minutes, and Recommendation Tracker yourself to extract the "Resolved" items and pending recommendations.

**How often to check:** After every Audit Committee meeting. The scraper now flags each meeting for you; still read the minutes, Recommendation Tracker, and Work Programme. Meetings are roughly every two to three months.

**Obligation level:** Creates periodic obligations, live follow-up actions, and evidence of completion.

---

### Source 5: Statement of Accounts and Reports Page (best for published evidence)

**What it is:** The council's public page for all published accounts, audit opinions, annual governance statements, and external auditor reports. This is where you close obligations by linking to the final published proof.

**Exactly where to go:** https://www.nottinghamcity.gov.uk/your-council/about-the-council/statement-of-accounts-and-reports/

**What to look for:**
- Published Statement of Accounts with audit opinion — closes the accounts obligation.
- Annual Governance Statement — closes the AGS obligation.
- External Auditor's Annual Report and Value for Money report — these trigger management response obligations.
- Any public interest reports or statutory notices — high-priority triggers for new obligations.

**Evidence URL rule:** When completing an obligation in the Obligations tab, the Evidence Location for accounts and governance documents should link directly to a specific document on this page, not just the homepage. A link like `https://www.nottinghamcity.gov.uk/your-council/about-the-council/statement-of-accounts-and-reports/` alone is too vague — scroll to the specific year and document and copy that URL.

**How often to check:** Weekly during accounts season (May to September). Monthly otherwise.

**Obligation level:** Provides evidence to close periodic obligations.

---

### Source 6: LGR-Specific Sources (best for transition obligations)

**What they are:** Three overlapping sources cover the LGR track: the council's own LGR page, the MHCLG consultation, and the national LGR programme updates.

**Exactly where to go:**
- NCC LGR page: https://www.nottinghamcity.gov.uk/your-council/local-government-reorganisation/
- MHCLG consultation on Nottinghamshire and Nottingham: https://consult.communities.gov.uk/local-government-reorganisation/nottinghamshire-and-nottingham/
- LGR programme updates collection: https://www.gov.uk/government/collections/local-government-reorganisation-policy-and-programme-updates
- LGR implementation guidance: https://www.gov.uk/government/publications/local-government-reorganisation-implementation-guidance
- Nottinghamshire and Nottingham LGR collection: https://www.gov.uk/government/collections/nottinghamshire-and-nottingham-local-government-reorganisation
- English Devolution and Community Empowerment Act 2026: https://bills.parliament.uk/bills/4002

**How the scraper watches this:** Your sources.json already watches these key LGR paths:
```
/government/collections/local-government-reorganisation-policy-and-programme-updates
/government/collections/nottinghamshire-and-nottingham-local-government-reorganisation
/government/consultations/local-government-reorganisation-in-nottinghamshire-and-nottingham
```
When MHCLG publishes a statutory order decision or new guidance, it will appear in the Intelligence tab automatically. However, check the NCC LGR page and the consultation page manually each week because council-level content and consultation responses are not scraped by the current configuration.

**What to look for:**
- Statutory consultation outcomes — when MHCLG publishes a decision, this creates immediate transition planning obligations.
- Implementation guidance milestones — map these to NCC obligations.
- Shadow authority elections — timetable announcements for when a shadow authority is established.
- Day-one preparation milestones — service transfer plans, asset and liability mapping, TUPE arrangements, IT systems, and governance frameworks for the new authority.

**Critical LGR milestone:** The moment the Secretary of State issues the final Statutory Boundary Order for the Nottingham/Nottinghamshire unitary structure, log an immediate High-Risk obligation requiring the Section 151 Officer (Stuart Fair) to review asset and liability arrangements for any items planned for transfer. This is not about freezing the asset registry as if you have Section 114 powers — that is the S151 Officer's decision — but the tracker should flag that this transition point triggers a formal finance review obligation.

**How often to check manually:** Weekly. The LGR timetable is moving quickly.

**Obligation level:** Creates monitoring obligations (ongoing LGR tracking) and, once the statutory order is made, a cascade of transition planning periodic obligations.

---

### Source 7: Your Intelligence Tab (already working for you)

**What it is:** Your tracker already scrapes GOV.UK, Parliament, PSAA, NAO, CIPFA, EMCCA, and committee pages automatically via update_intelligence.py. The Intelligence tab is your first alert system.

**What to look for:**
- Items flagged Material = **Yes** — these matched on at least two keyword themes and are the most likely to create obligations. Review each one.
- Items flagged **Unclear** — worth a glance; matched on one theme only. Quick judgment call.
- The Matched column (column G in the sheet) shows you exactly *why* an item was flagged, for example "Local, Audit". Use this to decide quickly whether it is relevant.

**What to do with each item:**
- If it creates a new requirement for the council, add a row to the Obligations tab and write "Raised as OB-00X" in the Notes column.
- If it is background context or monitoring only, mark as Reviewed with a short note.
- If it is noise, mark as Reviewed and consider adding the title phrase to `exclude_keywords` in sources.json.

---

## Part 3: Tuning the Scraper — sources.json

The scraper only reads sources.json — you never need to edit the Python files. Here is what each section controls and what you should add or adjust.

### Adding new mandatory search terms

The section `govuk_search_terms` lists keyword searches run against GOV.UK. The following terms are already there and should stay:

```
"local audit reform", "local audit office", "audit backstop",
"public sector audit appointments", "local government reorganisation",
"english devolution bill", "exceptional financial support",
"best value intervention", "whole of government accounts",
"code of practice local authority accounting"
```

Consider adding these if they are not already present:
- `"ministerial envoy nottingham"` — to catch any new envoy publications directly
- `"continuous improvement committee"` — to catch any national guidance on this committee type
- `"shadow authority"` — to catch vesting day and shadow authority announcements

### Watched GOV.UK paths

These five paths are already watched and will auto-collect all child documents when the scraper runs:

```json
"/government/collections/local-government-reorganisation-policy-and-programme-updates",
"/government/collections/nottinghamshire-and-nottingham-local-government-reorganisation",
"/government/consultations/local-government-reorganisation-in-nottinghamshire-and-nottingham",
"/government/publications/local-audit-reform",
"/government/collections/statutory-intervention-nottingham-city-council-minded-to-decision"
```

If MHCLG publishes a new collection specifically for Vesting Day or Shadow Authority guidance, add its path here.

### Watching NCC committee pages (`ncc_committees`)

NCC's committee site (committee.nottinghamcity.gov.uk) runs the ModernGov platform, whose pages are `.aspx`, not the GOV.UK content API — so these **cannot** go in `watched_govuk_paths`. They have their own block, `ncc_committees`, which has its own small scraper:

```json
"ncc_committees": {
  "enabled": true,
  "since_date": "2026-01-01",
  "pages": [
    { "name": "Audit Committee",       "url": ".../ieListMeetings.aspx?CommitteeId=145" },
    { "name": "Improvement Committee", "url": ".../ieListMeetings.aspx?CommitteeId=1175" }
  ],
  "keywords": ["audit","improvement","governance","standards","treasury","accounts","scrutiny","risk"]
}
```

- **To add another committee:** find its "Browse meetings" page (`ieListMeetings.aspx?CommitteeId=NNN`) and copy a line into `pages` with the committee name. A `mgCommitteeDetails.aspx?ID=NNN` URL also works — the scraper follows the Browse-meetings link for you.
- **`since_date`** stops the back-catalogue of old meetings flooding the feed. It is set to 2026-01-01; meetings before that are skipped. Raise it if you only want the current year.
- **`keywords`** filter which committees are kept by matching the committee name and link text. Committee items are always treated as locally material (they are NCC's own meetings), so they reach the sheet as Material = Yes rather than being suppressed.

### How the exclusion rules work

The `exclusion_rules` section in sources.json has three parts:

| Section | What it does | Current examples |
|---|---|---|
| `exclude_keywords` | Drops any item whose title contains these phrases before scoring | "revenue and customs", "hmrc", "employment tribunal", "planning inspector" |
| `exclude_nations` | Drops items about devolved nations | "scotland", "wales", "northern ireland" |
| `exclude_lgr_councils` | Drops LGR items from other counties | "cambridgeshire", "derbyshire", "devon" and 17 others |

**Important nuance on "commissioner":** The word "commissioner" appears in your `intervention_keywords` (which scores items as material) and also in the `Governance and Transparency` theme keywords. This is intentional because historic Commissioner documents from NCC's intervention are still relevant. The key distinction is that since 24 March 2026 the oversight structure uses **Ministerial Envoys**, not Commissioners. So if you see an item in the Intelligence tab flagged only because of "commissioner" and it refers to a historic Commissioner role rather than an active intervention, mark it as Reviewed with a note "Historic commissioner reference only." Do not add "commissioner" to exclude_keywords — that would drop the remaining Commissioner reports and the Ministerial response documents which are still live evidence sources.

### The stop-word principle for manual review

When reviewing Intelligence items, these patterns are reliably noise and can be marked Reviewed immediately:

| What you see in the title | Why it is noise | What to do |
|---|---|---|
| Any title naming a specific county other than Nottinghamshire or Nottingham | District-level operational changes with no City impact | Mark Reviewed: "Other county LGR, no NCC impact" |
| "Consultation Open" with no mention of Nottingham | General public engagement notices | Mark Reviewed: "Monitor — action only when decision published" |
| "Capital Gains Manual" or "Employment Tribunal" or any HMRC reference | These match on "commissioner" in its tax/legal sense | Mark Reviewed: "False positive — not intervention commissioner". Add to exclude_keywords if this pattern recurs. |
| PSAA items about another named council's audit contract | Procurement news for other councils | Mark Reviewed: "Other council audit, monitoring only" |

---

## Part 4: How to Write a Good Obligation

A well-written obligation answers five questions in one or two sentences:

1. Who must act? (NCC, or a specific director or committee)
2. What must they do? (The concrete deliverable)
3. By when or how often?
4. Under what authority? (The source trigger)
5. What will prove it happened? (The evidence)

### Template

> NCC must [do specific thing] by [date or event], as required by [source trigger]. Evidence: [what proof looks like].

### Good examples

> NCC must prepare and agree the Continuous Service Improvement Plan with the Ministerial Envoys within three months of 24 March 2026. Evidence: Improvement Committee endorsement minute and published CSIP document.

> The Head of Internal Audit must align the internal audit plan with Local Audit Office standards and guidance and ensure synergy with external assurance, as required by the CSIP Risk Management and Internal Audit programme. Evidence: Updated Internal Audit Annual Plan approved by Audit Committee.

> NCC must continue to work with other councils in the Nottinghamshire area for unitary local government, as required by the 24 March 2026 directions. Evidence: Ongoing LGR programme updates, committee papers, and joint transition planning documents.

### What makes an obligation too vague

Avoid obligations like "Monitor LGR" or "Keep track of audit reform." These do not have a clear deliverable, owner, or evidence route. Keep them in the Intelligence tab as monitoring notes, not in Obligations.

### What makes an obligation too narrow

Avoid obligations like "Send email to G Robinson about Table 5 note." This is an action, not an obligation. The obligation is "Provide clarification on Table 5 in the Treasury Management Report." The email is the action beneath it, linked by Parent Obligation ID in the Actions tab.

---

## Part 5: The Mature Tracker — What Good Looks Like

### Obligations tab

At full maturity, your Obligations tab should have:

- Every live obligation with a completed Owner and Target Date — no blanks in those two columns.
- Source Trigger using the exact document title and date, not just "GOV.UK" or "committee paper."
- Evidence Required written specifically enough that anyone could pick it up and know what to look for.
- Evidence Location filled in with a direct URL (not a homepage), document title, or folder path once evidence exists.
- Risk Rating and Status kept up to date — do not leave statuses as "Not started" for obligations that are clearly in progress.
- A mix of themes reflecting both workstreams.

### Actions tab

At full maturity, every In Progress or Ongoing obligation should have at least one corresponding action row in the Actions tab with:

- Parent Obligation ID linking it to the right obligation row.
- A clear action statement.
- Owner and Due Date.
- Evidence Link filled in when the step is completed.

### Dashboard

Before any meeting, run `run_build_dashboard.bat` so the dashboard is current. A strong dashboard shows:

- No obligations with a blank owner or missing evidence for Complete items.
- Overdue count as low as possible — anything overdue should have a note explaining why.
- The Attention Needed list actively managed and short.

The dashboard already colour-codes tiles: red means action needed, green means all clear. The Attention Needed list names specific obligations that are late or due within 30 days, with owner and date. This is the tab to open when John or an inspector asks for the current picture.

---

## Part 6: Fields Reference

### Obligations Tab

| Field | What to put in it | Example |
|---|---|---|
| Obligation ID | Sequential number: OB-001, OB-002 etc. | OB-006 |
| Obligation | One to two sentences. Start with "NCC must" or director/committee name. | NCC must prepare and agree the CSIP within three months of 24 March 2026 directions. |
| Source / Trigger | Exact document title and date. | Nottingham City Council: Directions made under the Local Government Act 1999 (24 March 2026) |
| Theme | One of the tracker's five themes. | Governance and Transparency |
| Owner | Named officer, director, or team. If unsure, ask John. | S Fair / L Dowdican |
| Risk Rating | High / Medium / Low. High = statutory risk if missed. | High |
| Target Date | Date the obligation should be complete or next reviewed. | 2026-06-24 |
| Status | Not started / In progress / Complete / Blocked / Ongoing | In progress |
| Evidence Required | Specific statement of what proof will look like. Not a URL — describe what you are looking for. | Published CSIP endorsed by Improvement Committee minute. |
| Evidence Location | URL or document path — fill in once evidence exists. Direct link to the specific document, not a homepage. | https://committee.nottinghamcity.gov.uk/[specific pack link] |
| Sign Off By | Who confirms completion. | Improvement Committee / John |
| Last Updated | Date you last reviewed or updated this row. | 2026-06-08 |
| Notes | Anything that helps context — links to related obligations, caveats, cross-track risk flags. | Related to OB-L1. Deadline is 24 June 2026. |
| Obligation Level | Enduring / Periodic / Monitoring — the Part 1 classification (dropdown). | Periodic |

---

## Part 7: The Core Obligations List — What to Populate First

### Local Audit and Improvement

**OB-A1 — Continuous Improvement Committee establishment**
Source: 24 March 2026 Directions.
Obligation: NCC must establish the Continuous Improvement Committee with the required membership including Opposition Leaders, independent external leads for Adults and Children, and Ministerial Envoys.
Evidence: Committee Terms of Reference published; first meeting held with correct membership.
Target: Completed at 4 June 2026 meeting — update Status to Complete and add evidence link.

**OB-A2 — CSIP preparation and agreement**
Source: 24 March 2026 Directions; Improvement Committee report 4 June 2026.
Obligation: NCC must prepare and agree the CSIP with the Ministerial Envoys within three months of 24 March 2026.
Deadline: **24 June 2026.** This is the most time-critical obligation in the tracker right now.
Evidence: Improvement Committee endorsement minute; published CSIP document.
Risk: High.

**OB-A3 — Embed financial stability improvements**
Source: 24 March 2026 Directions; CSIP Financial Sustainability and Management programme.
Obligation: NCC must embed improvements in financial management, savings delivery, accounts production, and capital programme governance.
Evidence: Audit Committee treasury and accounts papers; CSIP performance reporting; six-monthly Improvement Committee reports.
Status: Ongoing.

**OB-A4 — Embed scrutiny and decision-making improvements**
Source: 24 March 2026 Directions; CSIP Governance, Scrutiny and Decision Making programme.
Evidence: Improvement Committee reports; Corporate Scrutiny Committee papers; updated Scheme of Delegation.
Status: Ongoing.

**OB-A5 — Embed risk management and internal audit improvements (including LAO alignment)**
Source: 24 March 2026 Directions; CSIP Risk Management and Internal Audit programme.
Obligation: NCC must embed improvements in risk management and internal audit, including aligning with Local Audit Office standards.
Evidence: Internal Audit Annual Plan and progress reports to Audit Committee; Head of Internal Audit opinion; alignment note against LAO standards.
Status: Ongoing.

**OB-A6 — Cooperate with Ministerial Envoys**
Source: 24 March 2026 Directions.
Obligation: NCC must cooperate with Envoys, provide access, and respond to recommendations.
Evidence: Improvement Committee meeting records showing Envoy attendance; responses to Envoy recommendations.
Status: Ongoing.

**OB-A7 — External audit findings response**
Source: Audit Committee 27 March 2026; External Audit Findings 2024/25.
Obligation: NCC must respond to each recommendation in the external auditor's Annual Report and Audit Findings (ISA 260).
Evidence: Management response document; Audit Committee minute noting acceptance; completed action evidence for each recommendation.

**OB-A8 — Statement of Accounts publication**
Source: Accounts and Audit Regulations; Audit Committee work programme.
Obligation: NCC must produce and publish audited accounts with a signed audit opinion.
Evidence: Published accounts on council website at https://www.nottinghamcity.gov.uk/your-council/about-the-council/statement-of-accounts-and-reports/ — link to the specific year's document, not the page homepage.

**OB-A9 — Annual Governance Statement**
Source: Accounts and Audit Regulations; Audit Committee work programme July 2026.
Obligation: NCC must produce and publish an Annual Governance Statement reflecting the council's current governance position and any significant weaknesses.
Evidence: Published AGS; Audit Committee approval minute. Target: July 2026 committee cycle.

**OB-A10 — Monitor Local Audit Office transition**
Source: PSAA abolition and LAO transition. Bill Butler named as preferred LAO Chair candidate May 2026.
Obligation: NCC must understand and plan for how the LAO transition affects its audit arrangements. PSAA-procured contract runs to 2027/28.
Evidence: Audit Committee briefing note on LAO implications; updated audit plan if needed.

**OB-A11 — Audit Committee Recommendation Tracker: three sub-obligations**

Break OB-A11 into three explicit actions, each with its own row in the Actions tab linked to a parent obligation:

*OB-A11.1 — Contract Procedure Rules Exemption Benchmarking*
- Owner: A Spice / D Cafferty (Procurement)
- Target: July 2026 Audit Committee
- Action: Publish a benchmarking exercise comparing NCC's contract exemption rates against neighbouring Nottinghamshire authorities.
- Evidence: Formal benchmarking appendix in the Procurement Annual Report.

*OB-A11.2 — Treasury Management Table 5 Clarification*
- Owner: Gareth Robinson (Director of Finance)
- Target: June 2026 Audit Committee
- Action: Provide a clarification note splitting debt and investments between the General Fund and the Housing Revenue Account (HRA) in Table 5 of the Treasury Management Report.
- Evidence: Signed addendum note or updated table in the finalised Treasury Management Strategy.

*OB-A11.3 — UN PRI and UNGP Legal Briefing*
- Owner: Beth Brown (Strategic Director of Legal and Governance)
- Target: June 2026 Audit Committee
- Action: Provide a formal briefing note once legal advice on UN PRI (Principles for Responsible Investment) and UNGP (United Nations Guiding Principles) compliance frameworks is received.
- Evidence: Distributed legal briefing note; logged in committee minutes or correspondence record.

### LGR Obligations

**OB-L1 — Continue LGR work with Nottinghamshire councils**
Source: 24 March 2026 Directions; CSIP LGR priority service improvement area.
Obligation: NCC must continue to work with other Nottinghamshire councils to define, coordinate, and implement safe day-one establishment of a new unitary authority.
Evidence: Joint LGR committee papers; transition programme updates to Improvement Committee; cooperation records with other councils.
Status: Ongoing.

**OB-L2 — Respond to MHCLG LGR consultation and statutory order process**
Source: MHCLG consultation for Nottinghamshire and Nottingham (from 25 March 2026).
Obligation: NCC must track the decision and respond to statutory order implications.
Evidence: Council response to consultation; record of statutory order decision; legal advice on transition implications.

**OB-L3 — Develop day-one LGR transition plan**
Source: CSIP LGR priority area; MHCLG LGR implementation guidance (May 2026).
Obligation: NCC must work toward safe and legal day-one establishment of the new unitary authority.
Evidence: Transition programme plan; governance framework for shadow authority; service continuity planning documents.
Status: Ongoing. Planning horizon: shadow authority elections approximately May 2027; Vesting Day approximately 1 April 2028.

**OB-L4 — Internal audit plan covering LGR transition risks**
Source: CSIP Risk Management and Internal Audit programme; seeded OB-004.
Obligation: The internal audit plan must cover LGR transition risks including service demerger, asset and liability transfer, and governance during the shadow authority phase.
Evidence: Updated Internal Audit Annual Plan with LGR transition section; Audit Committee approval.
Target: October 2026.

**OB-L5 — English Devolution and Community Empowerment Act 2026 compliance**
Source: English Devolution and Community Empowerment Act 2026 (Royal Assent confirmed).
Obligation: NCC must review its governance, audit committee arrangements, and successor body governance in light of the Act's statutory transparency and accountability codes.
Evidence: A formal gap analysis report submitted to the July 2026 Audit Committee (or the next appropriate committee meeting) verifying that NCC's successor-body governance framework matches the transparency and accountability requirements of the 2026 Act. The gap analysis should reference the relevant sections of the Act against the current Audit Committee Terms of Reference and the proposed successor body governance model.
Target: July 2026 committee cycle.
Risk: Medium — the Act has received Royal Assent but the detailed implementation timeline for specific provisions will become clearer as statutory guidance is issued.

---

## Part 8: Critical Dates to Keep Visible

These are the hardcoded milestone dates that matter most. You should ensure each one has an obligation row with the correct Target Date so the dashboard's Attention Needed list will flag it in the 30-day window before it falls due.

| Obligation | Deadline | Why critical |
|---|---|---|
| OB-A2 (CSIP agreement) | 24 June 2026 | Three months from 24 March 2026 directions. Statutory. |
| OB-A11.2 (Table 5 clarification) | June 2026 Audit Committee | Audit Committee resolution. |
| OB-A11.3 (UN PRI legal briefing) | June 2026 Audit Committee | Audit Committee resolution. |
| OB-A9 (Annual Governance Statement) | July 2026 Audit Committee | Statutory accounts and governance cycle. |
| OB-A11.1 (Contract exemption benchmarking) | July 2026 Audit Committee | Audit Committee resolution. |
| OB-A10 (LAO transition briefing) | September 2026 | External audit contract planning horizon. |
| OB-L4 (LGR transition audit plan) | October 2026 | Audit planning horizon. |
| OB-L3 (Day-one transition plan) | Ongoing to May 2027 (shadow authority) | Ultimate LGR vesting horizon. |

---

## Part 9: Cross-Track Risk — When LGR and Audit Obligations Conflict

A mature tracker must flag when an LGR obligation could create a financial control risk. The most common version of this is an LGR transition action that requires procurement or capital spending at a time when the council is under spending restraint.

**When you are adding an action row under an LGR-themed obligation** and the action involves words like "procure", "contract", "vendor", "software upgrade", "capital", or "IT system migration", add a note in the Notes column of the action row:

> ⚠️ Procurement/capital action: requires Section 151 sign-off under current spending controls before proceeding. Confirm with Stuart Fair or Gareth Robinson.

This does not stop the work. It ensures the tracker records that the financial gateway has been identified and must be checked. This is exactly the kind of cross-track thinking that makes you useful as an audit and risk trainee — you are spotting the control point before it becomes a problem.

---

## Part 10: How to Tell a Good Obligation from Noise

Use this checklist for every potential obligation:

| Question | If Yes | If No |
|---|---|---|
| Is there a word like "must", "required", "shall", or "directions require"? | Likely an obligation | Probably monitoring or context |
| Is NCC specifically named, or does it apply to all councils? | Strengthen as NCC obligation | May be general monitoring |
| Can you name who in NCC is responsible? | Add to Obligations tab with owner | Hold in Intelligence until you find an owner |
| Can you describe what proof of completion looks like? | Add to Obligations tab | Not yet ready — hold as draft |
| Does it have a date or a committee cycle it must meet? | Set as Target Date | Use next relevant committee date as proxy |
| Is this a one-off deliverable or ongoing? | Periodic obligation | Ongoing obligation — set Status = Ongoing |

If you cannot answer three or more of these questions, the item is not yet ready to be an obligation. Keep it in the Intelligence tab as a monitoring note until you can.

---

## Part 11: Version Control and Backup

Because the whole system runs on local files — AuditTracker.xlsx, the Python scripts, sources.json, and seen_hashes.txt — it depends on the local machine. If the laptop is replaced or files are lost, the system can be rebuilt, but you would lose all manually entered obligations and actions.

**Weekly backup rule:** Every Friday, after running run_weekly_update.bat and reviewing new items, copy the entire tracker folder to the secure network drive or SharePoint document library. The folder to copy is the one containing:
- AuditTracker.xlsx (the workbook with all your data)
- sources.json (your tuning settings)
- seen_hashes.txt (the scraper's memory — without this it will re-add every item it has ever seen)

You do not need to back up the Python files separately as they are fixed code, but the three files above are the ones that would take time to rebuild.

**Handover note:** If you leave the role, the incoming person needs to know: (1) the folder location, (2) the virtual environment setup steps in the GUIDE.md, (3) where the network backup is kept, and (4) the contact at John's team who knows the obligation ownership context.

---

## Part 12: Signals That the Tracker Needs Updating

Watch for these triggers and act within one working day:

- A new GOV.UK publication with Nottingham in the title, especially from MHCLG.
- A new Audit Committee or Improvement Committee paper is published.
- An Audit Committee resolution is made at a meeting.
- A new entry appears on the MHCLG Nottingham statutory intervention collection page.
- John or another officer mentions a new commitment made to government or to committee.
- A recommendation tracker item moves from Pending to Responded, or a new item is added.
- A PSAA or LAO update mentions the audit contract or external audit timetable.
- The LGR consultation page is updated with a decision or next step.
- The statutory order for Nottingham/Nottinghamshire LGR is published — this triggers a cascade of new transition obligations immediately.

---

## Part 13: Key Contacts and Owners Reference

| Area | Named Officer |
|---|---|
| Finance and Treasury | Gareth Robinson, Director of Finance |
| Section 151 / Corporate Finance Director | Stuart Fair, Corporate Director for Finance and Resources |
| Internal Audit | Lynne Dowdican, Head of Internal Audit |
| Audit Committee support | Kate Morris, Scrutiny and Audit Support Officer |
| LGR and Policy | James Rhodes, Director of Policy, Performance and Communications |
| Chief Executive | Sajeeda Rose, Chief Executive |
| Legal and Governance | Beth Brown, Strategic Director of Legal and Governance |
| Risk | D Bowring |
| Procurement | A Spice / D Cafferty |

When unsure, use the Director column in the Work Programme or the SAO/RDL column in the CSIP Detailed Delivery Plan.

---

## Part 14: Weekly, Monthly, and Quarterly Routines

### Weekly (about 15 minutes)

1. Close AuditTracker.xlsx and run `run_weekly_update.bat`.
2. Open the Intelligence tab. Filter Material = Yes. Read each new item.
   - If it creates a new obligation: add a row to Obligations tab. Mark as Reviewed. Note the Obligation ID.
   - If it is background: mark as Reviewed with a short note.
   - If Unclear: spend 30 seconds reading the source URL.
3. Check the LGR sources manually (GOV.UK collection, MHCLG consultation page, NCC LGR page).
4. Update any Obligation statuses that have changed since last week.

### Before any committee meeting (30 minutes)

1. Close AuditTracker.xlsx and run `run_build_dashboard.bat`.
2. Open the Dashboard. Look at the Attention Needed list — chase any overdue or due-in-30-days items.
3. Read the committee papers. Cross-check any new recommendations or management responses against your Obligations tab.
4. Add any new obligations before the meeting so you can brief John if asked.

### Monthly (about 5 minutes)

1. Run `run_monthly_report.bat` to produce the Word report.
2. Read it through — check for blank owners, missing evidence on complete items, overdue items needing escalation.
3. Send or file as instructed by John.

### Quarterly (about 30 minutes)

1. Review all Ongoing obligations — are they still live, or can they be closed?
2. Review the CSIP against the tracker — are all CSIP programmes covered by at least one obligation?
3. Check whether any new external audit, committee, or government papers have created obligations not yet captured.
4. Review sources.json search terms — are they still picking up the right material?

---

## Part 15: The Source Quick Reference

| What you need | Where to go | How often |
|---|---|---|
| The legal trigger for an obligation | GOV.UK Nottingham directions page and explanatory memorandum | Quarterly or when new directions issued |
| What the council says it will do | 4 June 2026 Improvement Committee report; CSIP Appendix 1 | After each Improvement Committee meeting |
| Specific milestones, owners, dates | CSIP Detailed Delivery Plan (Appendix 2) | Monthly |
| Audit-specific follow-up | Audit Committee minutes, Recommendation Tracker, Work Programme | After every Audit Committee meeting |
| Published evidence of completion | Statement of Accounts and Reports page; committee publication pages | Weekly in accounts season; monthly otherwise |
| LGR timetable and consultation | NCC LGR page; MHCLG consultation page; GOV.UK LGR collection | Weekly |
| National audit reform context | Intelligence tab (PSAA, NAO, CIPFA items) | Weekly via scraper; manual check monthly |
| New legislation | Intelligence tab (Parliament Bills items) | Weekly via scraper |

---

## Part 16: Role Enforcement and the Validation Check (new)

The judgement that used to live only in your head — who owns what, whether an item is really an obligation, whether a row is complete enough to show an inspector — is now written down as rules in `audit_logic.py`. You do not edit that file; you just benefit from the checks.

### What is enforced

- **Owners (Part 13).** The agreed officer names live in code. If an Owner cell names someone who is not a recognised Part 13 contact or a council body, the check flags it. Use the names exactly as they appear in Part 13.
- **Obligation level (Part 1).** Each obligation carries an Enduring / Periodic / Monitoring level in its own column.
- **The Section 151 spending gateway (Part 9).** When an action mentions procurement, contract, vendor, capital, software upgrade, or IT system migration under an LGR obligation, the ⚠️ Section 151 sign-off note is attached automatically. Action A-004 is the worked example already in the Actions tab.
- **Maturity (Part 5) and readiness (Part 10).** Every obligation is checked for a blank owner, a missing target date when it is not Ongoing, a vague source ("GOV.UK", "committee paper"), missing Evidence Required, missing Evidence Location on Complete items, and homepage-only evidence links.

### How to run the check

Close AuditTracker.xlsx, then run:

```
.venv\Scripts\python.exe populate_tracker.py
```

This rewrites the Obligations and Actions tabs from `tracker_data.py`, re-attaches the S151 notes, and prints a validation report listing anything that falls short. A clean register prints only OB-L6 — which is *meant* to be flagged, because it is the contingent obligation that only goes live when the Statutory Boundary Order is published (Part 6); give it a target date then.

**When to run it:** not weekly. Run it (1) the first time you set the tracker up, (2) whenever you want to re-seed from the canonical list, and (3) at your quarterly review as a quick "is the register still mature?" sweep. Day to day you still edit obligations by hand in Excel — `populate_tracker.py` overwrites the Obligations and Actions tabs, so do not run it if you have unsaved hand edits you want to keep that are not also in `tracker_data.py`.

### Adding a permanent new obligation

For a one-off obligation, just add a row in Excel. For an obligation you want to survive a re-seed (or a fresh `setup_tracker.py` rebuild), add it to the `OBLIGATIONS` list in `tracker_data.py` using the same shape as the others, then run `populate_tracker.py`. The same applies to actions via the `ACTIONS` list — actions added there get the S151 gateway check applied automatically.

---

## Quick recap — what you actually have to do now

- **Weekly:** close the workbook, run `run_weekly_update.bat`, review Material = Yes items (now including new Audit and Improvement Committee meetings), set Reviewed, raise obligations where needed. Unchanged from before, just with committee meetings included.
- **When you add/edit obligations:** fill the new **Obligation Level** column; use Part 13 owner names; for LGR spending actions, keep the ⚠️ S151 note.
- **Quarterly (or after a big change):** run `populate_tracker.py` and clear any warnings it prints.
- **Before meetings / monthly:** `run_build_dashboard.bat` and `run_monthly_report.bat` as before.
- **Weekly backup (Part 11):** now also copy `tracker_data.py` along with AuditTracker.xlsx, sources.json, and seen_hashes.txt.

---

*End of guide. Version 2 — updated June 2026 (build with committee scraping, role enforcement, and pre-populated obligations). Update this document if the council's governance structure, officer contacts, or source URLs change.*
