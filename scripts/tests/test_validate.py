import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))

import validate  # noqa: E402

GOOD = {
    "updated_at": "2026-11-12T09:30:00+00:00",
    "source": "Test",
    "ipos": [
        {
            "id": "alpha-ltd",
            "name": "Alpha Ltd",
            "type": "sme",
            "exchange": "BSE SME",
            "status": "open",
            "open_date": "2026-11-10",
            "close_date": "2026-11-12",
            "listing_date": None,
            "offer_price": {"min": 62, "max": 66},
            "list_price": None,
            "lot_size": 2000,
            "issue_size": None,
            "subscription": None,
            "subscription_breakup": None,
            "gmp": None,
            "source_url": "https://example.com/ipo",
        }
    ],
}


def broken(**changes):
    doc = copy.deepcopy(GOOD)
    doc["ipos"][0].update(changes)
    return doc


class ValidateIposTests(unittest.TestCase):
    def test_good_document_passes(self):
        self.assertEqual(validate.validate_ipos(GOOD), [])

    def test_empty_list_fails(self):
        self.assertTrue(validate.validate_ipos(dict(GOOD, ipos=[])))

    def test_missing_updated_at_fails(self):
        doc = copy.deepcopy(GOOD)
        del doc["updated_at"]
        self.assertTrue(validate.validate_ipos(doc))

    def test_bad_fields_fail(self):
        cases = {
            "id": "Not A Slug",
            "name": "",
            "status": "live",
            "type": "main",
            "open_date": "12/11/2026",
            "offer_price": {"min": 70, "max": 66},
            "lot_size": "2000",
            "source_url": "http://example.com",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                self.assertTrue(validate.validate_ipos(broken(**{field: value})))

    def test_duplicate_ids_fail(self):
        doc = copy.deepcopy(GOOD)
        doc["ipos"].append(copy.deepcopy(doc["ipos"][0]))
        self.assertTrue(any("duplicate" in e for e in validate.validate_ipos(doc)))


class RepoDataTests(unittest.TestCase):
    def test_committed_data_is_valid(self):
        self.assertEqual(validate.validate_all(os.path.join(ROOT, "data")), [])

    def test_missing_directory_fails(self):
        self.assertTrue(validate.validate_all(os.path.join(ROOT, "no-such-dir")))


if __name__ == "__main__":
    unittest.main()
