"""Pin the source-bound startup layout and bounded execution evidence."""
import json
import unittest

from tests._paths import ROOT


DATA = ROOT / "audit/data"
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


class StartupVectorClock(unittest.TestCase):
    def test_copy_and_mmio_execution_artifact(self):
        run = json.loads((DATA / "startup_init_emulation.json").read_text())
        self.assertEqual(run["raw_sha256"], SHA)
        self.assertEqual(run["descriptor_copy"], {
            "initialized_bytes": 2208, "zeroed_bytes": 994,
            "executable_template_bytes": 164, "visited_instruction_starts": 46,
        })
        self.assertEqual(run["clock_setup"]["visited_instruction_starts"], 57)
        self.assertEqual(run["clock_setup"]["aic_fallback_vector_words"], 31)
        writes = {(int(w["address"], 0), int(w["value"], 0))
                  for w in run["clock_setup"]["mmio_writes"]}
        self.assertTrue({(0xFFFFFC20, 0x601), (0xFFFFFC2C, 0x481C0E),
                         (0xFFFFFC30, 4), (0xFFFFFC30, 7),
                         (0xFFFFFD44, 0x8000)} <= writes)

    def test_literal_pools_and_clock_ratio(self):
        run = json.loads((DATA / "startup_init_emulation.json").read_text())
        pools = run["literal_pools"]
        self.assertEqual([(int(pools[name]["start"], 0), len(pools[name]["words"]))
                          for name in ("arm_startup", "descriptor_loop", "clock_setup")],
                         [(0x40F8, 7), (0x4144, 2), (0x41C0, 12)])
        pllr = int(pools["clock_setup"]["words"][5], 0)
        mckr = 7
        divider = pllr & 0xFF
        multiplier = ((pllr >> 16) & 0x7FF) + 1
        prescaler = 2 if (mckr >> 2) & 7 == 1 else None
        self.assertEqual((divider, multiplier, prescaler), (14, 73, 2))
        self.assertAlmostEqual(18.4 * multiplier / divider / prescaler, 47.9714285714)


if __name__ == "__main__":
    unittest.main()
