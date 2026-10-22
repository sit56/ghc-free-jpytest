import json
import tempfile
import unittest
from pathlib import Path

from scripts.update_rate import read_observations, update


class UpdateRateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "data" / "rates.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_adds_observation(self):
        observation = {"date": "2026-10-21", "usd_jpy": 151.25}
        self.assertTrue(update(self.data_file, fetch=lambda: observation))
        self.assertEqual(json.loads(self.data_file.read_text()), [observation])

    def test_skips_duplicate_date(self):
        existing = [{"date": "2026-10-21", "usd_jpy": 151.25}]
        self.data_file.parent.mkdir(parents=True)
        self.data_file.write_text(json.dumps(existing))
        self.assertFalse(update(self.data_file, fetch=lambda: existing[0]))
        self.assertEqual(json.loads(self.data_file.read_text()), existing)

    def test_sorts_new_observation_by_date(self):
        older = {"date": "2026-10-20", "usd_jpy": 150.0}
        newer = {"date": "2026-10-21", "usd_jpy": 151.25}
        self.assertTrue(update(self.data_file, fetch=lambda: newer))
        self.assertTrue(update(self.data_file, fetch=lambda: older))
        self.assertEqual(read_observations(self.data_file), [older, newer])

    def test_rejects_duplicate_or_unsorted_existing_dates(self):
        self.data_file.parent.mkdir(parents=True)
        self.data_file.write_text(json.dumps([
            {"date": "2026-10-21", "usd_jpy": 151.25},
            {"date": "2026-10-20", "usd_jpy": 150.0},
        ]))
        with self.assertRaisesRegex(ValueError, "ascending order"):
            read_observations(self.data_file)


if __name__ == "__main__":
    unittest.main()
