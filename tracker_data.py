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

LAST_UPDATED = "2026-08-04"

# Column order for the Obligations sheet. "Obligation Level" is appended last so
# the existing data-validation ranges on Risk (F) and Status (H) are undisturbed.
OBLIGATION_COLUMNS = [
    "Obligation ID", "Obligation", "Source / Trigger", "Theme", "Owner",
    "Risk Rating", "Target Date", "Status", "Evidence Required",
    "Evidence Location", "Sign Off By", "Last Updated", "Notes",
    "Obligation Level",
    # Appended last, after "Obligation Level", so the reading order of the sheet
    # is unchanged. DERIVED from ACTIONS by populate_tracker.py — never type into
    # it, the next rebuild overwrites it.
    "Linked Actions",
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
AUDIT_CTTE_PAGE = "https://committee.nottinghamcity.gov.uk/ieListMeetings.aspx?CommitteeId=145"
IMP_CTTE_PAGE = "https://committee.nottinghamcity.gov.uk/ieListMeetings.aspx?CommitteeId=1175"
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
        "https://www.gov.uk/government/collections/statutory-intervention-nottingham-city-council-minded-to-decision",
        "Improvement Committee / Ministerial Envoys",
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
        IMP_CTTE_PAGE, "Improvement Committee",
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
        IMP_CTTE_PAGE, "Improvement Committee",
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
        AUDIT_CTTE_PAGE, "Audit Committee",
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
        "https://www.gov.uk/government/collections/statutory-intervention-nottingham-city-council-minded-to-decision",
        "Chief Executive / Improvement Committee",
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
        AUDIT_CTTE_PAGE, "Audit Committee",
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
        "https://assets.publishing.service.gov.uk/media/6926f871345e31ab14ecf524/"
        "Local_Audit_Transition_Plan.pdf  (MHCLG Local Audit Transition Plan, "
        "Nov 2025 — Annex A carries the milestone timeline);  "
        "https://www.gov.uk/government/organisations/local-audit-office",
        "Audit Committee",
        "CORRECTED 4 Aug 2026 against the MHCLG Local Audit Transition Plan "
        "(Nov 2025), which states PSAA's contracts with audit firms 'have "
        "recently been extended until 2030' — the tracker previously said "
        "2027/28, understating the horizon by two years. Auditor appointment "
        "and contracting duties transfer to the LAO in Spring 2027, with PSAA "
        "staff and the existing contracts novating across. Bill Butler is "
        "CONFIRMED as LAO Chair from 1 July 2026 (previously recorded as "
        "preferred candidate). Was the old OB-002.",
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
        "https://committee.nottinghamcity.gov.uk/ieListMeetings.aspx?CommitteeId=145",
        "Audit Committee",
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
        "https://www.gov.uk/government/publications/local-audit-office-chair-appointment",
        "Audit Committee",
        "NEW IMMINENT REQUIREMENT tracking transition handovers before ultimate "
        "PSAA abolition.",
        "Periodic",
    ),
    _ob(
        "OB-A13",
        "NCC must have an audit committee and arrange for it to exercise the four "
        "statutory functions in section 33A of the Local Audit and Accountability "
        "Act 2014: reviewing and scrutinising financial affairs; reviewing and "
        "assessing risk management, internal control and governance arrangements; "
        "reviewing and assessing economy, efficiency and effectiveness of resource "
        "use; and making reports and recommendations to the authority.",
        "Section 94, English Devolution and Community Empowerment Act 2026 "
        "(inserting s.33A into the Local Audit and Accountability Act 2014), "
        "commenced for Category 1 authorities from 15 July 2026 by SI 2026/812; "
        "MHCLG letter to Section 151 Officers, 31 July 2026",
        T_GOV, OWNERS["Section 151"], "High", "2026-09-25", "In progress",
        "Audit Committee terms of reference mapped against the four s.33A "
        "functions; constitution showing the committee is established; record of "
        "independent member appointment once the membership regulations are in "
        "force.",
        # The full chain, in the order it happened: the duty, the instrument
        # that switched it on, and the letter that told us about it.
        "https://www.legislation.gov.uk/ukpga/2014/2/section/33A  (the duty);  "
        "https://www.legislation.gov.uk/uksi/2026/812/made  (SI 2026/812, "
        "commenced it 15 July 2026);  "
        "evidence/2026-07-31-MHCLG-audit-committee-requirement.pdf  (MHCLG "
        "letter to S151 Officers — not published on GOV.UK, filed alongside "
        "this tracker)",
        "Audit Committee",
        "STATUTORY DUTY IN FORCE since 15 July 2026. MHCLG expects most "
        "authorities already comply and asks to be told of any difficulty "
        "(localaudit@communities.gov.uk). The independent member requirement is "
        "NOT yet in force — s.94 provides for further regulations on membership, "
        "appointments and allowances, to be followed by statutory guidance. "
        "MHCLG encourages authorities without an independent member to begin "
        "recruitment now so they are ready when the regulations commence.",
        "Enduring",
    ),
    _ob(
        "OB-A14",
        "NCC must onboard the newly appointed Political Envoy and provide the "
        "briefings and access needed for the envoy to discharge the advisory role "
        "under the de-escalated intervention arrangements.",
        "MHCLG appointment letter to Sir Stephen Houghton CBE, 15 July 2026 "
        "(James Blythe, Deputy Director, Local Government Stewardship and "
        "Interventions), appointing him Political Envoy for the purposes of the "
        "Directions made 24 March 2026 under section 15(5) of the Local "
        "Government Act 1999",
        T_GOV, OWNERS["Chief Executive"], "High", "2026-09-24", "Not started",
        "Schedule of induction and advisory sessions; reporting matrix defining "
        "the advisory boundary; budget provision for envoy fees; records "
        "submitted to the Continuous Improvement Committee.",
        "https://www.gov.uk/government/publications/nottingham-city-council-"
        "ministerial-envoy-appointment-letter-15-july-2026",
        "Chief Executive / Continuous Improvement Committee",
        "Sir Stephen Houghton CBE joins Sharon Kemp, who is Lead Envoy; the "
        "Envoys may act jointly or severally and are accountable to the "
        "Secretary of State. The letter asks them to provide support 'in an "
        "advisory and mentoring capacity', particularly on the Best Value themes "
        "of Continuous Improvement and Service Delivery. TWO POINTS THE "
        "APPOINTMENT LETTER PUTS ON NCC: (1) fees of GBP 800 per day up to 75 "
        "days a year, plus reasonable expenses, are the Authority's "
        "responsibility to meet — a liability of up to GBP 60,000 a year per "
        "envoy that needs budget provision; (2) the Secretary of State has asked "
        "the Envoys to report within the first six months of the intervention, "
        "which runs from the 24 March 2026 Directions, hence the target date. "
        "Complements OB-A1, which covers Envoy membership of the Continuous "
        "Improvement Committee.",
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
        "https://www.gov.uk/government/collections/nottinghamshire-and-nottingham-local-government-reorganisation",
        "Chief Executive / Improvement Committee",
        "See also OB-L8 on the MHCLG Devolution Framework Explainers. "
        "LGR sits under the Chief Executive and the Director of Policy. MHCLG "
        "issued non-statutory staffing issues guidance on 16 July 2026 covering "
        "appointment and transfer of employees to the new single-tier councils; "
        "gap analysis and staff consultation tracked as A-025 and A-026.",
        "Monitoring",
    ),
    _ob(
        "OB-L2",
        "NCC must track the MHCLG consultation decision and respond to the "
        "statutory order implications for Nottinghamshire and Nottingham.",
        "Secretary of State decision letter to Nottinghamshire and Nottingham "
        "council leaders, 16 July 2026; HCWS286 written ministerial statement",
        T_LGR, OWNERS["LGR and Policy"], "High", "", "Ongoing",
        "Council response to consultation; record of statutory order decision; "
        "legal advice on transition implications.",
        "https://assets.publishing.service.gov.uk/media/6a58d3105ca06bf11ccb42f9/"
        "Local_government_reorganisation_-_decision_letter_to_Nottinghamshire_and_"
        "Nottingham_council_leaders.pdf",
        "Chief Executive",
        "CONSULTATION DECISION MADE 16 July 2026: Secretary of State confirmed the "
        "two-unitary 'modified' option — 'Southwest' (Nottingham City plus wards "
        "from Broxtowe, Gedling, Rushcliffe) and 'North and East' (Ashfield, "
        "Bassetlaw, Mansfield, Newark and Sherwood plus remaining wards). Shadow "
        "elections confirmed May 2027 (replacing scheduled local elections); "
        "implementation targeted April 2028. Ministerial Envoy named as Sharon "
        "Kemp. This is NOT yet OB-L6's trigger: the Structural Changes Order "
        "(the statutory instrument itself) is still subject to Parliamentary "
        "approval — officials to write separately with the implementation "
        "timeline. OB-L6 becomes live only when that Order is made.",
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
        "https://www.gov.uk/government/collections/nottinghamshire-and-nottingham-local-government-reorganisation",
        "Chief Executive / Improvement Committee",
        "Planning horizon: shadow authority elections CONFIRMED May 2027 (SoS "
        "decision letter 16 July 2026, replacing scheduled local elections); "
        "Vesting Day targeted 1 April 2028.",
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
        "https://www.gov.uk/government/publications/local-government-reorganisation-implementation-guidance",
        "Chief Executive / Improvement Committee",
        "NEW GUIDANCE INCORPORATION: ensures technical migration alignment with "
        "central criteria.",
        "Monitoring",
    ),
    _ob(
        "OB-L8",
        "NCC must track the MHCLG Devolution Framework Explainers and assess how "
        "the statutory functions they set out for Strategic Authorities shape the "
        "operating model of the new unitary authorities.",
        "English Devolution and Community Empowerment Act 2026: Devolution "
        "Framework Explainers, MHCLG (last updated 8 June 2026)",
        T_LGR, OWNERS["LGR and Policy"], "Medium", "2026-10-31", "Not started",
        "Gap analysis mapping NCC service lines against the Strategic Authority "
        "functions in the Explainers, reported to the LGR programme board.",
        "https://www.gov.uk/government/publications/english-devolution-and-"
        "community-empowerment-bill-devolution-framework-explainers",
        "Chief Executive / Improvement Committee",
        "SCOPE NOTE: the Explainers set out the statutory functions of STRATEGIC "
        "AUTHORITIES. NCC is not a Strategic Authority — EMCCA is — so these are "
        "not a duty on NCC directly. They matter because the new unitaries will "
        "be constituent councils of EMCCA, so the Explainers define the boundary "
        "between what EMCCA holds and what the unitaries hold. Monitoring, not "
        "compliance.",
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
        "implications for NCC's PSAA-procured audit contract, which now runs to "
        "2030.",
        OWNERS["Internal Audit"], "", "2026-09-30", "Not started", 0,
        "https://assets.publishing.service.gov.uk/media/6926f871345e31ab14ecf524/"
        "Local_Audit_Transition_Plan.pdf",
        "Supports OB-A10. Milestones from the MHCLG Local Audit Transition Plan "
        "(Nov 2025), Annex A: LAO legally established Autumn 2026; auditor "
        "appointment and contracting duties, PSAA staff and the existing "
        "contracts transfer to the LAO Spring 2027. Bill Butler CONFIRMED as "
        "LAO Chair from 1 July 2026 (was recorded as preferred candidate).",
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
        OWNERS["LGR and Policy"], "2026-07-11", "2026-08-31", "In progress", 40,
        "https://assets.publishing.service.gov.uk/media/6a58d3105ca06bf11ccb42f9/"
        "Local_government_reorganisation_-_decision_letter_to_Nottinghamshire_and_"
        "Nottingham_council_leaders.pdf",
        "Consultation decision half done: SoS confirmed the two-unitary option "
        "on 16 July 2026 (Southwest / North and East, elections May 2027). "
        "Still monitoring for the Structural Changes Order itself, which "
        "officials said would follow separately and remains subject to "
        "Parliamentary approval — that is what triggers OB-L6 (Guide Part 12).",
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
    _ac(
        "A-021", "OB-L1",
        "Participate in joint implementation governance.",
        OWNERS["LGR and Policy"], "2026-07-16", "", "Not started", 0, "",
        "Joint programme governance structure to be agreed and implemented.",
    ),
    _ac(
        "A-022", "OB-L1",
        "Work with Nottinghamshire authorities on transition arrangements.",
        OWNERS["LGR and Policy"], "2026-07-16", "", "Not started", 0, "",
        "Joint programme to be set out and ownership and accountabilities to be "
        "defined and progress monitored.",
    ),
    _ac(
        "A-023", "OB-L1",
        "Support development of new operating models, staffing arrangements and "
        "service integration plans.",
        OWNERS["HR and EDI"], "2026-07-16", "", "Not started", 0, "",
        "Gather existing establishment and operating model details. Support "
        "planning for new establishment and operating models. Ensure timely "
        "onboarding processes.",
    ),
    _ac(
        "A-025", "OB-L1",
        "Review the MHCLG local government reorganisation staffing issues "
        "guidance (16 July 2026) and complete a gap analysis against current "
        "demerger and staffing transition assumptions.",
        OWNERS["HR and EDI"], "2026-08-04", "2026-09-30", "Not started", 0,
        "https://www.gov.uk/government/publications/local-government-reorganisation-staffing-issues-guidance",
        "Checks the emerging operating model against central expectations on "
        "appointment and transfer of staff to the new single-tier councils. "
        "Feeds A-023.",
    ),
    _ac(
        "A-026", "OB-L1",
        "Use the MHCLG staffing guidance overview in joint-council consultation "
        "with trade unions and staff on day-one staffing arrangements.",
        OWNERS["HR and EDI"], "2026-08-04", "2026-10-31", "Not started", 0,
        "https://www.gov.uk/government/publications/local-government-reorganisation-staffing-issues-guidance",
        "The 3-page overview published alongside the full guidance is the "
        "version intended for staff and union consultation.",
    ),
    _ac(
        "A-027", "OB-A13",
        "Map the Audit Committee's terms of reference against the four statutory "
        "functions in s.33A of the Local Audit and Accountability Act 2014 and "
        "report the result to the Audit Committee, identifying any constitutional "
        "amendment needed.",
        OWNERS["Section 151"], "2026-08-04", "2026-09-25", "Not started", 0,
        "https://www.legislation.gov.uk/ukpga/2026/23/section/94/enacted",
        "Duty in force since 15 July 2026. MHCLG expects most authorities already "
        "comply, so this confirms compliance rather than builds it — and gives a "
        "documented basis for telling MHCLG if any difficulty is foreseen. "
        "Target: 25 September 2026 Audit Committee.",
    ),
    _ac(
        "A-028", "OB-A13",
        "Launch recruitment for an independent member of the Audit Committee, "
        "including a public advertisement and role profile, ahead of the "
        "membership regulations coming into force.",
        OWNERS["Legal and Governance"], "2026-08-04", "2026-10-15", "Not started", 0,
        "",
        "Evidence: live public advertisement on the NCC jobs portal, role "
        "profile, and the appointment route through to committee. MHCLG "
        "encourages early recruitment — the independent member requirement is "
        "not yet in force and will be commenced by regulations made under s.94, "
        "so this is preparation rather than a duty in force. Starting now avoids "
        "a compliance gap on commencement.",
    ),
    _ac(
        "A-029", "OB-A13",
        "Monitor for the s.94 regulations on audit committee membership, "
        "appointments and allowances, and the statutory guidance that follows "
        "them; on publication, reassess the terms of reference and the "
        "independent member appointment against the final requirements.",
        OWNERS["Section 151"], "2026-08-04", "", "Not started", 0, "",
        "TRIGGER PENDING: dates are set when the membership regulations are laid. "
        "Government has said this will happen 'when parliamentary time allows', "
        "so there is no announced date to work to (Guide Part 12).",
    ),
    _ac(
        "A-030", "OB-A14",
        "Coordinate the initial political and executive induction sessions with "
        "Political Envoy Sir Stephen Houghton CBE.",
        OWNERS["Chief Executive"], "2026-08-04", "2026-09-15", "Not started", 0, "",
        "Evidence: schedule of initial advisory sessions submitted to the "
        "Continuous Improvement Committee.",
    ),
    _ac(
        "A-031", "OB-A14",
        "Update the executive reporting matrix to define the advisory and "
        "mentoring boundaries of the Envoy role, covering both the Lead Envoy "
        "and the Political Envoy and their power to act jointly or severally.",
        OWNERS["Chief Executive"], "2026-08-04", "2026-09-30", "Not started", 0,
        "https://www.gov.uk/government/publications/nottingham-city-council-"
        "letter-to-council-leader-15-july-2026",
        "Evidence: framework document signed off by the Leader (Cllr Neghat "
        "Khan) and Executive Panel. Records the distinction between the former "
        "Commissioner powers and the current advisory and mentoring role.",
    ),
    _ac(
        "A-032", "OB-A14",
        "Confirm budget provision for Political Envoy fees and expenses, and put "
        "in place the approval route for exceeding the 75-day annual cap.",
        OWNERS["Section 151"], "2026-08-04", "2026-09-30", "Not started", 0, "",
        "The appointment letter makes envoy costs the Authority's "
        "responsibility: GBP 800 per day, maximum 75 days a year, plus "
        "reasonable expenses at senior officer rates. The cap cannot be exceeded "
        "without prior Secretary of State approval, so the route needs to exist "
        "before it is needed.",
    ),
    _ac(
        "A-033", "OB-L8",
        "Map NCC's single-tier operational workflows against the Strategic "
        "Authority functions set out in the MHCLG Devolution Framework "
        "Explainers, identifying which service lines sit with EMCCA and which "
        "with the new unitary authorities.",
        OWNERS["LGR and Policy"], "2026-08-04", "2026-10-31", "Not started", 0,
        "https://www.gov.uk/government/publications/english-devolution-and-"
        "community-empowerment-bill-devolution-framework-explainers",
        "Evidence: structural gap analysis signed off by the Director of Policy "
        "and reported to the LGR programme board. Establishes the EMCCA / "
        "unitary boundary before day-one service allocation is fixed.",
    ),
    _ac(
        "A-034", "OB-A7",
        "Confirm whether NCC gave MHCLG permission for its auditor to share the "
        "Auditor's Annual Report, the ISA 260 and the audit capacity assessment "
        "with the Department, and resolve the position with MHCLG if it did not.",
        OWNERS["Section 151"], "2026-08-04", "2026-09-25", "Not started", 0,
        "https://assets.publishing.service.gov.uk/media/692992e6a245b0985f034280/"
        "Ministerial_letter_to_local_bodies.pdf",
        "RETROSPECTIVE CHECK — BOTH DEADLINES HAVE PASSED. The Minister of State "
        "wrote to Chief Executives, CFOs and Leaders on 27 November 2025 asking "
        "for the AAR and ISA 260 by 31 March 2026 and an auditor capacity "
        "assessment by end July 2026. The letter says that where permission is "
        "not given, MHCLG officials will follow up directly. There is no record "
        "either way in the tracker, so the answer needs establishing rather than "
        "assuming. Evidence: the permission response to the audit firm, or "
        "correspondence with MHCLG.",
    ),
    _ac(
        "A-035", "OB-A8",
        "Agree the build-back trajectory with the external auditor for clearing "
        "any backstop-related disclaimed opinions, working to the 30 November "
        "2028 backstop, and report the trajectory to the Audit Committee.",
        OWNERS["Section 151"], "2026-08-04", "2026-11-27", "Not started", 0,
        "https://assets.publishing.service.gov.uk/media/692992e6a245b0985f034280/"
        "Ministerial_letter_to_local_bodies.pdf",
        "The build-back programme aims to clear backstop-related disclaimers by "
        "the end of 2027/28, for which the backstop date is 30 November 2028. "
        "Government has said progress is slower than hoped and that NO FURTHER "
        "build-back grant was paid in 2025/26, with the funding model reviewed "
        "in summer and autumn 2026 — so the cost of this sits with NCC unless "
        "that review changes it. The letter also stresses that authorities must "
        "adequately resource their finance functions to supply audit evidence.",
    ),
]
