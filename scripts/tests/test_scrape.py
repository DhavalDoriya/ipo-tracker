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
