"""
Canonical obligations and actions for the NCC Audit Reform and LGR tracker.

This is the single source of truth for the seeded content described in the
Tracker Operating Guide v2, Parts 7, 8 and 13. Both setup_tracker.py (fresh
build) and populate_tracker.py (refresh an existing workbook) import from here
so the seed and the live data never drift apart.

Owners are taken from Part 13. Target dates are the hard milestones in Part 8.
Obligation Level is the Part 1 classification (Enduring / Periodic / Monitoring).

LAST_UPDATED is stamped on every row. Change it when you refresh this file.
"""

from __future__ import annotations

from audit_logic import OWNERS, s151_note_for_action

LAST_UPDATED = "2026-07-11"

# Column order for the Obligations sheet. "Obligation Level" is appended last so
# the existing data-validation ranges on Risk (F) and Status (H) are undisturbed.
OBLIGATION_COLUMNS = [
    "Obligation ID", "Obligation", "Source / Trigger", "Theme", "Owner",
    "Risk Rating", "Target Date", "Status", "Evidence Required",
    "Evidence Location", "Sign Off By", "Last Updated", "Notes",
    "Obligation Level",
]

ACTION_COLUMNS = [
    "Action ID", "Parent Obligation ID", "Action", "Owner",
    "Start Date", "Due Date", "Status", "Percent Complete",
    "Evidence Link", "Notes",
]

OBLIGATION_LEVELS = ["Enduring", "Periodic", "Monitoring", "Statutory"]

# Shorthand for the five tracker themes (Guide Part 6 — must be one of these).
T_AUDIT_PROC = "Audit Procurement"
T_FIN = "Financial Reporting"
T_CONTROLS = "Internal Controls"
T_GOV = "Governance and Transparency"
T_LGR = "LGR Transition"

# Useful evidence anchors
IMP_CTTE_PACK = (
    "https://committee.nottinghamcity.gov.uk/documents/g11742/"
    "Public%20reports%20pack%2004th-Jun-2026%2014.00%20Improvement%20Committee.pdf"
)
ACCOUNTS_PAGE = (
    "https://www.nottinghamcity.gov.uk/your-council/about-the-council/"
    "statement-of-accounts-and-reports/"
)


def _ob(oid, obligation, source, theme, owner, risk, target, status,
        evidence_req, evidence_loc, sign_off, notes, level):
    """Build an obligation dict keyed by sheet header."""
    return {
        "Obligation ID": oid,
        "Obligation": obligation,
        "Source / Trigger": source,
        "Theme": theme,
        "Owner": owner,
        "Risk Rating": risk,
        "Target Date": target,
        "Status": status,
        "Evidence Required": evidence_req,
        "Evidence Location": evidence_loc,
        "Sign Off By": sign_off,
        "Last Updated": LAST_UPDATED,
        "Notes": notes,
        "Obligation Level": level,
    }


# ---------------------------------------------------------------------------
# Local Audit and Improvement obligations (Guide Part 7)
# ---------------------------------------------------------------------------
OBLIGATIONS = [
    _ob(
        "OB-A1",
        "NCC must establish the Continuous Improvement Committee with the "
        "required membership including Opposition Leaders, independent external "
        "leads for Adults and Children, and Ministerial Envoys.",
        "Nottingham City Council: Directions made under the Local Government Act "
        "1999 (24 March 2026)",
        T_GOV, OWNERS["Legal and Governance"], "High", "2026-06-04", "Complete",
        "Committee Terms of Reference published; first meeting held with correct "
        "membership.",
        IMP_CTTE_PACK, "Improvement Committee / John",
        "Completed at the 4 June 2026 Improvement Committee meeting. Was part of "
        "the old OB-005 commissioner row.",
        "Periodic",
    ),
    _ob(
        "OB-A2",
        "NCC must prepare and agree the Continuous Service Improvement Plan (CSIP) "
        "with the Ministerial Envoys within three months of the 24 March 2026 "
        "directions.",
        "24 March 2026 Directions; Improvement Committee report 4 June 2026",
        T_GOV, OWNERS["Chief Executive"], "High", "2026-06-24", "In progress",
        "Improvement Committee endorsement minute; published CSIP document.",
        "", "Improvement Committee / Ministerial Envoys",
        "MOST TIME-CRITICAL obligation. Deadline 24 June 2026 = three months from "
        "the 24 March 2026 directions.",
        "Statutory",
    ),
    _ob(
        "OB-A3",
        "NCC must embed improvements in financial management, savings delivery, "
        "accounts production, and capital programme governance.",
        "24 March 2026 Directions; CSIP Financial Sustainability and Management "
        "programme",
        T_FIN, OWNERS["Section 151"], "High", "", "Ongoing",
        "Audit Committee treasury and accounts papers; CSIP performance reporting; "
        "six-monthly Improvement Committee reports.",
        "", "Improvement Committee",
        "SAO Finance: S Fair. Monitored six-monthly via the Improvement Committee.",
        "Monitoring",
    ),
    _ob(
        "OB-A4",
        "NCC must embed improvements in scrutiny and decision making across the "
        "council's governance arrangements.",
        "24 March 2026 Directions; CSIP Governance, Scrutiny and Decision Making "
        "programme",
        T_GOV, OWNERS["Legal and Governance"], "Medium", "", "Ongoing",
        "Improvement Committee reports; Corporate Scrutiny Committee papers; "
        "updated Scheme of Delegation.",
        "", "Improvement Committee",
        "Ongoing CSIP programme.",
        "Monitoring",
    ),
    _ob(
        "OB-A5",
        "NCC must embed improvements in risk management and internal audit, "
        "including aligning the internal audit function with Local Audit Office "
        "standards and guidance and ensuring synergy with external assurance.",
        "24 March 2026 Directions; CSIP Risk Management and Internal Audit "
        "programme",
        T_CONTROLS, OWNERS["Internal Audit"], "High", "", "Ongoing",
        "Internal Audit Annual Plan and progress reports to Audit Committee; Head "
        "of Internal Audit opinion; alignment note against LAO standards.",
        "", "Audit Committee",
        "Direct CSIP obligation: internal audit must align with LAO standards. "
        "Supported by D Bowring (Risk).",
        "Monitoring",
    ),
    _ob(
        "OB-A6",
        "NCC must cooperate with the Ministerial Envoys, provide access, and "
        "respond to their recommendations.",
        "24 March 2026 Directions",
        T_GOV, OWNERS["Chief Executive"], "High", "", "Ongoing",
        "Improvement Committee meeting records showing Envoy attendance; responses "
        "to Envoy recommendations.",
        "", "Chief Executive / Improvement Committee",
        "Since 24 March 2026 the oversight structure uses Ministerial Envoys, not "
        "Commissioners.",
        "Monitoring",
    ),
    _ob(
        "OB-A7",
        "NCC must respond to each recommendation in the external auditor's Annual "
        "Report and Audit Findings (ISA 260).",
        "Audit Committee 27 March 2026; External Audit Findings 2024/25",
        T_FIN, OWNERS["Finance and Treasury"], "High", "2026-07-31", "In progress",
        "Management response document; Audit Committee minute noting acceptance; "
        "completed action evidence for each recommendation.",
        "", "Audit Committee",
        "Tie target to the next Audit Committee cycle.",
        "Periodic",
    ),
    _ob(
        "OB-A8",
        "NCC must produce and publish audited accounts with a signed audit opinion.",
        "Accounts and Audit Regulations 2015; Audit Committee work programme",
        T_FIN, OWNERS["Section 151"], "High", "2026-09-30", "In progress",
        "Published Statement of Accounts; auditor's opinion; note on any disclaimer.",
        "", "Audit Committee",
        "Evidence Location must link to the SPECIFIC year's document on the "
        "Statement of Accounts page, not the homepage: " + ACCOUNTS_PAGE,
        "Enduring",
    ),
    _ob(
        "OB-A9",
        "NCC must produce and publish an Annual Governance Statement reflecting the "
        "council's current governance position and any significant weaknesses.",
        "Accounts and Audit Regulations 2015; Audit Committee work programme July "
        "2026",
        T_GOV, OWNERS["Legal and Governance"], "High", "2026-07-31", "In progress",
        "Published AGS; Audit Committee approval minute.",
        "https://nottinghamcity.gov.uk", "Audit Committee",
        "Target: July 2026 committee cycle. Draft AGS 2024/25 confirmed published "
        "online; awaiting Audit Committee approval minute.",
        "Enduring",
    ),
    _ob(
        "OB-A10",
        "NCC must understand and plan for how the Local Audit Office (LAO) "
        "transition affects its audit arrangements, and brief the Audit Committee.",
        "PSAA abolition and Local Audit Office transition",
        T_AUDIT_PROC, OWNERS["Internal Audit"], "High", "2026-09-30", "In progress",
        "Audit Committee briefing note on LAO implications; updated audit plan if "
        "needed.",
        "", "Audit Committee",
        "PSAA-procured contract runs to 2027/28. Bill Butler named preferred LAO "
        "Chair candidate May 2026. Was the old OB-002.",
        "Monitoring",
    ),
    _ob(
        "OB-A11",
        "NCC must progress the open items on the Audit Committee Recommendation "
        "Tracker through to completion (see linked actions OB-A11.1, .2, .3).",
        "Audit Committee minutes 20 February 2026; Recommendation Tracker",
        T_GOV, OWNERS["Audit Committee support"], "Medium", "2026-07-31",
        "In progress",
        "Recommendation Tracker rows moved from Pending to Responded; completion "
        "evidence for each sub-action.",
        "", "Audit Committee",
        "Parent obligation. Three sub-actions live in the Actions tab: A11.1 "
        "(exemption benchmarking), A11.2 (Table 5 clarification), A11.3 (UN "
        "PRI/UNGP legal briefing).",
        "Periodic",
    ),
    _ob(
        "OB-A12",
        "NCC must integrate transitional accounting baselines derived from new "
        "oversight standards into local audit workflows.",
        "Bill Butler named as preferred candidate for Local Audit Office Chair "
        "PSAA (8 June 2026)",
        T_AUDIT_PROC, OWNERS["Internal Audit"], "High", "2026-09-30", "In progress",
        "Alignment strategy document approved by Audit Committee referencing new "
        "LAO framework parameters.",
        "psaa.co.uk", "Audit Committee",
        "NEW IMMINENT REQUIREMENT tracking transition handovers before ultimate "
        "PSAA abolition.",
        "Periodic",
    ),

    # -----------------------------------------------------------------------
    # LGR obligations (Guide Part 7 — "list the LGR obligations")
    # -----------------------------------------------------------------------
    _ob(
        "OB-L1",
        "NCC must continue to work with other Nottinghamshire councils to define, "
        "coordinate, and implement safe day-one establishment of a new unitary "
        "authority.",
        "24 March 2026 Directions; CSIP LGR priority service improvement area",
        T_LGR, OWNERS["LGR and Policy"], "High", "", "Ongoing",
        "Joint LGR committee papers; transition programme updates to Improvement "
        "Committee; cooperation records with other councils.",
        "", "Chief Executive / Improvement Committee",
        "LGR sits under the Chief Executive and the Director of Policy.",
        "Monitoring",
    ),
    _ob(
        "OB-L2",
        "NCC must track the MHCLG consultation decision and respond to the "
        "statutory order implications for Nottinghamshire and Nottingham.",
        "MHCLG consultation for Nottinghamshire and Nottingham (from 25 March 2026)",
        T_LGR, OWNERS["LGR and Policy"], "High", "", "Ongoing",
        "Council response to consultation; record of statutory order decision; "
        "legal advice on transition implications.",
        "", "Chief Executive",
        "CRITICAL MILESTONE: when the Secretary of State issues the final Statutory "
        "Boundary Order, OB-L6 becomes live (S151 asset/liability review).",
        "Monitoring",
    ),
    _ob(
        "OB-L3",
        "NCC must work toward safe and legal day-one establishment of the new "
        "unitary authority, including governance, service continuity, and asset "
        "and liability planning.",
        "CSIP LGR priority area; MHCLG LGR implementation guidance (May 2026)",
        T_LGR, OWNERS["LGR and Policy"], "High", "2027-05-01", "Ongoing",
        "Transition programme plan; governance framework for shadow authority; "
        "service continuity planning documents.",
        "", "Chief Executive / Improvement Committee",
        "Planning horizon: shadow authority elections approximately May 2027; "
        "Vesting Day approximately 1 April 2028.",
        "Monitoring",
    ),
    _ob(
        "OB-L4",
        "The internal audit plan must cover LGR transition risks including service "
        "demerger, asset and liability transfer, and governance during the shadow "
        "authority phase.",
        "CSIP Risk Management and Internal Audit programme; seeded OB-004",
        T_LGR, OWNERS["Internal Audit"], "High", "2026-10-31", "In progress",
        "Updated Internal Audit Annual Plan with an LGR transition section; Audit "
        "Committee approval.",
        "", "Audit Committee",
        "Cross-track: also an Internal Controls obligation. Was the old OB-004.",
        "Periodic",
    ),
    _ob(
        "OB-L5",
        "NCC must review its governance, audit committee arrangements, and "
        "successor body governance in light of the English Devolution and "
        "Community Empowerment Act 2026 transparency and accountability codes.",
        "English Devolution and Community Empowerment Act 2026 (Royal Assent "
        "confirmed)",
        T_GOV, OWNERS["Legal and Governance"], "Medium", "2026-07-31",
        "In progress",
        "Formal gap analysis report to the July 2026 Audit Committee verifying the "
        "successor-body governance framework matches the 2026 Act, referencing the "
        "relevant Act sections against the current Audit Committee Terms of "
        "Reference and the proposed successor body governance model.",
        "", "Audit Committee",
        "LGR legislative track. Detailed implementation timeline firms up as "
        "statutory guidance is issued. Was the old OB-001.",
        "Periodic",
    ),
    _ob(
        "OB-L6",
        "On issue of the final Statutory Boundary Order, the Section 151 Officer "
        "must review asset and liability arrangements for any items planned for "
        "transfer to the new unitary authority.",
        "Statutory Boundary Order for the Nottingham/Nottinghamshire unitary "
        "structure (pending)",
        T_LGR, OWNERS["Section 151"], "High", "", "Not started",
        "S151 finance review of asset and liability transfer arrangements; report "
        "to Audit / Improvement Committee.",
        "", "Section 151 Officer / Audit Committee",
        "TRIGGER PENDING: this obligation only becomes live when the final "
        "Statutory Boundary Order is published (Guide Part 6). It is a formal "
        "finance review obligation, not a freeze of the asset registry — that "
        "remains the S151 Officer's decision. Set the Target Date when the order "
        "lands.",
        "Periodic",
    ),
    _ob(
        "OB-L7",
        "NCC must optimize regional demerger models to comply with newly issued "
        "national administrative transformation frameworks.",
        "Local government reorganisation: implementation guidance GOV.UK "
        "(8 June 2026)",
        T_LGR, OWNERS["LGR and Policy"], "Medium", "", "Ongoing",
        "LGR working team minutes detailing structural compliance parameters "
        "mapped against the June 2026 layout guides.",
        "www.gov.uk", "Chief Executive / Improvement Committee",
        "NEW GUIDANCE INCORPORATION: ensures technical migration alignment with "
        "central criteria.",
        "Monitoring",
    ),
]


# ---------------------------------------------------------------------------
# Actions (Guide Part 7 — OB-A11 breaks into three; Part 9 cross-track demo)
# ---------------------------------------------------------------------------
def _ac(aid, parent, action, owner, start, due, status, pct, evidence, notes):
    note = notes
    extra = s151_note_for_action(action, theme=_theme_for_parent(parent))
    if extra and extra not in note:
        note = (note + "  " + extra).strip()
    return {
        "Action ID": aid,
        "Parent Obligation ID": parent,
        "Action": action,
        "Owner": owner,
        "Start Date": start,
        "Due Date": due,
        "Status": status,
        "Percent Complete": pct,
        "Evidence Link": evidence,
        "Notes": note,
    }


def _theme_for_parent(parent_id: str) -> str:
    """Look up the theme of the parent obligation so S151 logic can fire."""
    for ob in OBLIGATIONS:
        if ob["Obligation ID"] == parent_id:
            return ob["Theme"]
    return ""


ACTIONS = [
    _ac(
        "A-001", "OB-A11",
        "Publish a benchmarking exercise comparing NCC's contract exemption rates "
        "against neighbouring Nottinghamshire authorities.",
        OWNERS["Procurement"], "", "2026-07-31", "Not started", 0, "",
        "OB-A11.1 — Contract Procedure Rules Exemption Benchmarking. Evidence: "
        "formal benchmarking appendix in the Procurement Annual Report. Target: "
        "July 2026 Audit Committee.",
    ),
    _ac(
        "A-002", "OB-A11",
        "Provide a clarification note splitting debt and investments between the "
        "General Fund and the Housing Revenue Account (HRA) in Table 5 of the "
        "Treasury Management Report.",
        OWNERS["Finance and Treasury"], "2026-04-15", "2026-06-30", "Complete", 100,
        "nottinghamcity.gov.uk",
        "OB-A11.2 — Treasury Management Table 5 Clarification. Evidence: signed "
        "addendum note or updated table in the finalised Treasury Management "
        "Strategy. Target: June 2026 Audit Committee.",
    ),
    _ac(
        "A-003", "OB-A11",
        "Provide a formal briefing note once legal advice on UN PRI (Principles "
        "for Responsible Investment) and UNGP (UN Guiding Principles) compliance "
        "frameworks is received.",
        OWNERS["Legal and Governance"], "", "2026-06-30", "Not started", 0, "",
        "OB-A11.3 — UN PRI and UNGP Legal Briefing. Evidence: distributed legal "
        "briefing note; logged in committee minutes or correspondence record. "
        "Target: June 2026 Audit Committee.",
    ),
    _ac(
        "A-004", "OB-L3",
        "Scope and procure the day-one IT systems and data migration required for "
        "the new unitary authority.",
        OWNERS["LGR and Policy"], "2026-06-01", "2027-02-28", "Not started", 0, "",
        "Demonstrates the Part 9 cross-track financial gateway: this LGR action "
        "involves procurement / IT system migration, so the S151 sign-off note is "
        "attached automatically.",
    ),
    _ac(
        "A-005", "OB-A10",
        "Prepare an Audit Committee briefing note on the LAO transition and its "
        "implications for NCC's PSAA-procured contract to 2027/28.",
        OWNERS["Internal Audit"], "", "2026-09-30", "Not started", 0, "",
        "Supports OB-A10. Note Bill Butler as preferred LAO Chair candidate (May "
        "2026).",
    ),
    _ac(
        "A-006", "OB-A12",
        "Review structural transitional reporting regulations issued by the "
        "preferred LAO Chair candidate and adjust internal audit backstop "
        "clearance milestones accordingly.",
        OWNERS["Internal Audit"], "2026-06-09", "2026-09-30", "Not started", 0, "",
        "NEW ACTION: Leverages 8 June 2026 intelligence on Bill Butler's "
        "framework metrics.",
    ),
    _ac(
        "A-007", "OB-L7",
        "Perform an internal option appraisal to cross-examine whether the newly "
        "introduced June 2026 GOV.UK reorganisation layout guidance changes "
        "boundary line migration costings.",
        OWNERS["LGR and Policy"], "2026-06-09", "2026-08-31", "Not started", 0, "",
        "NEW ACTION: Triggered by 8 June 2026 GOV.UK Implementation Guidance "
        "paper updates.",
    ),
    _ac(
        "A-008", "OB-L5",
        "Draft the formal accountability framework and code alignment overview "
        "mandated by the recent Royal Assent confirmation of the English "
        "Devolution Act.",
        OWNERS["Legal and Governance"], "2026-06-09", "2026-07-31", "Not started",
        0, "",
        "NEW ACTION: Directly links legislative confirmation of Act 2026 to the "
        "July 2026 Audit Committee agenda.",
    ),
    _ac(
        "A-009", "OB-A2",
        "Coordinate final verification review and ensure physical sign-off "
        "endorsement of the complete CSIP text block by Ministerial Envoys.",
        OWNERS["Chief Executive"], "2026-06-05", "2026-06-24", "In progress", 50,
        "",
        "NEW ACTION: Drives the immediate execution threshold for the statutory "
        "3-month target deadline.",
    ),

    # -----------------------------------------------------------------------
    # Coverage actions (2026-07-11): one executable action for each live
    # obligation that previously had none, derived via the Policy 4 action
    # translation (audit_logic.py) and hand-tuned. Standing Monitor actions
    # carry the next committee-cycle date and roll forward after each review.
    # -----------------------------------------------------------------------
    _ac(
        "A-010", "OB-A3",
        "Review financial management, savings delivery, accounts production, "
        "and capital programme improvements at the six-monthly Improvement "
        "Committee report and record the check.",
        OWNERS["Section 151"], "2026-07-11", "2026-12-31", "In progress", 0, "",
        "Standing Monitor action — six-monthly cycle; roll the due date "
        "forward after each review.",
    ),
    _ac(
        "A-011", "OB-A4",
        "Review scrutiny and decision-making improvements at each Improvement "
        "Committee report and record the check, filing Corporate Scrutiny "
        "papers and Scheme of Delegation updates as evidence.",
        OWNERS["Legal and Governance"], "2026-07-11", "2026-12-31",
        "In progress", 0, "",
        "Standing Monitor action — roll the due date forward after each review.",
    ),
    _ac(
        "A-012", "OB-A5",
        "Prepare the internal audit alignment note against Local Audit Office "
        "standards and guidance, and present progress reports at each Audit "
        "Committee.",
        OWNERS["Internal Audit"], "2026-07-11", "2026-07-31", "In progress", 0,
        "",
        "First deliverable under the standing CSIP internal-audit obligation; "
        "target the July 2026 Audit Committee.",
    ),
    _ac(
        "A-013", "OB-A6",
        "Record Ministerial Envoy attendance and the council's responses to "
        "Envoy recommendations at each Improvement Committee meeting.",
        OWNERS["Chief Executive"], "2026-07-11", "2026-09-30", "In progress", 0,
        "",
        "Standing Engage action — evidence accrues each committee cycle.",
    ),
    _ac(
        "A-014", "OB-A7",
        "Produce the management response document to each recommendation in "
        "the external auditor's Annual Report (ISA 260) and secure the Audit "
        "Committee acceptance minute.",
        OWNERS["Finance and Treasury"], "2026-07-11", "2026-07-31",
        "In progress", 0, "",
        "Delivers OB-A7 at the July 2026 Audit Committee cycle.",
    ),
    _ac(
        "A-015", "OB-A8",
        "Produce and publish the 2024/25 Statement of Accounts with the "
        "auditor's opinion (noting any disclaimer), and link the specific "
        "year's document on the accounts page as evidence.",
        OWNERS["Section 151"], "2026-07-11", "2026-09-30", "In progress", 0, "",
        "Recurring Produce action under the enduring Accounts and Audit "
        "Regulations duty — repeats each reporting year.",
    ),
    _ac(
        "A-016", "OB-A9",
        "Secure Audit Committee approval of the published draft Annual "
        "Governance Statement 2024/25 and link the approval minute as "
        "evidence.",
        OWNERS["Legal and Governance"], "2026-07-11", "2026-07-31",
        "In progress", 50, "",
        "Draft AGS confirmed published online; remaining step is the approval "
        "minute at the July 2026 Audit Committee.",
    ),
    _ac(
        "A-017", "OB-L1",
        "File joint LGR committee papers, transition programme updates to the "
        "Improvement Committee, and cooperation records with the other "
        "Nottinghamshire councils each committee cycle.",
        OWNERS["LGR and Policy"], "2026-07-11", "2026-09-30", "In progress", 0,
        "",
        "Standing Engage action for the joint LGR programme.",
    ),
    _ac(
        "A-018", "OB-L2",
        "Monitor MHCLG announcements for the LGR consultation decision and "
        "the Statutory Boundary Order; on publication, set OB-L6's target "
        "date and notify the Section 151 Officer immediately.",
        OWNERS["LGR and Policy"], "2026-07-11", "2026-08-31", "In progress", 0,
        "",
        "The Order is expected summer 2026 and triggers OB-L6 (Guide Part 12).",
    ),
    _ac(
        "A-019", "OB-L4",
        "Update the Internal Audit Annual Plan with an LGR transition risk "
        "section (service demerger, asset and liability transfer, shadow "
        "authority governance) and secure Audit Committee approval.",
        OWNERS["Internal Audit"], "2026-07-11", "2026-10-31", "Not started", 0,
        "",
        "Delivers OB-L4; cross-track with Internal Controls.",
    ),
    _ac(
        "A-020", "OB-L6",
        "On issue of the final Statutory Boundary Order, complete the Section "
        "151 review of asset and liability transfer arrangements and report "
        "to the Audit / Improvement Committee.",
        OWNERS["Section 151"], "", "", "Not started", 0, "",
        "TRIGGER PENDING: dates are set when the Statutory Boundary Order is "
        "published (see A-018).",
    ),
]
