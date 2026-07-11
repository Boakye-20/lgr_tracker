"""
Shared logic used by more than one script.

Keeping the scoring and theming rules in one place means the intelligence
feed and any future report use exactly the same definitions.
"""

from __future__ import annotations

import hashlib
from datetime import datetime


def make_hash(url: str, title: str) -> str:
    """A stable fingerprint for an item, used to avoid storing duplicates."""
    return hashlib.md5(f"{url}|{title}".encode("utf-8")).hexdigest()


def to_iso_date(raw: str | None) -> str:
    """Turn whatever date format a source gives us into YYYY-MM-DD, or blank."""
    if not raw:
        return ""
    raw = str(raw).strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %Y",
    ):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def is_excluded(title: str, rules: dict) -> bool:
    """
    Hard pre-filter: drop items entirely before they are scored or stored.
    Drops devolved-nation content, LGR stories naming other counties, and
    items matching exclude_keywords (e.g. HMRC tax tribunal cases that match
    "commissioner" in its legal sense rather than the intervention sense).
    """
    lowered = title.lower()
    if any(nation in lowered for nation in rules.get("exclude_nations", [])):
        return True
    if any(kw in lowered for kw in rules.get("exclude_keywords", [])):
        return True
    if "local government reorganisation" in lowered and any(
        council in lowered for council in rules.get("exclude_lgr_councils", [])
    ):
        return True
    return False


def classify_materiality(text: str, rules: dict) -> tuple[str, str]:
    """
    Decide whether an item is material to NCC by checking which keyword
    groups appear in the text, then applying a simple rule:

        Two or more groups matched  ->  Yes
        Exactly one group matched   ->  Unclear
        No groups matched           ->  No

    Returns (verdict, matched_groups_string) so the caller can write both
    to the spreadsheet. Examples:

        ("Yes",     "Local, Audit")
        ("Unclear", "Transition")
        ("No",      "")

    All keywords live in sources.json under materiality_rules so you can
    tune them without touching this code.
    """
    lowered = text.lower()
    matched = []

    if any(k in lowered for k in rules.get("local_keywords", [])):
        matched.append("Local")
    if any(k in lowered for k in rules.get("intervention_keywords", [])):
        matched.append("Intervention")
    if any(k in lowered for k in rules.get("audit_keywords", [])):
        matched.append("Audit")
    if any(k in lowered for k in rules.get("transition_keywords", [])):
        matched.append("Transition")

    if len(matched) >= 2:
        verdict = "Yes"
    elif len(matched) == 1:
        verdict = "Unclear"
    else:
        verdict = "No"

    return verdict, ", ".join(matched)


def assign_themes(text: str, theme_keywords: dict) -> str:
    """
    Return every theme whose keywords appear in the text as a
    semicolon-separated string, e.g. 'LGR Transition; Governance'.
    """
    lowered = text.lower()
    matched = [
        theme
        for theme, keywords in theme_keywords.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    return "; ".join(matched) if matched else "Other"


# ===========================================================================
# THE POLICY SECTION — role and obligation enforcement
# (Tracker Guide v2, Parts 1, 4, 5, 9, 10, 13)
# ---------------------------------------------------------------------------
# Everything below is the "judgement" half of the system written down as rules
# so the tracker can be checked automatically. It is organised as six policies,
# built around one idea: an obligation is only under control once it has been
# translated into at least one specific, executable compliance action.
#
#   Policy 1 — Ownership: only Part 13 contacts / council bodies own things.
#   Policy 2 — Obligation levels: Enduring / Periodic / Monitoring (Part 1),
#              each with a stated expectation of what action satisfies it.
#   Policy 3 — Obligation triggers: "must / required / shall" separates a real
#              obligation from monitoring noise (Parts 2 and 10).
#   Policy 4 — Action translation: how an obligation becomes an executable
#              action (the five action archetypes and derivation rules).
#   Policy 5 — Financial gateway: LGR actions that spend money need Section
#              151 sign-off (Part 9).
#   Policy 6 — Validation: the maturity checklist for rows (Parts 5 and 10)
#              and the action-coverage check across the register.
# ===========================================================================

# --- Policy 1: Ownership — Key Contacts and Owners Reference (Part 13) -----
# Canonical owners. The key is the area; the value is how the name should read
# in the Owner column. KNOWN_OWNER_TOKENS lets validate_obligation() recognise
# an owner however it was typed (full name, surname, or initials).
OWNERS = {
    "Finance and Treasury": "Gareth Robinson (Director of Finance)",
    "Section 151": "Stuart Fair (Corporate Director for Finance and Resources, S151)",
    "Internal Audit": "Lynne Dowdican (Head of Internal Audit)",
    "Audit Committee support": "Kate Morris (Scrutiny and Audit Support Officer)",
    "LGR and Policy": "James Rhodes (Director of Policy, Performance and Communications)",
    "Chief Executive": "Sajeeda Rose (Chief Executive)",
    "Legal and Governance": "Beth Brown (Strategic Director of Legal and Governance)",
    "Risk": "D Bowring (Risk)",
    "Procurement": "A Spice / D Cafferty (Procurement)",
}

# Recognisable tokens for each real person, used by validate_obligation() to
# decide whether an Owner cell names someone the council actually has. A team
# name ("Improvement Committee", "Audit Committee") is also accepted as a body.
KNOWN_OWNER_TOKENS = {
    "robinson", "g robinson", "gareth robinson",
    "fair", "s fair", "stuart fair",
    "dowdican", "l dowdican", "lynne dowdican",
    "morris", "k morris", "kate morris",
    "rhodes", "j rhodes", "james rhodes",
    "rose", "sajeeda rose",
    "brown", "b brown", "beth brown",
    "bowring", "d bowring",
    "spice", "a spice", "cafferty", "d cafferty",
}

KNOWN_BODY_TOKENS = {
    "improvement committee", "continuous improvement committee",
    "audit committee", "city council", "ministerial envoy", "ministerial envoys",
    "scrutiny committee", "ncc",
}


def canonical_owner(area: str) -> str:
    """Look up the agreed Owner string for an area name from Part 13."""
    return OWNERS.get(area, "")


def is_known_owner(owner: str | None) -> bool:
    """
    True if the Owner cell names a recognised officer (Part 13) or a council
    body. Used to stop obligations carrying an unverifiable owner.
    """
    if not owner or not str(owner).strip():
        return False
    lowered = str(owner).lower()
    if any(token in lowered for token in KNOWN_OWNER_TOKENS):
        return True
    if any(body in lowered for body in KNOWN_BODY_TOKENS):
        return True
    return False


# --- Policy 2: the three obligation levels (Part 1) -------------------------

# What kind of action satisfies each obligation level. Used by the coverage
# check and printed by populate_tracker.py so the expectation is visible next
# to the warning, not buried in the guide.
LEVEL_ACTION_POLICY = {
    "Enduring": (
        "a recurring Produce action each reporting cycle — the statutory duty "
        "itself never closes"
    ),
    "Statutory": (
        "a dated Produce action plus an Approve action, both completed before "
        "the statutory deadline"
    ),
    "Periodic": (
        "at least one dated action that delivers the evidence, after which "
        "the obligation closes"
    ),
    "Monitoring": (
        "a standing Monitor action reviewed each committee cycle — it never "
        "closes, but each review must be recorded"
    ),
}

ENDURING_SIGNALS = (
    "local government act", "accounts and audit regulations", "best value",
    "statutory duty", "must have", "duty to", "shall", "code of practice",
)
MONITORING_SIGNALS = (
    "monitor", "track", "keep watching", "watch", "ongoing", "as they develop",
    "timetable", "transition", "horizon",
)
PERIODIC_SIGNALS = (
    "within three months", "by ", "prepare and agree", "respond to", "publish",
    "produce", "endorse", "approve", "deadline", "committee cycle",
)


def classify_obligation_level(text: str, status: str | None = None) -> str:
    """
    Sort an obligation into one of the Part 1 levels:

        Enduring   - flows from legislation / standing statutory duty
        Periodic   - a one-off deliverable with a date or event
        Monitoring - something the council must keep watching; never closes

    Heuristic, deliberately simple, and overridable by the human in the sheet.
    Status is used as a tie-breaker: an 'Ongoing' status leans Monitoring.
    """
    lowered = (text or "").lower()
    if any(sig in lowered for sig in ENDURING_SIGNALS):
        return "Enduring"
    if (status or "").strip().lower() == "ongoing":
        return "Monitoring"
    if any(sig in lowered for sig in MONITORING_SIGNALS) and not any(
        sig in lowered for sig in ("within three months", "deadline", "by 2")
    ):
        return "Monitoring"
    if any(sig in lowered for sig in PERIODIC_SIGNALS):
        return "Periodic"
    return "Monitoring"


# --- Policy 3: obligation triggers (Parts 2 & 10) ---------------------------
OBLIGATION_TRIGGER_WORDS = (
    "must", "required", "shall", "directions require",
    "the authority is required to", "is required to",
)


def has_obligation_trigger(text: str) -> bool:
    """
    True if the text contains a real obligation trigger word. Mirrors the
    first row of the Part 10 'good obligation vs noise' checklist: no trigger
    word usually means monitoring or context, not an obligation.
    """
    lowered = (text or "").lower()
    return any(word in lowered for word in OBLIGATION_TRIGGER_WORDS)


# --- Policy 4: action translation — obligations into executable actions ----
# The categorisation model. Every obligation is translated into one of five
# action archetypes, chosen by the leading verbs in its text. Each archetype
# says what "done" looks like, so the derived action is executable: it has a
# verb, an owner, a date, and the evidence that closes it.
#
# Precedence matters: an obligation that both "publishes" and "monitors" is a
# Produce obligation — the concrete deliverable always wins over the watching.
ACTION_TYPES = {
    "Produce": {
        "verbs": (
            "produce", "publish", "prepare", "draft", "issue", "submit",
            "respond to", "provide", "establish",
        ),
        "template": "Produce the deliverable and file the evidence: {evidence}",
    },
    "Approve": {
        "verbs": ("agree", "endorse", "approve", "sign off", "sign-off", "adopt"),
        "template": "Secure the approval and minute it: {evidence}",
    },
    "Assess": {
        "verbs": (
            "review", "assess", "analyse", "benchmark", "appraise",
            "gap analysis", "understand", "plan for", "integrate", "optimize",
            "optimise",
        ),
        "template": "Complete the assessment and report the findings: {evidence}",
    },
    "Engage": {
        "verbs": (
            "cooperate", "work with", "coordinate", "brief", "consult",
            "liaise", "work toward",
        ),
        "template": "Carry out the engagement and record it: {evidence}",
    },
    "Monitor": {
        "verbs": ("monitor", "track", "keep watching", "watch", "embed"),
        "template": (
            "Review at each committee cycle and record the check: {evidence}"
        ),
    },
}

ACTION_TYPE_ORDER = ("Produce", "Approve", "Assess", "Engage", "Monitor")


def classify_action_type(text: str) -> str:
    """
    Sort an obligation (or action) text into one of the five archetypes by
    verb, in precedence order. Defaults to Assess: if we cannot tell what the
    deliverable is, the first executable step is always to scope the work.
    """
    lowered = (text or "").lower()
    for name in ACTION_TYPE_ORDER:
        if any(verb in lowered for verb in ACTION_TYPES[name]["verbs"]):
            return name
    return "Assess"


def derive_compliance_action(ob: dict) -> dict:
    """
    Translate one Obligations row into a concrete, executable action stub for
    the Actions tab: a verb-led statement built from the obligation's own
    Evidence Required, the same owner, the target date as the due date, and
    the Section 151 note attached automatically where the Part 9 gateway
    applies. The human still reviews and refines it — this guarantees the
    action is specific, owned, and dated rather than a restated obligation.
    """
    text = ob.get("Obligation") or ""
    evidence = (ob.get("Evidence Required") or "").strip() \
        or "the evidence described on the obligation row"
    atype = classify_action_type(text)
    level = (ob.get("Obligation Level") or "").strip()
    note = f"Derived from {ob.get('Obligation ID', '?')} ({atype} action)."
    if level in LEVEL_ACTION_POLICY:
        note += f" Level policy: {LEVEL_ACTION_POLICY[level]}."
    s151 = s151_note_for_action(text, theme=ob.get("Theme"))
    if s151:
        note += f"  {s151}"
    return {
        "Parent Obligation ID": ob.get("Obligation ID", ""),
        "Action": ACTION_TYPES[atype]["template"].format(evidence=evidence),
        "Action Type": atype,
        "Owner": ob.get("Owner", ""),
        "Due Date": ob.get("Target Date") or "",
        "Status": "Not started",
        "Percent Complete": 0,
        "Evidence Link": "",
        "Notes": note,
    }


def action_coverage_warnings(obligations: list[dict], actions: list[dict]) -> list[str]:
    """
    The register-level half of the Part 5 maturity bar: every obligation that
    is not Complete must be covered by at least one row in the Actions tab.
    For each uncovered obligation, the warning states what its level expects
    and quotes the derived action so fixing it is one copy-paste, not a
    research task. Returns plain-English warnings (empty list = full coverage).
    """
    covered = {
        str(a.get("Parent Obligation ID") or "").strip()
        for a in actions
    }
    warnings: list[str] = []
    for ob in obligations:
        status = (ob.get("Status") or "").strip()
        oid = str(ob.get("Obligation ID") or "").strip()
        if not oid or status == "Complete":
            continue
        if oid in covered:
            continue
        suggestion = derive_compliance_action(ob)
        level = (ob.get("Obligation Level") or "").strip() or "Periodic"
        expects = LEVEL_ACTION_POLICY.get(level, LEVEL_ACTION_POLICY["Periodic"])
        warnings.append(
            f"{oid}: no action row in the Actions tab. Level '{level}' expects "
            f"{expects}. Suggested {suggestion['Action Type']} action: "
            f"\"{suggestion['Action']}\""
        )
    return warnings


# --- Policy 5: cross-track Section 151 financial gateway (Part 9) ----------
S151_SIGNOFF_KEYWORDS = (
    "procure", "procurement", "contract", "vendor", "software upgrade",
    "capital", "it system migration", "system migration", "purchase",
)

S151_SIGNOFF_NOTE = (
    "⚠️ Procurement/capital action: requires Section 151 sign-off under "
    "current spending controls before proceeding. Confirm with Stuart Fair or "
    "Gareth Robinson."
)


def needs_s151_signoff(text: str) -> bool:
    """
    Part 9: an LGR transition action that spends money (procure, contract,
    vendor, software upgrade, capital, IT system migration) hits the financial
    gateway and must carry the S151 sign-off note. Returns True if it does.
    """
    lowered = (text or "").lower()
    return any(kw in lowered for kw in S151_SIGNOFF_KEYWORDS)


def s151_note_for_action(action_text: str, theme: str | None = None) -> str:
    """
    Return the S151 sign-off note if this action is LGR-themed AND involves
    spending, else an empty string. Used when adding rows to the Actions tab so
    the financial control point is recorded automatically (Part 9).
    """
    is_lgr = "lgr" in (theme or "").lower() or "reorgan" in (theme or "").lower()
    if is_lgr and needs_s151_signoff(action_text):
        return S151_SIGNOFF_NOTE
    return ""


# --- Policy 6: maturity / readiness validation (Parts 5 & 10) --------------
VALID_RISK = {"High", "Medium", "Low"}
VALID_STATUS = {"Not started", "In progress", "Complete", "Blocked", "Ongoing"}


def validate_obligation(row: dict) -> list[str]:
    """
    Check one Obligations row against the 'what good looks like' rules in Part 5
    and the readiness checklist in Part 10. Returns a list of plain-English
    warnings (empty list means the row is in good shape).

    Expected keys match the Obligations sheet headers: 'Obligation ID',
    'Obligation', 'Source / Trigger', 'Owner', 'Risk Rating', 'Target Date',
    'Status', 'Evidence Required', 'Evidence Location'.
    """
    warnings: list[str] = []
    oid = (row.get("Obligation ID") or "?").strip() if isinstance(
        row.get("Obligation ID"), str
    ) else (row.get("Obligation ID") or "?")

    def blank(key: str) -> bool:
        v = row.get(key)
        return v is None or not str(v).strip()

    status = (row.get("Status") or "").strip()

    # Part 5: no blank Owner.
    if blank("Owner"):
        warnings.append(f"{oid}: Owner is blank — assign a named officer (Part 13).")
    elif not is_known_owner(row.get("Owner")):
        warnings.append(
            f"{oid}: Owner '{row.get('Owner')}' is not a recognised Part 13 contact "
            f"or council body — check the name."
        )

    # Part 5: no blank Target Date unless the obligation is genuinely Ongoing.
    if blank("Target Date") and status != "Ongoing":
        warnings.append(
            f"{oid}: Target Date is blank and Status is not 'Ongoing' — set a date "
            f"or a committee cycle."
        )

    # Part 5: Source / Trigger should be a specific title, not a vague pointer.
    src = (row.get("Source / Trigger") or "").strip().lower()
    if blank("Source / Trigger"):
        warnings.append(f"{oid}: Source / Trigger is blank.")
    elif src in {"gov.uk", "committee paper", "committee", "guidance"}:
        warnings.append(
            f"{oid}: Source / Trigger '{row.get('Source / Trigger')}' is too vague — "
            f"use the exact document title and date."
        )

    # Part 10: can you describe what proof looks like?
    if blank("Evidence Required"):
        warnings.append(f"{oid}: Evidence Required is blank — describe the proof.")

    # Part 5: Complete items must carry evidence.
    if status == "Complete" and blank("Evidence Location"):
        warnings.append(
            f"{oid}: Status is Complete but Evidence Location is blank — link the proof."
        )

    # Part 5: Evidence Location must be a specific link, not a homepage.
    loc = (row.get("Evidence Location") or "").strip().rstrip("/").lower()
    if loc in {
        "https://www.nottinghamcity.gov.uk",
        "https://www.gov.uk",
        "https://committee.nottinghamcity.gov.uk",
    }:
        warnings.append(
            f"{oid}: Evidence Location is a homepage — link the specific document."
        )

    # Validity of the dropdown fields.
    risk = (row.get("Risk Rating") or "").strip()
    if risk and risk not in VALID_RISK:
        warnings.append(f"{oid}: Risk Rating '{risk}' is not High/Medium/Low.")
    if status and status not in VALID_STATUS:
        warnings.append(f"{oid}: Status '{status}' is not a recognised status.")

    # Part 4: avoid obligations too vague to be useful.
    text = (row.get("Obligation") or "").strip()
    if text and len(text.split()) < 5:
        warnings.append(
            f"{oid}: Obligation text looks too short/vague — state who must do what, "
            f"by when, under what authority, and the evidence."
        )

    return warnings
