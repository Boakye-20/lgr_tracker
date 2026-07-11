"""
Extra web scrapers for sources that have no clean API:
  - National Audit Office
  - CIPFA publications
  - Parliament Committees API
  - East Midlands Combined County Authority
  - NCC committee pages (ModernGov: committee.nottinghamcity.gov.uk)

Each function returns a list of ScrapedItem dataclasses.
update_intelligence.py converts these to the standard item dict via _ext_to_item().
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "NCC-Internal-Audit-Tracker/2.0 (Nottingham City Council Internal Audit)",
    "Accept": "application/json, text/html;q=0.9, */*;q=0.5",
}
TIMEOUT = 20
RATE_LIMIT = 0.4


@dataclass
class ScrapedItem:
    Title: str
    Category: str
    Source: str
    SourceURL: str
    PublishedDate: str


def _to_iso_date(raw: Optional[str]) -> str:
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


def _get(url: str, params: Optional[dict] = None) -> requests.Response:
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response


# ---------------------------------------------------------------------------
# National Audit Office
# ---------------------------------------------------------------------------

def scrape_nao(keywords: Iterable[str], max_items: int = 40) -> list[ScrapedItem]:
    keywords_lower = [k.lower() for k in keywords]
    items: list[ScrapedItem] = []

    # Try WordPress REST API endpoints first (cleaner than scraping HTML)
    for endpoint in (
        "https://www.nao.org.uk/wp-json/wp/v2/reports",
        "https://www.nao.org.uk/wp-json/wp/v2/posts",
    ):
        try:
            response = _get(endpoint, params={"per_page": max_items, "_fields": "title,link,date"})
            posts = response.json() or []
            if posts:
                for post in posts:
                    title_raw = post.get("title", {})
                    title = (title_raw.get("rendered", "") if isinstance(title_raw, dict) else str(title_raw)).strip()
                    url = post.get("link") or ""
                    if not title or not url:
                        continue
                    if keywords_lower and not any(k in title.lower() for k in keywords_lower):
                        continue
                    items.append(ScrapedItem(
                        Title=title, Category="Report", Source="NAO",
                        SourceURL=url, PublishedDate=_to_iso_date(post.get("date")),
                    ))
                return items
        except requests.RequestException:
            continue

    # HTML fallback
    try:
        html = _get("https://www.nao.org.uk/reports/").text
    except requests.RequestException as exc:
        print(f"  [nao] failed: {exc}")
        return items

    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    # NAO pages use heading anchors to link to reports
    for anchor in soup.select("h2 a[href], h3 a[href], article a[href]"):
        title = anchor.get_text(strip=True)
        url = str(anchor.get("href", ""))
        if not title or len(title) < 8 or url in seen:
            continue
        if not url.startswith("http"):
            url = "https://www.nao.org.uk" + url
        seen.add(url)
        if keywords_lower and not any(k in title.lower() for k in keywords_lower):
            continue
        parent = anchor.find_parent(["article", "li", "div"])
        date_el = parent.find("time") if parent else None
        items.append(ScrapedItem(
            Title=title, Category="Report", Source="NAO",
            SourceURL=url,
            PublishedDate=_to_iso_date(date_el.get("datetime") if date_el else ""),
        ))
        if len(items) >= max_items:
            break
    return items


# ---------------------------------------------------------------------------
# CIPFA publications
# ---------------------------------------------------------------------------

def scrape_cipfa(keywords: Iterable[str], max_items: int = 40) -> list[ScrapedItem]:
    keywords_lower = [k.lower() for k in keywords]
    items: list[ScrapedItem] = []

    for index_url in (
        "https://www.cipfa.org/policy-and-guidance/publications",
        "https://www.cipfa.org/cipfa-thinks",
    ):
        try:
            html = _get(index_url).text
        except requests.RequestException as exc:
            print(f"  [cipfa] failed to fetch {index_url}: {exc}")
            continue

        soup = BeautifulSoup(html, "lxml")
        seen: set[str] = set()
        for anchor in soup.select("a[href]"):
            href = str(anchor.get("href", ""))
            title = anchor.get_text(strip=True)
            if not href or not title or len(title) < 12:
                continue
            href_lower = href.lower()
            if "/publications/" not in href_lower and "/cipfa-thinks/articles/" not in href_lower:
                continue
            if href.startswith("/"):
                href = "https://www.cipfa.org" + href
            if href in seen:
                continue
            seen.add(href)
            if keywords_lower and not any(k in title.lower() for k in keywords_lower):
                continue
            items.append(ScrapedItem(
                Title=title, Category="Guidance", Source="CIPFA",
                SourceURL=href, PublishedDate="",
            ))
            if len(items) >= max_items:
                return items

    return items


# ---------------------------------------------------------------------------
# Parliament Committees API
# ---------------------------------------------------------------------------

PARLIAMENT_COMMITTEES_API = "https://committees-api.parliament.uk/api/Publications"

KNOWN_COMMITTEE_IDS = {
    127: "Public Accounts Committee",
    398: "Housing, Communities and Local Government Committee",
    448: "Levelling Up, Housing and Communities Committee",
}


def scrape_parliament_committees(
    keywords: Iterable[str],
    committee_ids: Optional[Iterable[int]] = None,
    max_per_committee: int = 20,
) -> list[ScrapedItem]:
    if committee_ids is None:
        committee_ids = list(KNOWN_COMMITTEE_IDS.keys())

    keywords_lower = [k.lower() for k in keywords]
    items: list[ScrapedItem] = []

    for committee_id in committee_ids:
        try:
            response = _get(
                PARLIAMENT_COMMITTEES_API,
                params={"CommitteeId": committee_id, "Take": max_per_committee, "Skip": 0},
            )
            payload = response.json()
        except requests.RequestException as exc:
            print(f"  [committees {committee_id}] failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue

        for pub in payload.get("items", []) or []:
            title = (pub.get("description") or "").strip()
            pub_id = pub.get("id")
            if not title or not pub_id:
                continue
            # Prefer a direct file URL; fall back to the publication page
            documents = pub.get("documents") or []
            url = None
            if documents:
                files = (documents[0].get("files") or [])
                if files:
                    url = files[0].get("url")
            if not url:
                url = f"https://committees.parliament.uk/publications/{pub_id}/"
            if keywords_lower and not any(k in title.lower() for k in keywords_lower):
                continue
            items.append(ScrapedItem(
                Title=title, Category="Guidance", Source="Parliament Committees",
                SourceURL=url,
                PublishedDate=_to_iso_date(pub.get("publicationStartDate")),
            ))
        time.sleep(RATE_LIMIT)

    return items


# ---------------------------------------------------------------------------
# East Midlands Combined County Authority
# ---------------------------------------------------------------------------

def scrape_emcca(
    keywords: Optional[Iterable[str]] = None,
    max_items: int = 30,
) -> list[ScrapedItem]:
    keywords_lower = [k.lower() for k in (keywords or [])]
    items: list[ScrapedItem] = []

    try:
        html = _get("https://www.eastmidlands-cca.gov.uk/news/").text
    except requests.RequestException as exc:
        print(f"  [emcca] failed: {exc}")
        return items

    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    # EMCCA uses article.c-post cards; the title is in an <h3> inside a second <a>
    for card in soup.select("article.c-post"):
        heading = card.find(["h2", "h3", "h4"])
        anchor = heading.find_parent("a") if heading else None
        if not anchor:
            # fallback: first link with non-empty text
            for a in card.find_all("a", href=True):
                if a.get_text(strip=True):
                    anchor = a
                    break
        if not anchor:
            continue
        title = (heading or anchor).get_text(strip=True)
        url = str(anchor.get("href", ""))
        if not title or len(title) < 6 or url in seen:
            continue
        if url.startswith("/"):
            url = "https://www.eastmidlands-cca.gov.uk" + url
        seen.add(url)
        if keywords_lower and not any(k in title.lower() for k in keywords_lower):
            continue
        date_el = card.find("time")
        items.append(ScrapedItem(
            Title=title, Category="Guidance", Source="EMCCA",
            SourceURL=url,
            PublishedDate=_to_iso_date(date_el.get("datetime") if date_el else ""),
        ))
        if len(items) >= max_items:
            break
    return items


# ---------------------------------------------------------------------------
# NCC committee pages (ModernGov)
# ---------------------------------------------------------------------------
# committee.nottinghamcity.gov.uk runs the ModernGov platform, whose pages are
# .aspx (mgCommitteeDetails, ieListDocuments, mgCalendarMonthView), NOT the
# GOV.UK content API. That is why these URLs cannot live in watched_govuk_paths
# and need this dedicated scraper.
#
# Strategy: fetch each configured committee/calendar page and pull out the links
# that point at a specific meeting's document list (ieListDocuments.aspx) or a
# reports-pack / agenda / minutes PDF. Each becomes one Intelligence item, so a
# new meeting pack shows up in the feed automatically.

# Match "20th February, 2026" / "4 June 2026" / "4th Jun 2026" inside link text.
_MG_DATE_RE = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9}),?\s+(\d{4})", re.IGNORECASE
)


def _mg_date(text: str) -> str:
    """Pull an ISO date out of a ModernGov link/title, or '' if none found."""
    match = _MG_DATE_RE.search(text or "")
    if not match:
        return ""
    day, month, year = match.groups()
    cleaned = f"{int(day)} {month} {year}"
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def _mg_page_label(soup: BeautifulSoup, fallback: str) -> str:
    """The committee name for a page — from <h1>, else the <title>, else fallback."""
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    if soup.title and soup.title.get_text(strip=True):
        # ModernGov titles look like "Agenda for Audit Committee on ..." — keep the lot.
        return soup.title.get_text(strip=True)
    return fallback


def _mg_doc_links(soup: BeautifulSoup):
    """Yield (href, link_text) for meeting-document and pack/agenda/minutes PDF links."""
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", ""))
        text = anchor.get_text(" ", strip=True).replace("\xa0", " ")
        href_lower = href.lower()
        is_meeting = "ielistdocuments.aspx" in href_lower
        is_doc_pack = href_lower.endswith(".pdf") and any(
            w in (text.lower() + " " + href_lower)
            for w in ("reports pack", "agenda", "minutes", "report")
        )
        if is_meeting or is_doc_pack:
            yield href, text, is_meeting


def scrape_moderngov(
    pages: Iterable[dict],
    keywords: Optional[Iterable[str]] = None,
    base_url: str = "https://committee.nottinghamcity.gov.uk/",
    max_per_page: int = 25,
    since: Optional[str] = None,
) -> list[ScrapedItem]:
    """
    Scrape NCC ModernGov committee pages.

    `pages` is a list of {"name": "...", "url": "..."} dicts. The best URL to use
    is a committee's "Browse meetings" list (ieListMeetings.aspx?CommitteeId=NNN),
    which lists each meeting with its date. A committee details page
    (mgCommitteeDetails.aspx?ID=NNN) also works — the scraper follows its
    "Browse meetings" link automatically. Each meeting (or reports-pack PDF)
    becomes one Intelligence item.

    `keywords` filters items by committee name + link text (so "audit",
    "improvement", "governance" keep the committees you care about). Pass no
    keywords to keep everything.

    `since` is an ISO date (YYYY-MM-DD). Meetings dated before it are dropped, so
    the back-catalogue of old meetings does not flood the feed. A meeting whose
    date could not be parsed is always kept (better to review than to lose it).
    """
    keywords_lower = [k.lower() for k in (keywords or [])]
    since = (since or "").strip() or None
    items: list[ScrapedItem] = []
    seen: set[str] = set()
    dropped_old = 0

    for page in pages:
        name = (page.get("name") or "").strip() or "NCC Committee"
        url = page.get("url") or ""
        if not url:
            continue
        try:
            soup = BeautifulSoup(_get(url).text, "lxml")
        except requests.RequestException as exc:
            print(f"  [ncc-committee] {name} failed: {exc}")
            time.sleep(RATE_LIMIT)
            continue

        doc_links = list(_mg_doc_links(soup))

        # If this is a details/calendar page with no meeting links of its own,
        # follow its "Browse meetings" link (ieListMeetings.aspx) and use that.
        if not doc_links:
            follow = soup.find("a", href=re.compile("ielistmeetings.aspx", re.IGNORECASE))
            if follow:
                next_url = urljoin(base_url, str(follow.get("href")))
                try:
                    soup = BeautifulSoup(_get(next_url).text, "lxml")
                    doc_links = list(_mg_doc_links(soup))
                except requests.RequestException as exc:
                    print(f"  [ncc-committee] {name} meetings page failed: {exc}")

        label = _mg_page_label(soup, name)
        count = 0
        for href, text, is_meeting in doc_links:
            full_url = href if href.startswith("http") else urljoin(base_url, href)
            if full_url in seen:
                continue

            meeting_date = _mg_date(text) or _mg_date(label)
            # Drop meetings older than the cutoff (undated items are kept).
            if since and meeting_date and meeting_date < since:
                seen.add(full_url)
                dropped_old += 1
                continue
            # Meeting links carry only a date, so prefix the committee name;
            # pack/agenda PDFs usually carry their own descriptive text.
            if is_meeting or len(text) < 12:
                title = f"{name} — meeting {text}".strip(" —")
            else:
                title = text

            haystack = f"{name} {label} {text}".lower()
            if keywords_lower and not any(k in haystack for k in keywords_lower):
                continue

            seen.add(full_url)
            items.append(ScrapedItem(
                Title=title,
                Category="Committee Paper",
                Source="NCC Committee",
                SourceURL=full_url,
                PublishedDate=meeting_date,
            ))
            count += 1
            if count >= max_per_page:
                break
        time.sleep(RATE_LIMIT)

    if dropped_old:
        print(f"  [ncc-committee] skipped {dropped_old} meeting(s) before {since}")
    return items
