"""Collect IPO data from the sources in scripts/sources.json and write data/ipos.json.

Rules (docs/SECURITY.md): obey robots.txt, at most 1 request per second, honest User-Agent.
Nothing is written when the content is unchanged, so the workflow only commits real changes.
"""

import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone
from urllib import robotparser
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUT = os.path.join(DATA_DIR, "ipos.json")
SOURCES_FILE = os.path.join(ROOT, "scripts", "sources.json")

USER_AGENT = "ipo-update-bot/0.1 (+https://github.com/DhavalDoriya/ipo-update)"
MIN_INTERVAL = 1.0  # seconds between requests

# Fields a source may map a table column to.
TEXT_FIELDS = {"name", "issue_size", "subscription"}
DATE_FIELDS = {"open_date", "close_date", "listing_date"}
NUMBER_FIELDS = {"lot_size", "list_price"}

_last_request = 0.0


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def parse_date(text, fmt):
    """Source date text -> 'YYYY-MM-DD', or None when empty or unparseable."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, fmt).date().isoformat()
    except ValueError:
        return None


def parse_number(text):
    """'₹1,200.50' -> 1200.5, '2000' -> 2000, '' -> None."""
    cleaned = re.sub(r"[^0-9.]", "", text or "")
    if not cleaned or cleaned == ".":
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    return int(value) if value.is_integer() else value


def parse_price_band(text):
    """'62 to 66', '₹62 - ₹66' or '120' -> {'min': 62, 'max': 66}; None when no number."""
    numbers = [parse_number(n) for n in re.findall(r"[0-9][0-9,]*\.?[0-9]*", text or "")]
    numbers = [n for n in numbers if n is not None]
    if not numbers:
        return None
    return {"min": min(numbers[:2]), "max": max(numbers[:2])}


def derive_status(open_date, close_date, listing_date, today):
    """Status from the dates alone; all arguments are ISO strings or None."""
    if listing_date and listing_date <= today:
        return "listed"
    if close_date and close_date < today:
        return "closed"
    if open_date and open_date <= today:
        return "open"
    return "upcoming"


def parse_table(html, source, today):
    """Parse one HTML table into IPO dicts using the column mapping in `source`."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(source.get("table_selector", "table"))
    if table is None:
        return []

    rows = table.find_all("tr")
    if not rows:
        return []
    headers = [c.get_text(" ", strip=True).lower() for c in rows[0].find_all(["th", "td"])]
    # field -> column index, matched on header text
    index = {}
    for field, header in source["columns"].items():
        if header.lower() in headers:
            index[field] = headers.index(header.lower())
    if "name" not in index:
        return []

    date_format = source.get("date_format", "%Y-%m-%d")
    ipos = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue

        def cell(field):
            i = index.get(field)
            return cells[i].get_text(" ", strip=True) if i is not None and i < len(cells) else ""

        name = cell("name")
        if not name:
            continue
        ipo = {
            "id": slugify(name),
            "name": name,
            "type": source["type"],
            "exchange": source["exchange"],
            "status": "upcoming",
            "open_date": None,
            "close_date": None,
            "listing_date": None,
            "offer_price": parse_price_band(cell("offer_price")),
            "list_price": None,
            "lot_size": None,
            "issue_size": None,
            "subscription": None,
            "subscription_breakup": None,
            "gmp": None,
            "source_url": source["url"],
        }
        for field in DATE_FIELDS:
            ipo[field] = parse_date(cell(field), date_format)
        for field in NUMBER_FIELDS:
            ipo[field] = parse_number(cell(field))
        for field in TEXT_FIELDS - {"name"}:
            ipo[field] = cell(field) or None
        ipo["status"] = derive_status(ipo["open_date"], ipo["close_date"], ipo["listing_date"], today)
        ipos.append(ipo)
    return ipos


def robots_allowed(url):
    parts = urlsplit(url)
    parser = robotparser.RobotFileParser(f"{parts.scheme}://{parts.netloc}/robots.txt")
    try:
        parser.read()
    except OSError as err:
        print(f"[warn] cannot read robots.txt for {parts.netloc}: {err}")
        return False
    return parser.can_fetch(USER_AGENT, url)


def fetch(url, retries=3):
    import requests

    global _last_request
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.monotonic()
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
            response.raise_for_status()
            return response.text
        except requests.RequestException as err:
            print(f"[warn] {url} attempt {attempt + 1} failed: {err}")
            time.sleep(2**attempt)
    return None


def load_sources():
    with open(SOURCES_FILE, encoding="utf-8") as f:
        return json.load(f)["sources"]


def scrape(sources, today):
    """Run every source; a failing source is skipped, not fatal."""
    ipos, seen = [], set()
    for source in sources:
        if not source["url"].startswith("https://"):
            print(f"[warn] {source['name']}: url must be https; skipped")
            continue
        if not robots_allowed(source["url"]):
            print(f"[warn] {source['name']}: disallowed by robots.txt; skipped")
            continue
        html = fetch(source["url"])
        if html is None:
            continue
        found = parse_table(html, source, today)
        print(f"[info] {source['name']}: {len(found)} IPOs")
        for ipo in found:
            if ipo["id"] not in seen:
                seen.add(ipo["id"])
                ipos.append(ipo)
    return ipos


def is_unchanged(existing, ipos, source_label):
    return (
        existing is not None
        and existing.get("ipos") == ipos
        and existing.get("source") == source_label
        and not existing.get("sample")
    )


def write_json(path, payload):
    """Atomic write: a crash never leaves a half-written file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def main():
    sources = load_sources()
    if not sources:
        print("[info] no sources configured in scripts/sources.json; data left as is")
        return 0

    ipos = scrape(sources, date.today().isoformat())
    if not ipos:
        print("[error] no data from any source; data left as is")
        return 1

    source_label = ", ".join(s["name"] for s in sources)
    existing = None
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            existing = json.load(f)
    if is_unchanged(existing, ipos, source_label):
        print("[ok] no change")
        return 0

    now = datetime.now(timezone.utc)
    payload = {
        "updated_at": now.isoformat(timespec="seconds"),
        "source": source_label,
        "ipos": ipos,
    }
    write_json(OUT, payload)
    os.makedirs(os.path.join(DATA_DIR, "history"), exist_ok=True)
    write_json(os.path.join(DATA_DIR, "history", f"{now:%Y-%m-%d}.json"), payload)
    print(f"[ok] wrote {len(ipos)} IPOs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
