#!/usr/bin/env python3
"""Execute vector-page maintenance and its overlap with the scalar table."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from emulate_startup_init import make_cpu, execute, SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from model_scalar_telemetry import calculate

RANGES = ((0x4114, 0x4144), (0x8530, 0x854A), (0x854C, 0x8562),
          (0x73E4, 0x742E), (0x6B20, 0x6B44), (0x7498, 0x74B2), (0x74B4, 0x74C2),
          (0x200C84, 0x200C92), (0x200C94, 0x200CEC),
          (0x4D38, 0x5016), (0x8564, 0x8678))


def run_case(raw, mode):
    import unicorn
    cpu, arm, visited, mmio = make_cpu(raw, RANGES)
    cpu.mem_map(0, 0x1000)
    cpu.mem_map(0x104000, 0x8000)
    cpu.mem_write(0x104000, raw)
    cpu.mem_protect(0x104000, 0x8000, unicorn.UC_PROT_READ)
    execute(cpu, arm, 0x4114)
    original = bytes(cpu.mem_read(0x200000, 400))
    vectors = bytearray(raw[:128] if mode == 'different_image_prefix' else b''.join(
        struct.pack('<I', 0xA0000000+4*i) for i in range(32)))
    if mode == 'match':
        vectors[4:8] = ((int.from_bytes(raw[4:8], 'little')+0x1000) & 0xFFFFFFFF).to_bytes(4, 'little')
    cpu.mem_write(0, bytes(vectors))
    cpu.mem_write(0xFFFFFF68, struct.pack('<I', 1))
    cpu.mem_write(0xFFFFF110, struct.pack('<I', 0x15))
    records = []
    def write(_, access, address, size, value, user):
        if 0x200000 <= address < 0x200190 or address < 128 or address >= 0xFFFF0000:
            records.append(dict(site=hex(cpu.reg_read(arm.UC_ARM_REG_PC)), address=hex(address), size=size, value=hex(value)))
    cpu.hook_add(unicorn.UC_HOOK_MEM_WRITE, write)
    visited.clear(); mmio.clear()
    saved = []
    for n in range(4, 12):
        reg = getattr(arm, f'UC_ARM_REG_R{n}')
        cpu.reg_write(reg, 0x12340000+n); saved.append((reg, 0x12340000+n))
    execute(cpu, arm, 0x73E4)
    if cpu.reg_read(arm.UC_ARM_REG_R0) != 0x200000 or any(cpu.reg_read(r) != v for r, v in saved):
        raise ValueError('vector path return/preservation mismatch')
    after = bytes(cpu.mem_read(0x200000, 400))
    expected = bytearray(original)
    if mode != 'match':
        expected[:128] = vectors
        for i in range(1, 6):
            expected[4*i:4*i+4] = ((int.from_bytes(raw[4*i:4*i+4], 'little')+0x1000) & 0xFFFFFFFF).to_bytes(4, 'little')
    if after != expected:
        raise ValueError('scalar-table overlap differs from original vector loop')
    ram_writes = [r for r in records if 0x200000 <= int(r['address'], 0) < 0x200190]
    staging = [r for r in records if int(r['address'], 0) < 128]
    if (len(ram_writes), len(staging)) != ((0, 0) if mode == 'match' else (37, 32)):
        raise ValueError('vector/staging write counts differ')
    commands = [r for r in records if r['address'] == '0xffffff64']
    if [r['value'] for r in commands] != ([] if mode == 'match' else ['0x5a000001']):
        raise ValueError(('flash request command differs', commands))
    vector_records = records.copy()
    vector_visited = sorted(visited)
    # A separate, controlled scalar call preserves the table but supplies its
    # other state explicitly. It is not the entire startup/main-loop path.
    c = dict(mode=0, refresh=0, response_flags=[0]*4, gate_sum=[0, 0], selector=100,
             enabled=1, base=1000, capture=2000, knots=[200, 400, 600, 800, 1000],
             coefficient=20, response=50, threshold=0, working61=10, status=0,
             percent0=50, percent1=100, cell=after[3])
    for a, value in ((0x200425, 0), (0x200426, 0), (0x200432, 1), (0x200433, 0), (0x200434, 0),
                     (0x200588, 20), (0x200BC2, 50), (0x2005B3, 0), (0x2005D7, 0), (0x2005B0, 50), (0x2005B1, 100)):
        cpu.mem_write(a, bytes([value]))
    for a, value in ((0x2005E8, 1000), (0x2005EC, 2000), (0x20046C, 10),
                     *((0x200458+4*i, v) for i, v in enumerate(c['knots']))):
        cpu.mem_write(a, struct.pack('<I', value))
    cpu.mem_write(0x203000, struct.pack('<I', 0))
    cpu.reg_write(arm.UC_ARM_REG_R1, 100); cpu.reg_write(arm.UC_ARM_REG_R3, 3)
    scalar_reads = []
    def read(_, access, address, size, value, user):
        if cpu.reg_read(arm.UC_ARM_REG_PC) == 0x4E82:
            scalar_reads.append(dict(address=hex(address), size=size))
    cpu.hook_add(unicorn.UC_HOOK_MEM_READ, read)
    execute(cpu, arm, 0x4D38)
    reference = calculate(c)
    if cpu.reg_read(arm.UC_ARM_REG_R0) != reference['return'] or scalar_reads != [dict(address='0x200003', size=1)]:
        raise ValueError('scalar did not consume the overwritten table cell as modeled')
    return dict(mode=mode, synthetic_page0_hex=bytes(vectors).hex(),
                initial_table_sha256=hashlib.sha256(original).hexdigest(),
                after_table_sha256=hashlib.sha256(after).hexdigest(),
                changed_offsets=[i for i, (a, b) in enumerate(zip(original, after)) if a != b],
                unchanged_suffix=after[128:] == original[128:], ram_word_writes=len(ram_writes),
                synthetic_flash_staging_writes=len(staging), vector_writes=vector_records,
                vector_path_visited=[hex(a) for a in vector_visited],
                scalar_cell_before=original[3], scalar_cell_after=after[3],
                scalar_cell_signed=after[3] if after[3] < 128 else after[3]-256,
                scalar_reads=scalar_reads, scalar_reference=reference,
                scalar_return=cpu.reg_read(arm.UC_ARM_REG_R0))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    cases = [run_case(raw, mode) for mode in ('match', 'different_sentinel', 'different_image_prefix')]
    doc = dict(format='quadzilla-vector-table-alias-v1', raw_sha256=SHA, cases=cases,
               limits=['original descriptor initializer, vector helper, mask wrapper and copied flash helpers execute',
                       'page zero and physical application view are explicit synthetic inputs; actual remap/bootloader state is unknown',
                       'flash ready/status and AIC mask are plain memory; no erase/program/interrupt hardware behavior modeled',
                       'flash destination writes are emulator staging only; no host device or firmware file is changed',
                       'later scalar call supplies other state directly and does not execute the full remaining startup',
                       'subsequent restoration, all writers, live branch frequency and physical output remain unproven'])
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print([(c['mode'], c['ram_word_writes'], c['scalar_cell_signed'], hex(c['scalar_return'])) for c in cases])


if __name__ == '__main__':
    main()
