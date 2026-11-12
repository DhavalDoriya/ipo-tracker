import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import scrape  # noqa: E402

SOURCE = {
    "name": "Fixture",
    "url": "https://example.com/ipo/sme",
    "type": "sme",
    "exchange": "BSE SME",
    "table_selector": "table#ipo-list",
    "date_format": "%d %b %Y",
    "columns": {
        "name": "Company",
        "open_date": "Open",
        "close_date": "Close",
        "listing_date": "Listing",
        "offer_price": "Price Band",
        "lot_size": "Lot Size",
        "issue_size": "Issue Size",
        "subscription": "Subscription",
    },
}


def fixture():
    with open(os.path.join(HERE, "fixtures", "ipo_table.html"), encoding="utf-8") as f:
        return f.read()


class HelperTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(scrape.slugify("Fixture Beta & Co"), "fixture-beta-co")
        self.assertEqual(scrape.slugify("  Alpha Ltd. "), "alpha-ltd")

    def test_parse_date(self):
        self.assertEqual(scrape.parse_date("10 Nov 2026", "%d %b %Y"), "2026-11-10")
        self.assertIsNone(scrape.parse_date("", "%d %b %Y"))
        self.assertIsNone(scrape.parse_date("soon", "%d %b %Y"))

    def test_parse_number(self):
        self.assertEqual(scrape.parse_number("2,000"), 2000)
        self.assertEqual(scrape.parse_number("₹52.80"), 52.8)
        self.assertIsNone(scrape.parse_number("-"))

    def test_parse_price_band(self):
        self.assertEqual(scrape.parse_price_band("₹62 to ₹66"), {"min": 62, "max": 66})
        self.assertEqual(scrape.parse_price_band("120"), {"min": 120, "max": 120})
        self.assertEqual(scrape.parse_price_band("1,020 - 1,075"), {"min": 1020, "max": 1075})
        self.assertIsNone(scrape.parse_price_band("TBA"))

    def test_derive_status(self):
        today = "2026-11-12"
        self.assertEqual(scrape.derive_status("2026-11-20", "2026-11-24", None, today), "upcoming")
        self.assertEqual(scrape.derive_status("2026-11-10", "2026-11-12", "2026-11-17", today), "open")
        self.assertEqual(scrape.derive_status("2026-11-06", "2026-11-10", "2026-11-13", today), "closed")
        self.assertEqual(scrape.derive_status("2026-11-03", "2026-11-05", "2026-11-10", today), "listed")
        self.assertEqual(scrape.derive_status(None, None, None, today), "upcoming")


class ParseTableTests(unittest.TestCase):
    def setUp(self):
        self.ipos = scrape.parse_table(fixture(), SOURCE, "2026-11-12")

    def test_skips_rows_without_a_name(self):
        self.assertEqual([i["id"] for i in self.ipos], ["fixture-alpha-ltd", "fixture-beta-co"])

    def test_maps_columns(self):
        alpha = self.ipos[0]
        self.assertEqual(alpha["name"], "Fixture Alpha Ltd.")
        self.assertEqual(alpha["open_date"], "2026-11-10")
        self.assertEqual(alpha["listing_date"], "2026-11-17")
        self.assertEqual(alpha["offer_price"], {"min": 62, "max": 66})
        self.assertEqual(alpha["lot_size"], 2000)
        self.assertEqual(alpha["issue_size"], "₹27.9 Cr")
        self.assertEqual(alpha["subscription"], "12.85x")
        self.assertEqual(alpha["status"], "open")
        self.assertEqual(alpha["type"], "sme")
        self.assertEqual(alpha["source_url"], SOURCE["url"])

    def test_empty_cells_become_null(self):
        beta = self.ipos[1]
        self.assertIsNone(beta["listing_date"])
        self.assertIsNone(beta["issue_size"])
        self.assertIsNone(beta["subscription"])
        self.assertEqual(beta["status"], "upcoming")

    def test_missing_table_gives_no_rows(self):
        source = dict(SOURCE, table_selector="table#nope")
        self.assertEqual(scrape.parse_table(fixture(), source, "2026-11-12"), [])

    def test_output_passes_the_validator(self):
        import validate

        doc = {"updated_at": "2026-11-12T09:30:00+00:00", "source": "Fixture", "ipos": self.ipos}
        self.assertEqual(validate.validate_ipos(doc), [])


NEXT_SOURCE = {
    "name": "Fixture next",
    "url": "https://example.com/ipo",
    "parser": "next_data",
    "detail_url": "https://example.com/ipo/",
    "max_age_days": 30,
}


class ParseNextDataTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "fixtures", "next_data.html"), encoding="utf-8") as f:
            self.all = scrape.parse_next_data(f.read(), NEXT_SOURCE, "2026-11-12")
        self.ipos = [i for i in self.all if not i.get("_archived")]
        self.by_id = {i["id"]: i for i in self.ipos}

    def test_old_issues_are_kept_only_as_archived(self):
        self.assertEqual([i["id"] for i in self.all if i.get("_archived")], ["old-co"])

    def test_keeps_dated_and_recent_only(self):
        self.assertEqual(
            sorted(self.by_id), ["closed-co", "dated-upcoming", "listed-sme", "open-co"]
        )

    def test_listed_entry(self):
        ipo = self.by_id["listed-sme"]
        self.assertEqual(ipo["type"], "sme")
        self.assertEqual(ipo["status"], "listed")
        self.assertEqual(ipo["listing_date"], "2026-11-11")  # epoch ms read in India time
        self.assertEqual(ipo["offer_price"], {"min": 66, "max": 66})
        self.assertEqual(ipo["list_price"], 52.8)
        self.assertEqual(ipo["subscription"], "12.09x")
        self.assertEqual(ipo["source_url"], "https://example.com/ipo/listed-sme-ipo")

    def test_statuses_and_price_band(self):
        self.assertEqual(self.by_id["open-co"]["status"], "open")
        self.assertEqual(self.by_id["open-co"]["offer_price"], {"min": 100, "max": 105})
        self.assertEqual(self.by_id["open-co"]["lot_size"], 140)
        self.assertEqual(self.by_id["dated-upcoming"]["status"], "upcoming")
        self.assertEqual(self.by_id["closed-co"]["status"], "closed")
        self.assertIsNone(self.by_id["closed-co"]["list_price"])

    def test_page_without_data_gives_nothing(self):
        self.assertEqual(scrape.parse_next_data("<html></html>", NEXT_SOURCE, "2026-11-12"), [])

    def test_output_passes_the_validator(self):
        import validate

        doc = {"updated_at": "2026-11-12T09:30:00+00:00", "source": "Fixture", "ipos": self.ipos}
        self.assertEqual(validate.validate_ipos(doc), [])


FILINGS = {
    "name": "Fixture filings",
    "url": "https://example.gov/filings",
    "stage": "DRHP",
    "type": "mainboard",
    "max_age_days": 90,
}


class ParseFilingsTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "fixtures", "filings.html"), encoding="utf-8") as f:
            self.entries = scrape.parse_filings(f.read(), FILINGS, "2026-11-12")

    def test_clean_filing_title(self):
        self.assertEqual(scrape.clean_filing_title("Acme Ltd.- RHP Acme Ltd. - Abridged"), "Acme Ltd.")
        self.assertEqual(scrape.clean_filing_title("ACME STEELS LIMITED - DRHP"), "Acme Steels Limited")
        self.assertEqual(scrape.clean_filing_title("Hi-Tech Gears Limited – UDRHP-1"), "Hi-Tech Gears Limited")
        self.assertEqual(scrape.clean_filing_title("Acme Limited : Addendum to RHP"), "Acme Limited")
        self.assertEqual(scrape.clean_filing_title("ACME LIMITED - Notice to Investors"), "Acme Limited")
        self.assertIsNone(scrape.clean_filing_title(" - DRHP"))

    def test_one_entry_per_company_newest_first(self):
        self.assertEqual(
            [e["id"] for e in self.entries],
            ["alpha-traveltech-limited", "beta-coated-and-special-steels-limited"],
        )

    def test_entry_fields(self):
        alpha, beta = self.entries
        self.assertEqual(alpha["expected"], "DRHP filing, 9 Nov 2026")
        self.assertEqual(alpha["stage"], "DRHP")
        self.assertEqual(alpha["filed_date"], "2026-11-09")
        self.assertEqual(alpha["source_url"], "https://example.gov/filings/alpha-udrhp_1.html")
        self.assertEqual(beta["name"], "Beta Coated And Special Steels Limited")
        # relative link falls back to the list page
        self.assertEqual(beta["source_url"], FILINGS["url"])
        self.assertIsNone(beta["exchange"])

    def test_output_passes_the_validator(self):
        import validate

        doc = {"updated_at": "2026-11-12T09:30:00+00:00", "source": "Fixture", "ipos": self.entries}
        self.assertEqual(validate.validate_coming_soon(doc), [])


class KnownCompanyTests(unittest.TestCase):
    def test_company_key(self):
        self.assertEqual(scrape.company_key("Bombay Coated & Special Steels"), "bombay coated and special steels")
        self.assertEqual(scrape.company_key("SFC Environmental Technologies Ltd."), "sfc environmental technologies")

    def test_is_known(self):
        known = {"bombay coated and special steels", "bls polymers", "tata", "zetwerk"}
        self.assertTrue(scrape.is_known("Zetwerk Manufacturing Businesses Limited", known))
        self.assertTrue(scrape.is_known("Bombay Coated And Special Steels Limited", known))
        self.assertTrue(scrape.is_known("BLS Polymers Limited", known))
        # a longer legal name still matches a two-word-or-more short name
        self.assertTrue(scrape.is_known("BLS Polymers India Limited", known))
        # a short one-word name must match exactly
        self.assertFalse(scrape.is_known("Tata Capital Limited", known))
        self.assertFalse(scrape.is_known("Carlsberg India Limited", known))


class UnchangedTests(unittest.TestCase):
    def test_same_content_is_unchanged(self):
        ipos = [{"id": "a"}]
        existing = {"updated_at": "old", "source": "S", "ipos": [{"id": "a"}]}
        self.assertTrue(scrape.is_unchanged(existing, ipos, "S"))

    def test_changes_are_detected(self):
        existing = {"updated_at": "old", "source": "S", "ipos": [{"id": "a"}]}
        self.assertFalse(scrape.is_unchanged(existing, [{"id": "b"}], "S"))
        self.assertFalse(scrape.is_unchanged(None, [{"id": "a"}], "S"))

    def test_sample_data_is_always_replaced(self):
        existing = {"source": "S", "sample": True, "ipos": [{"id": "a"}]}
        self.assertFalse(scrape.is_unchanged(existing, [{"id": "a"}], "S"))


if __name__ == "__main__":
    unittest.main()
