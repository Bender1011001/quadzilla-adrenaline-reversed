"""Pin the device-side clamp facts cited in docs/SECURITY_ASSESSMENT.md (F5) to the committed decompile."""
import unittest

from tests._paths import ROOT  # noqa: F401  (sets sys.path)
import aid_clamps as ac

SOURCE = (ROOT / "decompiled_firmware_full.c").read_text(encoding="utf-8", errors="replace")


class DispatcherClamps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = ac.cases(ac.dispatcher_body(SOURCE))
        cls.profile = ac.load_profile(ROOT / "vehicles" / "vehicle_v2_dodge9802.json")

    def literals(self, aid):
        return ac.clamp_literals(self.cases[aid])

    def test_dispatcher_handles_57_aids_including_the_curve_and_timing_points(self):
        self.assertEqual(len(self.cases), 57)
        for aid in [85, 104, *range(113, 142)]:
            self.assertIn(aid, self.cases)

    def test_fueling_curve_points_clamp_to_the_apps_range(self):
        for aid in range(113, 122):  # stacked labels 122-136 share one body (see aid_clamps.py notes)
            assigned, compared = self.literals(aid)
            self.assertEqual(assigned, [50, 150], aid)
            self.assertIn(151, compared, aid)
            p = self.profile[aid]
            self.assertEqual((p["minValue"], p["maxValue"]), (50, 150), aid)

    def test_aid85_device_floor_is_below_the_apps_minimum(self):
        assigned, compared = self.literals(85)
        self.assertEqual(assigned, [800])
        self.assertLess(assigned[0], self.profile[85]["minValue"])  # 800 < 1200

    def test_timing_points_clamp_at_raw_300(self):
        for aid in range(137, 142):
            assigned, _ = self.literals(aid)
            self.assertEqual(assigned, [300], aid)

    def test_device_timing_limit_exceeds_the_app_for_the_two_lowest_rpm_points(self):
        def app_raw_max(aid):  # the profile mixes string and numeric values
            p = self.profile[aid]
            return round(float(p["maxValue"]) / float(p["multiplyFactor"]))

        for aid in (137, 138):
            self.assertGreater(300, app_raw_max(aid), aid)       # device 300 > app 200 / 260
        for aid in (139, 140, 141):
            self.assertEqual(app_raw_max(aid), 300, aid)         # equal

    def test_stacked_labels_yield_empty_bodies_not_fabricated_limits(self):
        self.assertEqual(self.literals(123), ([], []))


if __name__ == "__main__":
    unittest.main()
