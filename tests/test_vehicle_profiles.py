import importlib.util
import json
import unittest

from tests._paths import ROOT

spec = importlib.util.spec_from_file_location("diff_profiles", ROOT / "tools" / "diff_profiles.py")
dp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dp)


def load(name):
    with open(ROOT / "vehicles" / f"vehicle_{name}.json", encoding="utf-8-sig") as fh:
        return dp.extract_aids(json.load(fh))


class VehicleProfiles(unittest.TestCase):
    def test_fourteen_profiles_shipped(self):
        self.assertEqual(len(list((ROOT / "vehicles").glob("vehicle_*.json"))), 14)

    def test_union_is_117_unique_aids(self):
        union = set()
        for path in (ROOT / "vehicles").glob("vehicle_*.json"):
            with open(path, encoding="utf-8-sig") as fh:
                union |= set(dp.extract_aids(json.load(fh)))
        self.assertEqual(len(union), 117)

    def test_qztest_only_aids(self):
        self.assertEqual(sorted(set(load("qztest")) - set(load("v2_dodge9802"))), [145, 181])

    def test_boost_fueling_curve(self):
        aids = load("v2_dodge9802")
        curve = range(113, 137)
        self.assertTrue(all(a in aids for a in curve))
        self.assertTrue(all(aids[a]["minValue"] == 50 and aids[a]["maxValue"] == 150 for a in curve))


if __name__ == "__main__":
    unittest.main()
