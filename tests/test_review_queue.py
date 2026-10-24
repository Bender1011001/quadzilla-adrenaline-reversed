"""Check queue completeness, provenance, and validity of its graph paths."""
import hashlib
import json
import unittest
from tests._paths import ROOT


class ReviewQueue(unittest.TestCase):
    def test_complete_queue_with_valid_paths(self):
        path = ROOT / "audit/data/execution_entry_catalog.json"
        catalog = json.loads(path.read_text())
        queue = json.loads((ROOT / "audit/data/offline_review_queue.json").read_text())
        self.assertEqual(queue["catalog_lf_text_sha256"], hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest())
        entries = {row["entry"]: row for row in catalog["entries"]}
        self.assertEqual(len(queue["queue"]), 42)
        self.assertEqual({row["entry"] for row in queue["queue"]},
                         {ea for ea, row in entries.items() if not row["semantics"]})
        for row in queue["queue"]:
            if row["anchor_path"] is None:
                self.assertIsNone(row["undirected_call_distance"])
                continue
            route = row["anchor_path"]
            self.assertIn(route[0], queue["anchors"])
            self.assertEqual(route[-1], row["entry"])
            self.assertEqual(len(route)-1, row["undirected_call_distance"])
            for a, b in zip(route, route[1:]):
                self.assertTrue(b in entries[a]["calls"]["outgoing"] or a in entries[b]["calls"]["outgoing"])


if __name__ == "__main__":
    unittest.main()
