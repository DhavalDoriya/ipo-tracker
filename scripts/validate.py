"""Check every file in data/ against the schema in docs/DATABASE.md.

Exits 1 on the first run that finds any error, so the workflow never commits bad data.
Usage: python3 scripts/validate.py [data_dir]
"""

import json
import os
import re
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
IPO_TYPES = {"mainboard", "sme"}
IPO_STATUSES = {"upcoming", "open", "closed", "listed"}
BUYBACK_TYPES = {"tender", "open_market"}
BUYBACK_STATUSES = {"upcoming", "open", "closed"}


def is_date(value):
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def is_timestamp(value):
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (AttributeError, ValueError):
        return False


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_common(item, where, errors, seen):
    """id and name rules shared by every list item. Returns False when the item is unusable."""
    if not isinstance(item, dict):
        errors.append(f"{where}: must be an object")
        return False
    item_id = item.get("id")
    if not isinstance(item_id, str) or not ID_RE.match(item_id):
        errors.append(f"{where}: id must be a kebab-case slug")
    elif item_id in seen:
        errors.append(f"{where}: duplicate id '{item_id}'")
    else:
        seen.add(item_id)
    if not isinstance(item.get("name"), str) or not item["name"].strip():
        errors.append(f"{where}: name is required")
    return True


def check_dates(item, fields, where, errors):
    for field in fields:
        value = item.get(field)
        if value is not None and not is_date(value):
            errors.append(f"{where}: {field} must be YYYY-MM-DD or null")


def check_url(item, where, errors):
    value = item.get("source_url")
    if value is not None and not (isinstance(value, str) and value.startswith("https://")):
        errors.append(f"{where}: source_url must start with https:// or be null")


def check_updated_at(doc, name, errors):
    if not is_timestamp(doc.get("updated_at")):
        errors.append(f"{name}: updated_at must be an ISO 8601 timestamp")


def validate_ipos(doc):
    errors, seen = [], set()
    check_updated_at(doc, "ipos.json", errors)
    if not isinstance(doc.get("source"), str) or not doc["source"].strip():
        errors.append("ipos.json: source is required")
    ipos = doc.get("ipos")
    if not isinstance(ipos, list) or not ipos:
        return errors + ["ipos.json: ipos must be a non-empty list"]
    for i, ipo in enumerate(ipos):
        where = f"ipos.json ipos[{i}]"
        if not check_common(ipo, where, errors, seen):
            continue
        if ipo.get("type") not in IPO_TYPES:
            errors.append(f"{where}: type must be one of {sorted(IPO_TYPES)}")
        if ipo.get("status") not in IPO_STATUSES:
            errors.append(f"{where}: status must be one of {sorted(IPO_STATUSES)}")
        check_dates(ipo, ("open_date", "close_date", "listing_date"), where, errors)
        check_url(ipo, where, errors)
        price = ipo.get("offer_price")
        if price is not None:
            if not (isinstance(price, dict) and is_number(price.get("min")) and is_number(price.get("max"))):
                errors.append(f"{where}: offer_price must be {{min, max}} numbers or null")
            elif price["min"] > price["max"]:
                errors.append(f"{where}: offer_price.min is above max")
        for field in ("list_price", "lot_size", "gmp"):
            if ipo.get(field) is not None and not is_number(ipo[field]):
                errors.append(f"{where}: {field} must be a number or null")
    return errors


def validate_coming_soon(doc):
    errors, seen = [], set()
    check_updated_at(doc, "coming_soon.json", errors)
    ipos = doc.get("ipos")
    if not isinstance(ipos, list):
        return errors + ["coming_soon.json: ipos must be a list"]
    for i, ipo in enumerate(ipos):
        where = f"coming_soon.json ipos[{i}]"
        if not check_common(ipo, where, errors, seen):
            continue
        if ipo.get("type") not in IPO_TYPES:
            errors.append(f"{where}: type must be one of {sorted(IPO_TYPES)}")
        check_url(ipo, where, errors)
    return errors


def validate_buybacks(doc):
    errors, seen = [], set()
    check_updated_at(doc, "buybacks.json", errors)
    buybacks = doc.get("buybacks")
    if not isinstance(buybacks, list):
        return errors + ["buybacks.json: buybacks must be a list"]
    for i, buyback in enumerate(buybacks):
        where = f"buybacks.json buybacks[{i}]"
        if not check_common(buyback, where, errors, seen):
            continue
        if buyback.get("type") not in BUYBACK_TYPES:
            errors.append(f"{where}: type must be one of {sorted(BUYBACK_TYPES)}")
        if buyback.get("status") not in BUYBACK_STATUSES:
            errors.append(f"{where}: status must be one of {sorted(BUYBACK_STATUSES)}")
        check_dates(buyback, ("record_date", "open_date", "close_date"), where, errors)
        if buyback.get("buyback_price") is not None and not is_number(buyback["buyback_price"]):
            errors.append(f"{where}: buyback_price must be a number or null")
    return errors


def validate_gmp(doc):
    errors = []
    check_updated_at(doc, "gmp.json", errors)
    entries = doc.get("entries")
    if not isinstance(entries, list):
        return errors + ["gmp.json: entries must be a list"]
    for i, entry in enumerate(entries):
        where = f"gmp.json entries[{i}]"
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            errors.append(f"{where}: id is required")
        elif not is_number(entry.get("gmp")):
            errors.append(f"{where}: gmp must be a number")
    return errors


def validate_checklist(doc, name):
    errors = []
    if not isinstance(doc.get("company"), str) or not doc["company"].strip():
        errors.append(f"{name}: company is required")
    sections = doc.get("sections")
    if not isinstance(sections, list) or not sections:
        return errors + [f"{name}: sections must be a non-empty list"]
    for s, section in enumerate(sections):
        where = f"{name} sections[{s}]"
        if not isinstance(section, dict) or not isinstance(section.get("title"), str):
            errors.append(f"{where}: title is required")
            continue
        parameters = section.get("parameters")
        if not isinstance(parameters, list) or not parameters:
            errors.append(f"{where}: parameters must be a non-empty list")
            continue
        for p, parameter in enumerate(parameters):
            for field in ("name", "meaning", "positive", "negative"):
                if not isinstance(parameter, dict) or not isinstance(parameter.get(field), str):
                    errors.append(f"{where} parameters[{p}]: {field} is required")
    return errors


def load(path, errors):
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, json.JSONDecodeError) as err:
        errors.append(f"{os.path.basename(path)}: cannot read ({err})")
        return None
    if not isinstance(doc, dict):
        errors.append(f"{os.path.basename(path)}: top level must be an object")
        return None
    return doc


def validate_all(data_dir):
    errors = []
    files = (
        ("ipos.json", validate_ipos),
        ("coming_soon.json", validate_coming_soon),
        ("buybacks.json", validate_buybacks),
        ("gmp.json", validate_gmp),
    )
    for name, validator in files:
        doc = load(os.path.join(data_dir, name), errors)
        if doc is not None:
            errors.extend(validator(doc))

    checklist_dir = os.path.join(data_dir, "checklists")
    if os.path.isdir(checklist_dir):
        for name in sorted(os.listdir(checklist_dir)):
            if not name.endswith(".json"):
                continue
            if not ID_RE.match(name[: -len(".json")]):
                errors.append(f"checklists/{name}: file name must be a kebab-case slug")
            doc = load(os.path.join(checklist_dir, name), errors)
            if doc is not None:
                errors.extend(validate_checklist(doc, f"checklists/{name}"))
    return errors


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data")
    errors = validate_all(data_dir)
    for error in errors:
        print(f"[error] {error}")
    if errors:
        print(f"[fail] {len(errors)} problem(s)")
        return 1
    print("[ok] data is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
