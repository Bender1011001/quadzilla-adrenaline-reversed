"""Verify raw encoding recognition and committed literal-reference coverage."""
import importlib.util
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT/'audit/tools'))
spec=importlib.util.spec_from_file_location('remaining_literals',ROOT/'audit/tools/audit_remaining_literals.py')
literal=importlib.util.module_from_spec(spec)
spec.loader.exec_module(literal)


class RemainingLiterals(unittest.TestCase):
    def test_word_load_target_encoding_excludes_other_memory_operations(self):
        self.assertEqual(literal.literal_target(0x1002,'thumb',0x4801),0x1008)
        self.assertEqual(literal.literal_target(0x1000,'thumb',0x4FFF),0x1400)
        self.assertEqual(literal.literal_target(0x1000,'arm',0xE59F0004),0x100C)
        self.assertEqual(literal.literal_target(0x1000,'arm',0xE51F0004),0x1004)
        for opcode in (0xE58F0004,0xE79F0004,0xE5DF0004,0xE49F0004):
            self.assertIsNone(literal.literal_target(0x1000,'arm',opcode))
        self.assertIsNone(literal.literal_target(0x1000,'thumb',0x6800))

    def test_every_accepted_word_has_an_encoding_derived_target(self):
        doc=json.loads((ROOT/'audit/data/remaining_literal_audit.json').read_text())
        self.assertEqual(doc['raw_sha256'],'1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((doc['literal_words'],doc['literal_bytes']),(447,1788))
        self.assertEqual(len(doc['literal_extents']),58)
        self.assertEqual(len(doc['padding_extents']),7)
        for pool in doc['literal_extents']:
            self.assertEqual(pool['bytes'],4*len(pool['words']))
            for word in pool['words']:
                self.assertTrue(word['load_sites'])
                for ref in word['load_sites']:
                    self.assertEqual(literal.literal_target(int(ref['site'],0),ref['isa'],int(ref['opcode'],0)),int(word['address'],0))


if __name__=='__main__':unittest.main()
