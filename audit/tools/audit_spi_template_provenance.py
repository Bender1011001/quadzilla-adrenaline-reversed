#!/usr/bin/env python3
"""Resolve two code-like initialized windows through original SPI setup paths."""
import argparse
import hashlib
import json
from pathlib import Path

from emulate_capture_parser import ParserRunner
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]
DATA_SOURCE, DATA_START, DATA_LENGTH = 0x96E8, 0x200000, 0x8A0


def source_address(address):
    if not DATA_START <= address < DATA_START + DATA_LENGTH:
        raise ValueError('outside initialized SRAM copy')
    return DATA_SOURCE + address - DATA_START


def initialized(raw, address, count):
    source_address(address + count - 1)
    offset = source_address(address) - 0x4000
    return raw[offset:offset + count]


class ProvenanceRunner(ParserRunner):
    def __init__(self, raw):
        self.window_accesses = []
        super().__init__(raw)

    def record_read(self, cpu, access, address, size, value, user):
        super().record_read(cpu, access, address, size, value, user)
        if address < 0x2006AE and address + size > 0x200690:
            self.window_accesses.append({'kind': 'read', 'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                         'address': hex(address), 'size': size})

    def record_write(self, cpu, access, address, size, value, user):
        super().record_write(cpu, access, address, size, value, user)
        if address < 0x2006AE and address + size > 0x200690:
            self.window_accesses.append({'kind': 'write', 'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                         'address': hex(address), 'size': size, 'value': hex(value)})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    discovery = json.loads((ROOT / 'audit/data/execution_discovery_audit.json').read_text())
    if discovery['raw_sha256'] != SHA:
        raise ValueError('discovery identity mismatch')
    # Validate the initialized-data descriptor, rather than assuming a mapping.
    descriptor = [int.from_bytes(raw[a-0x4000:a-0x4000+4], 'little') for a in (0x96C4, 0x96C8, 0x96CC)]
    # Descriptor field order is checked against the source below before any SRAM interpretation.
    if descriptor != [DATA_LENGTH, DATA_START, DATA_SOURCE]:
        raise ValueError(('initialized-data descriptor changed', descriptor))
    regions = [(0x200690, 4, 'RXB1 interrupt-clear command'),
               (0x200694, 9, 'RXB0 read command and dummy clock bytes'),
               (0x20069D, 3, 'zero gap between bounded command extents'),
               (0x2006A0, 14, 'RXB1 read command and dummy clock bytes')]
    windows = []
    for runtime, value in ((0x200693, 0x9200), (0x20069F, 0x9400)):
        source = source_address(runtime)
        candidate = next(row for row in discovery['code_address_data_windows'] if int(row['source'], 0) == source)
        data = initialized(raw, runtime, 4)
        if int.from_bytes(data, 'little') != value:
            raise ValueError('code-like window changed')
        parts = []
        for start, count, role in regions:
            lo, hi = max(start, runtime), min(start + count, runtime + 4)
            if lo < hi:
                parts.append({'start': hex(lo), 'end_exclusive': hex(hi), 'role': role,
                              'bytes': initialized(raw, lo, hi-lo).hex()})
        if sum(int(r['end_exclusive'], 0)-int(r['start'], 0) for r in parts) != 4:
            raise ValueError('unaccounted window bytes')
        windows.append({'image_source': hex(source), 'runtime': hex(runtime), 'bytes': data.hex(),
                        'apparent_code_address': hex(value), 'discovery_candidate': candidate,
                        'parts': parts, 'disposition': 'overlapping SPI data extents; no code-pointer consumer established'})
    runner = ProvenanceRunner(raw)
    cases = []
    specs = [('rx0_start_ready', 0, 0, 0x800, 0x30, 0x6B9C, 0x200694, 9),
             ('rx1_start_ready', 0, 0, 0x808, 0x30, 0x6B9C, 0x2006A0, 14),
             ('rx0_start_blocked', 0, 0, 0x800, 0, 0x6B9C, 0x200694, 9),
             ('rx1_start_blocked', 0, 0, 0x808, 0, 0x6B9C, 0x2006A0, 14),
             ('rx0_clear_ready', 2, 1, 0x818, 0x30, 0x6B64, 0x20068C, 4),
             ('rx1_clear_ready', 2, 2, 0x818, 0x30, 0x6B64, 0x200690, 4)]
    for name, state, kind, pins, status, helper, pointer, count in specs:
        runner.window_accesses.clear()
        result = runner.sample(name, state=state, kind=kind, pins=pins, status=status)
        transfers = [t for t in result['calls'] if int(t['entry'], 0) == helper]
        if len(transfers) != 1:
            raise ValueError(('expected unique transfer', name))
        call = transfers[0]
        actual = [int(a, 0) for a in call['args']]
        observed = (actual[2], actual[3]) if helper == 0x6B9C else (actual[1], actual[2])
        if observed != (pointer, count):
            raise ValueError(('transfer argument mismatch', name))
        tx = [w for w in result['mmio_writes'] if w['address'] == '0xfffe0108']
        counts = [w for w in result['mmio_writes'] if w['address'] == '0xfffe010c']
        if status:
            if len(tx) != 1 or int(tx[0]['value'], 0) != pointer or len(counts) != 1 or int(counts[0]['value'], 0) != count:
                raise ValueError(('PDC descriptor mismatch', name))
        elif tx or counts:
            raise ValueError('blocked transfer programmed TX descriptor')
        if runner.window_accesses:
            raise ValueError(('unexpected CPU window access', name, runner.window_accesses))
        result.update({'transmit_extent': {'start': hex(pointer), 'end_exclusive': hex(pointer+count),
                                          'initialized_bytes': initialized(raw, pointer, count).hex()},
                       'cpu_window_accesses': runner.window_accesses.copy(),
                       'tx_descriptor_programmed': bool(tx)})
        cases.append(result)
    doc = {'format': 'quadzilla-spi-template-provenance-v1', 'raw_sha256': SHA,
           'cpu': 'ARM926 functional surrogate', 'data_descriptor_words': [hex(v) for v in descriptor],
           'windows': windows, 'regions': [{'start': hex(a), 'end_exclusive': hex(a+n),
                                           'bytes': initialized(raw, a, n).hex(), 'role': role}
                                          for a, n, role in regions],
           'case_count': len(cases), 'cases': cases,
           'limits': ['selected original capture/transfer paths with synthetic SRAM and status flags',
                      'initialized bytes are interpreted at the programmed descriptor; no DMA engine or SPI transaction executes',
                      'no CPU read of these windows in six cases is not an exhaustive consumer or writer proof',
                      'no exclusion of synthesized addresses, runtime mutation, other aliases or interrupt interactions',
                      'no new execution entry, hardware measurement or complete firmware claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(windows)} overlapping initialized windows; {len(cases)} original-byte cases')


if __name__ == '__main__':
    main()
