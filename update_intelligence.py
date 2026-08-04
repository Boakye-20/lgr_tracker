"""
Run this WEEKLY. It refreshes the Intelligence sheet in AuditTracker.xlsx.

Sources scraped each run:
    1. GOV.UK Search API     - new publications by keyword and by department
    2. GOV.UK Content API    - the full contents of watched collection pages
    3. Parliament Bills API  - bills matching your search terms
    4. PSAA website          - latest news from psaa.co.uk
    5. National Audit Office - reports and posts (API with HTML fallback)
    6. CIPFA                 - publications and articles
    7. Parliament Committees - Public Accounts Committee and HCLG Committee
    8. EMCCA                 - East Midlands Combined County Authority news

It scores each item for relevance to NCC and tags it with a theme, then adds
only genuinely new items to the Intelligence sheet. It never touches your
Obligations or Actions sheets, and it never overwrites anything you have typed
into the Reviewed or Notes columns. Items you have already reviewed stay
exactly as you left them.

If the workbook is open in Excel when you run this, it cannot save. Close the
file first.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from audit_logic import (
    assign_themes,
    classify_action_type,
    classify_materiality,
    has_obligation_trigger,
    is_excluded,
    make_hash,
    to_iso_date,
)
from sheet_format import format_data_sheet
from scraper_extensions import (
    ScrapedItem,
    scrape_cipfa,
    scrape_emcca,
    scrape_moderngov,
    scrape_nao,
    scrape_parliament_committees,
)

WORKBOOK = "AuditTracker.xlsx"
CONFIG = "sources.json"
SEEN_HASHES = "seen_hashes.txt"

HEADERS = {
    "User-Agent": "NCC-Internal-Audit-Tracker/2.0 (Nottingham City Council Internal Audit)",
    "Accept": "application/json",
}
TIMEOUT = 20
RATE_LIMIT = 0.3

GOVUK_SEARCH = "https://www.gov.uk/api/search.json"
GOVUK_CONTENT = "https://www.gov.uk/api/content"
PARLIAMENT_BILLS = "https://bills-api.parliament.uk/api/v1/Bills"


def load_config() -> dict:
    with open(CONFIG, "r", encoding="utf-8") as handle:
        return json.load(handle)


def get_json(url: str, params: dict | None = None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_seen_hashes(path: str = SEEN_HASHES) -> set[str]:
    """Read the ledger of hashes we have already processed (one per line)."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return {line.strip() for line in handle if line.strip()}
    except FileNotFoundError:
        return set()


def save_seen_hashes(hashes: set[str], path: str = SEEN_HASHES) -> None:
    """Persist the full ledger so No items never come back to the sheet."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(sorted(hashes)))


def _ext_to_item(item: ScrapedItem) -> dict:
    """Convert a ScrapedItem from scraper_extensions into the standard item dict."""
    # NCC committee pages are hand-picked local sources, so every meeting from
    # them is relevant by definition. The materiality scorer is tuned to filter
    # NATIONAL noise and keys off words like "Nottingham" / "local audit", which
    # a bare "Audit Committee — meeting 31 Jul 2026" title lacks. Enrich the text
    # the scorer sees with the council context so these are not silently dropped.
    score_text = item.Title
    if item.Source == "NCC Committee":
        score_text = f"{item.Title} Nottingham City Council committee paper"
    return {
        "Title": item.Title,
        "Source": item.Source,
        "Category": item.Category,
        "Published": item.PublishedDate,
        "URL": item.SourceURL,
        "ScoreText": score_text,
    }


# ---------------------------------------------------------------------------
# Source 1: GOV.UK Search API (keyword searches and department feed)
# ---------------------------------------------------------------------------

def fetch_govuk_search(terms, organisations, since_date):
    items = []
    fields = "title,link,public_timestamp,content_store_document_type,description"
    # Filter by date on the server so each run transfers only items that can
    # possibly be new, instead of pulling the same back-catalogue every week
    # and discarding it locally. The local since_date check stays as a backstop.
    since_filter = f"from:{since_date}"

    for term in terms:
        try:
            # No "order" here: q is free-text OR matching, so a term like
            # "local government reorganisation" matches ~68,000 documents.
            # Sorting those newest-first and taking 40 returns the last day of
            # gov.uk output on any subject. Relevance order is what makes the
            # term list actually find the documents it names.
            data = get_json(GOVUK_SEARCH, {
                "q": term,
                "count": 40,
                "fields": fields,
                "filter_public_timestamp": since_filter,
            })
        except requests.RequestException as exc:
            print(f"  [govuk-search] '{term}' failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue
        items.extend(_parse_govuk_results(data.get("results", []), since_date))
        time.sleep(RATE_LIMIT)

    for org in organisations:
        try:
            data = get_json(GOVUK_SEARCH, {
                "filter_organisations": org,
                "count": 100,
                "order": "-public_timestamp",
                "fields": fields,
                "filter_public_timestamp": since_filter,
            })
        except requests.RequestException as exc:
            print(f"  [govuk-search] org '{org}' failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue
        results = data.get("results", [])
        if len(results) >= 100:
            print(f"  [govuk-search] org '{org}' filled the page — anything older "
                  f"than the newest 100 items was not seen. Run this weekly.")
        items.extend(_parse_govuk_results(results, since_date))
        time.sleep(RATE_LIMIT)

    return items


_GOVUK_CATEGORY = {
    "consultation": "Consultation",
    "open_consultation": "Consultation",
    "closed_consultation": "Consultation",
    "policy_paper": "Guidance",
    "guidance": "Guidance",
    "statutory_guidance": "Guidance",
    "correspondence": "Correspondence",
    "written_statement": "Ministerial Statement",
    "oral_statement": "Ministerial Statement",
    "news_story": "News",
    "press_release": "News",
    "independent_report": "Report",
    "transparency": "Report",
}


def _parse_govuk_results(results, since_date):
    parsed = []
    for result in results:
        title = (result.get("title") or "").strip()
        link = result.get("link") or ""
        if not title or not link:
            continue
        url = link if link.startswith("http") else f"https://www.gov.uk{link}"
        published = to_iso_date(result.get("public_timestamp"))
        if published and published < since_date:
            continue
        doc_type = result.get("content_store_document_type") or ""
        category = _GOVUK_CATEGORY.get(doc_type, "Guidance")
        parsed.append({
            "Title": title, "Source": "GOV.UK", "Category": category,
            "Published": published, "URL": url,
            "ScoreText": f"{title} {result.get('description') or ''}",
            "DocumentType": doc_type,
        })
    return parsed


# ---------------------------------------------------------------------------
# Source 2: GOV.UK Content API (cascade children of watched collections)
# ---------------------------------------------------------------------------

def _attachment_items(payload, parent_title, parent_published, since_date=""):
    """
    Pull the PDFs hanging off a GOV.UK page.

    The substance often lives in the attachment, not the page. The MHCLG Local
    Audit Transition Plan — which sets the LAO milestone timeline and corrected
    our PSAA contract end date from 2027/28 to 2030 — is an attachment on the
    "Local audit reform" page we were already watching, so watching the page
    alone never surfaced it.
    """
    out = []
    for att in payload.get("details", {}).get("attachments") or []:
        title = (att.get("title") or "").strip()
        url = att.get("url") or ""
        if not title or not url:
            continue
        published = to_iso_date(att.get("created_at")) or parent_published
        # A watched page drags its entire document history along — the NCC
        # intervention collection alone reaches back to 2022. Same date cut as
        # every other source, applied here because attachments are by far the
        # biggest source of back-catalogue.
        if since_date and published and published < since_date:
            continue
        out.append({
            "Title": title,
            "Source": "GOV.UK",
            "Category": "Attachment",
            "Published": published,
            "URL": url,
            # "Ministerial letter to local bodies" scores as nothing on its own.
            # The parent publication is what gives the title its meaning, so the
            # scorer sees both.
            "ScoreText": f"{title} {parent_title}",
        })
    return out


def fetch_watched_paths(paths, since_date=""):
    items = []
    for path in paths:
        try:
            payload = get_json(f"{GOVUK_CONTENT}{path}")
        except requests.RequestException as exc:
            print(f"  [watched] {path} failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue

        title = (payload.get("title") or "").strip()
        published = to_iso_date(payload.get("public_updated_at"))
        if title:
            items.append({
                "Title": title, "Source": "GOV.UK", "Category": "Collection",
                "Published": published,
                "URL": f"https://www.gov.uk{path}",
            })
        items.extend(_attachment_items(payload, title, published, since_date))

        for child in payload.get("links", {}).get("documents", []) or []:
            ctitle = (child.get("title") or "").strip()
            base = child.get("base_path") or ""
            if not ctitle or not base:
                continue
            cpublished = to_iso_date(
                child.get("public_updated_at") or child.get("first_published_at")
            )
            items.append({
                "Title": ctitle, "Source": "GOV.UK", "Category": "Guidance",
                "Published": cpublished,
                "URL": f"https://www.gov.uk{base}",
            })
            # The child listing does not carry attachments, so each document
            # needs its own fetch. One call per document on a weekly run.
            try:
                cpayload = get_json(f"{GOVUK_CONTENT}{base}")
                items.extend(_attachment_items(cpayload, ctitle, cpublished, since_date))
            except requests.RequestException:
                pass
            time.sleep(RATE_LIMIT)
        time.sleep(RATE_LIMIT)
    return items


# ---------------------------------------------------------------------------
# Source 3: Parliament Bills API
# ---------------------------------------------------------------------------

def fetch_parliament_bills(terms):
    items = []
    for term in terms:
        try:
            data = get_json(PARLIAMENT_BILLS, {
                "SearchTerm": term,
                "SortOrder": "DateUpdatedDescending",
                "Take": 20,
            })
        except requests.RequestException as exc:
            print(f"  [bills] '{term}' failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue
        for bill in data.get("items", []) or []:
            title = (bill.get("shortTitle") or "").strip()
            bill_id = bill.get("billId")
            if not title or not bill_id:
                continue
            items.append({
                "Title": title, "Source": "Parliament", "Category": "Bill",
                "Published": to_iso_date(bill.get("lastUpdate")),
                "URL": f"https://bills.parliament.uk/bills/{bill_id}",
            })
        time.sleep(RATE_LIMIT)
    return items


# ---------------------------------------------------------------------------
# Source 3b: legislation.gov.uk (Acts we watch, and the SIs made under them)
# ---------------------------------------------------------------------------

def fetch_legislation(config: dict, since_date: str) -> list[dict]:
    """
    Follow watched Acts on legislation.gov.uk. The Bills API stops at Royal
    Assent, but a duty only bites once it is commenced by SI — so this is where
    "the Act passed" turns into "the Act applies to us".
    """
    cfg = config.get("legislation", {})
    if not cfg.get("enabled"):
        return []

    items = []
    for entry in cfg.get("titles", []):
        title_query = entry.get("title", "")
        if not title_query:
            continue
        try:
            response = requests.get(
                "https://www.legislation.gov.uk/all/data.feed",
                params={"title": title_query},
                headers={"User-Agent": HEADERS["User-Agent"]},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"  [legislation] '{title_query}' failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue

        soup = BeautifulSoup(response.text, "xml")
        for node in soup.find_all("entry"):
            title_node = node.find("title")
            link_node = node.find("link")
            if not title_node or not link_node:
                continue
            title = title_node.get_text(strip=True)
            url = (link_node.get("href") or "").replace("http://", "https://")
            if not title or not url:
                continue
            doc_type = node.find("DocumentMainType")
            kind = doc_type.get("Value") if doc_type else ""
            published = to_iso_date((node.find("published").get_text(strip=True)
                                     if node.find("published") else ""))
            # A watched Act drags its whole back-catalogue of SIs with it (the
            # 2014 Act has 14, most from 2014-16). Same since_date cut as
            # everywhere else, so only live developments reach the sheet.
            if published and published < since_date:
                continue
            items.append({
                "Title": title,
                "Source": "legislation.gov.uk",
                "Category": "Act" if "Act" in kind else "Statutory Instrument",
                "Published": published,
                "URL": url,
                "ScoreText": f"{title} {entry.get('context', '')}",
            })
        time.sleep(RATE_LIMIT)
    return items


# ---------------------------------------------------------------------------
# Source 4: PSAA website (no public API — web scrape)
# ---------------------------------------------------------------------------

def scrape_psaa(config: dict) -> list[dict]:
    import re
    url = config.get("psaa", {}).get("url", "https://www.psaa.co.uk/latest-news/")
    items = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [psaa] failed: {exc}")
        return items

    soup = BeautifulSoup(response.text, "lxml")
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(strip=True)
        href = str(anchor.get("href", ""))
        # PSAA news articles follow WordPress /YYYY/MM/slug/ URL structure
        if not re.search(r"/20\d\d/", href):
            continue
        # Skip "Read more of: ..." duplicate links (same URL, different label)
        if text.lower().startswith("read more"):
            continue
        if len(text) < 10:
            continue
        full_url = href if href.startswith("http") else urljoin(url, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        items.append({
            "Title": text, "Source": "PSAA", "Category": "PSAA Update",
            "Published": datetime.today().date().isoformat(),
            "URL": full_url,
            "ScoreText": text,
        })
    return items


# ---------------------------------------------------------------------------
# Write to the Intelligence sheet without disturbing anything else
# ---------------------------------------------------------------------------

def update_workbook(new_items, config):
    try:
        wb = load_workbook(WORKBOOK)
    except FileNotFoundError:
        print(f"'{WORKBOOK}' not found. Run setup_tracker.py first.")
        sys.exit(1)
    except PermissionError:
        print(f"Cannot open '{WORKBOOK}'. It is probably open in Excel. Close it and run again.")
        sys.exit(1)

    ws = wb["Intelligence"]

    # Find columns by header name so this works if columns are added or reordered
    header_row = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

    def col_of(name: str, default: int) -> int:
        return next((i + 1 for i, v in enumerate(header_row) if v == name), default)

    hash_col = col_of("Hash", 12)
    material_col = col_of("Material", 6)
    reviewed_col = col_of("Reviewed", 10)
    notes_col = col_of("Notes", 11)

    # The Action Signal column marks new items whose text carries obligation
    # language ("must / required / shall"), so the weekly review can jump
    # straight to the items that likely need an Obligations row. It is always
    # the LAST column (rows are appended positionally); add the header to an
    # existing workbook the first time this runs.
    if "Action Signal" not in header_row:
        ws.cell(row=1, column=len(header_row) + 1, value="Action Signal")

    # Dedup now lives in seen_hashes.txt, not the sheet. Seed it once from any
    # hashes already in the workbook so existing items are never re-added when
    # we switch ledgers (a no-op on every run after the first).
    seen_hashes = load_seen_hashes()
    for row in range(2, ws.max_row + 1):
        h = ws.cell(row=row, column=hash_col).value
        if h:
            seen_hashes.add(h)

    # One-time cleanup: drop existing 'No' rows that no human has touched, so
    # the sheet only shows Yes/Unclear. Rows with anything in Reviewed or Notes
    # are kept. Iterate bottom-up so deletions don't shift rows we haven't seen.
    cleaned = 0
    for row in range(ws.max_row, 1, -1):
        verdict = ws.cell(row=row, column=material_col).value
        reviewed = ws.cell(row=row, column=reviewed_col).value
        notes = ws.cell(row=row, column=notes_col).value
        touched = (reviewed and str(reviewed).strip()) or (notes and str(notes).strip())
        if verdict == "No" and not touched:
            ws.delete_rows(row, 1)
            cleaned += 1

    theme_keywords = config["theme_keywords"]
    rules = config["materiality_rules"]
    exclusions = config.get("exclusion_rules", {})
    today = datetime.today().date().isoformat()

    added = 0
    excluded = 0
    suppressed = 0
    added_by_source = {}
    added_by_verdict = {"Yes": 0, "Unclear": 0}
    possible_obligations = []
    for item in new_items:
        # Match exclusions against ScoreText, not just Title. An attachment
        # called "Letter: Kent and Medway" carries no LGR wording of its own, so
        # the county rule never fired on the title alone; ScoreText adds the
        # parent publication and the rule catches it.
        exclusion_text = item.get("ScoreText", item["Title"])
        if is_excluded(exclusion_text, exclusions, item.get("DocumentType", "")):
            excluded += 1
            continue

        h = make_hash(item["URL"], item["Title"])
        if h in seen_hashes:
            continue
        seen_hashes.add(h)  # record as seen regardless of verdict, so it never returns

        score_text = item.get("ScoreText", item["Title"])
        verdict, matched = classify_materiality(score_text, rules)

        # Only Yes and Unclear reach the sheet. No items are now tracked
        # silently via the ledger instead of cluttering the Intelligence sheet.
        if verdict == "No":
            suppressed += 1
            continue

        # Policy 4: does this item talk like an obligation? If so, name the
        # action archetype it would translate into, so the reviewer sees not
        # just "material" but "material and probably actionable, as an X".
        if has_obligation_trigger(score_text):
            signal = f"Possible obligation ({classify_action_type(score_text)})"
            possible_obligations.append((item["Title"], item["Source"], verdict))
        else:
            signal = ""

        ws.append([
            today,
            item["Title"],
            item["Source"],
            item["Category"],
            item.get("Published", ""),
            verdict,          # Material  — Yes / Unclear
            matched,          # Matched   — which groups triggered it, e.g. "Local, Audit"
            assign_themes(score_text, theme_keywords),
            item["URL"],
            "",               # Reviewed  — left blank for a human
            "",               # Notes     — left blank for a human
            h,
            signal,           # Action Signal — obligation language detected
        ])
        added += 1
        added_by_source[item["Source"]] = added_by_source.get(item["Source"], 0) + 1
        added_by_verdict[verdict] += 1

    # Newly appended rows carry no styling, so re-apply the table treatment.
    format_data_sheet(ws)

    try:
        wb.save(WORKBOOK)
    except PermissionError:
        print(f"Cannot save '{WORKBOOK}'. Close it in Excel and run again.")
        sys.exit(1)

    # Only persist the ledger after a successful save, so a failed save doesn't
    # leave hashes recorded as seen for items that never made it to the sheet.
    save_seen_hashes(seen_hashes)

    if excluded:
        print(f"  (Filtered out {excluded} items about devolved nations, other counties' LGR, or excluded keywords)")
    if suppressed:
        print(f"  (Recorded {suppressed} non-material items silently in {SEEN_HASHES}; not written to the sheet)")
    if cleaned:
        print(f"  (Removed {cleaned} existing 'No' rows that had not been reviewed)")

    # Review-ready summary: what landed, from where, and which items look like
    # they create work — so the weekly review starts here, not with a filter.
    if added:
        print(f"\nThis week's intake: {added} new item(s) — "
              f"{added_by_verdict['Yes']} material, {added_by_verdict['Unclear']} unclear.")
        for source, count in sorted(added_by_source.items(), key=lambda x: -x[1]):
            print(f"  {source}: {count}")
    if possible_obligations:
        print(f"\n{len(possible_obligations)} item(s) contain obligation language "
              f"(must / required / shall) — review these first:")
        for title, source, verdict in possible_obligations:
            print(f"  [{verdict}] {title[:90]}  ({source})")

    return added


def main():
    config = load_config()
    since = config.get("since_date", "2024-01-01")

    print("Fetching GOV.UK search results...")
    items = fetch_govuk_search(
        config.get("govuk_search_terms", []),
        config.get("govuk_organisations", []),
        since,
    )
    print(f"  {len(items)} items")

    print("Fetching watched GOV.UK collections...")
    watched = fetch_watched_paths(config.get("watched_govuk_paths", []), since)
    print(f"  {len(watched)} items")
    items.extend(watched)

    print("Fetching Parliament bills...")
    bills = fetch_parliament_bills(config.get("parliament_search_terms", []))
    print(f"  {len(bills)} items")
    items.extend(bills)

    print("Fetching watched legislation...")
    legislation = fetch_legislation(config, since)
    print(f"  {len(legislation)} items")
    items.extend(legislation)

    print("Scraping PSAA...")
    psaa = scrape_psaa(config)
    print(f"  {len(psaa)} items")
    items.extend(psaa)

    nao_cfg = config.get("nao", {})
    if nao_cfg.get("enabled"):
        print("Fetching NAO...")
        nao_items = scrape_nao(
            keywords=nao_cfg.get("keywords", []),
            max_items=nao_cfg.get("max_items", 40),
        )
        print(f"  {len(nao_items)} items")
        items.extend(_ext_to_item(i) for i in nao_items)

    cipfa_cfg = config.get("cipfa", {})
    if cipfa_cfg.get("enabled"):
        print("Fetching CIPFA...")
        cipfa_items = scrape_cipfa(
            keywords=cipfa_cfg.get("keywords", []),
            max_items=cipfa_cfg.get("max_items", 40),
        )
        print(f"  {len(cipfa_items)} items")
        items.extend(_ext_to_item(i) for i in cipfa_items)

    committees_cfg = config.get("parliament_committees", {})
    if committees_cfg.get("enabled"):
        print("Fetching Parliament Committees...")
        committee_items = scrape_parliament_committees(
            keywords=committees_cfg.get("keywords", []),
            committee_ids=committees_cfg.get("committee_ids"),
            max_per_committee=committees_cfg.get("max_per_committee", 20),
        )
        print(f"  {len(committee_items)} items")
        items.extend(_ext_to_item(i) for i in committee_items)

    emcca_cfg = config.get("emcca", {})
    if emcca_cfg.get("enabled"):
        print("Fetching EMCCA...")
        emcca_items = scrape_emcca(
            keywords=emcca_cfg.get("keywords") or None,
            max_items=emcca_cfg.get("max_items", 30),
        )
        print(f"  {len(emcca_items)} items")
        items.extend(_ext_to_item(i) for i in emcca_items)

    ncc_cfg = config.get("ncc_committees", {})
    if ncc_cfg.get("enabled"):
        print("Fetching NCC committee pages...")
        ncc_items = scrape_moderngov(
            pages=ncc_cfg.get("pages", []),
            keywords=ncc_cfg.get("keywords") or None,
            base_url=ncc_cfg.get("base_url", "https://committee.nottinghamcity.gov.uk/"),
            max_per_page=ncc_cfg.get("max_per_page", 25),
            since=ncc_cfg.get("since_date") or since,
        )
        print(f"  {len(ncc_items)} items")
        items.extend(_ext_to_item(i) for i in ncc_items)

    print(f"\nProcessing {len(items)} fetched items...")
    added = update_workbook(items, config)
    print(f"Added {added} new items to the Intelligence sheet.")
    print("Open AuditTracker.xlsx and review anything marked Material = Yes.")


if __name__ == "__main__":
    main()
