#!/usr/bin/env python3
"""Follow original post-descriptor startup and first cycle with synthetic status."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import struct
from pathlib import Path

from emulate_startup_init import make_cpu, execute, SHA

ROOT = Path(__file__).resolve().parents[2]
TABLES = ((0x200000, 400, 'scalar'), (0x200190, 260, 'stretch'), (0x200294, 400, 'capture'))
MILESTONES = {0x77DE: 'after_vector_maintenance', 0x77E8: 'after_security_helper',
              0x77EC: 'after_peripheral_setup', 0x77F0: 'after_config_restore',
              0x77FA: 'after_default_initializer', 0x7836: 'startup_wait',
              0x78E4: 'dispatcher', 0x50F0: 'first_control', 0x4D38: 'scalar_entry'}


def run(raw, spec):
    import unicorn
    manifest = json.loads((ROOT / 'audit/data/reviewed_instruction_ranges.json').read_text())
    if manifest['raw_sha256'] != SHA:
        raise ValueError('instruction evidence identity changed')
    ranges = tuple((int(r['start'], 0), int(r['end'], 0)) for r in manifest['ranges'])
    ranges += ((0x200C84, 0x200C92), (0x200C94, 0x200CEC), (0x200CFC, 0x200D20))
    cpu, arm, visited, _ = make_cpu(raw, ranges)
    for address, size in ((0, 0x1000), (0x100000, 0x10000), (0xFFFA0000, 0x1000),
                           (0xFFFC0000, 0x1000), (0xFFFD8000, 0x1000), (0xFFFE0000, 0x1000)):
        cpu.mem_map(address, size)
    page = bytearray(raw[:128])
    if spec['vector_match']:
        page[4:8] = ((int.from_bytes(raw[4:8], 'little')+0x1000) & 0xFFFFFFFF).to_bytes(4, 'little')
    cpu.mem_write(0, bytes(page)); cpu.mem_write(0x104000, raw)
    config = bytearray(raw[0x96E8-0x4000+0x6CC:0x96E8-0x4000+0x6F8])
    config[0] = 0xA5 if spec['config_accepted'] else 0
    config[0x21] = 1
    cpu.mem_write(0x10FF00, bytes(config))
    execute(cpu, arm, 0x4114)
    original = {name: bytes(cpu.mem_read(a, size)) for a, size, name in TABLES}
    for address, value in ((0xFFFFFF68, 1), (0xFFFFF110, 0x15),
                           (0xFFFFF43C, 0x800 | (spec['pin17'] << 17)),
                           (0xFFFE0010, 0x30 if spec['spi_ready'] else 0)):
        cpu.mem_write(address, struct.pack('<I', value))
    visited.clear()
    tables = []; milestones = []; counts = Counter(); writes = Counter()
    commands = []; scalar_reads = []; injections = []; uscr_reads = []
    scalar_entry = {}
    stop = None
    def hashes():
        return {name: hashlib.sha256(cpu.mem_read(a, size)).hexdigest() for a, size, name in TABLES}
    def code(_, address, size, user):
        nonlocal stop
        counts[address] += 1
        if address in MILESTONES and counts[address] == 1:
            milestones.append(dict(site=hex(address), label=MILESTONES[address], tables_sha256=hashes(),
                                   stack_pointer=hex(cpu.reg_read(arm.UC_ARM_REG_SP))))
        if address == 0x4D38:
            scalar_entry.update(selector_r1=cpu.reg_read(arm.UC_ARM_REG_R1),
                                enable=cpu.mem_read(0x200432, 1)[0], step=cpu.mem_read(0x200433, 1)[0],
                                offset=cpu.mem_read(0x200434, 1)[0], mode=cpu.mem_read(0x200425, 1)[0],
                                refresh=cpu.mem_read(0x200426, 1)[0])
        if address == 0x7836 and spec['wait_event'] and not injections:
            cpu.mem_write(0x200718, b'\1')
            injections.append(dict(site='0x7836', address='0x200718', value=1,
                                   kind='explicit external software event, not an interrupt simulation'))
        if address == 0x78E4 and counts[address] == 2:
            stop = 'second_dispatcher_after_first_cycle'
            cpu.emu_stop()
    def write(_, access, address, size, value, user):
        nonlocal stop
        pc = cpu.reg_read(arm.UC_ARM_REG_PC)
        writes[(pc, address, size)] += 1
        if address < 0x200424 and address+size > 0x200000:
            tables.append(dict(site=hex(pc), address=hex(address), size=size, value=hex(value)))
        if address == 0xFFFFFF64:
            commands.append(dict(site=hex(pc), value=hex(value)))
        if address == 0xFFFFFD00:
            stop = 'reset_request'
            cpu.emu_stop()
    def read(_, access, address, size, value, user):
        pc = cpu.reg_read(arm.UC_ARM_REG_PC)
        if address == 0xFFFC0000:
            cpu.mem_write(address, struct.pack('<I', spec['uscr_read']))
            uscr_reads.append(dict(site=hex(pc), supplied=hex(spec['uscr_read'])))
        if pc in (0x4E82, 0x4ABC, 0x4CEC):
            byte = cpu.mem_read(address, 1)[0]
            scalar_reads.append(dict(site=hex(pc), address=hex(address), byte=byte,
                                     signed=byte if byte < 128 else byte-256))
    cpu.hook_add(unicorn.UC_HOOK_CODE, code)
    cpu.hook_add(unicorn.UC_HOOK_MEM_WRITE, write)
    cpu.hook_add(unicorn.UC_HOOK_MEM_READ, read)
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    cpu.emu_start(0x77B9, 0x3F00, count=30000)
    if stop is None:
        stop = 'instruction_budget'
    if spec['spi_ready'] and spec['wait_event']:
        if stop != 'second_dispatcher_after_first_cycle' or counts[0x50F0] != 1 or counts[0x4D38] != 1:
            raise ValueError(('ready startup did not reach first control cycle', spec, stop,
                              hex(cpu.reg_read(arm.UC_ARM_REG_PC)), dict(counts)))
    elif stop != 'instruction_budget':
        raise ValueError('blocked case unexpectedly completed')
    expected_prefix = bytearray(raw[:128])
    for i in range(1, 6):
        expected_prefix[4*i:4*i+4] = ((int.from_bytes(raw[4*i:4*i+4], 'little')+0x1000) & 0xFFFFFFFF).to_bytes(4, 'little')
    after = {name: bytes(cpu.mem_read(a, size)) for a, size, name in TABLES}
    expected_scalar = original['scalar'] if spec['vector_match'] else bytes(expected_prefix)+original['scalar'][128:]
    if after['scalar'] != expected_scalar or any(after[n] != original[n] for n in ('stretch', 'capture')):
        raise ValueError(('unexpected restoration or other table mutation', spec))
    if len(tables) != (0 if spec['vector_match'] else 37):
        raise ValueError('unexpected lookup-region store count')
    return dict(inputs=spec, outcome=stop, stop_pc=hex(cpu.reg_read(arm.UC_ARM_REG_PC)),
                stop_sp=hex(cpu.reg_read(arm.UC_ARM_REG_SP)), scalar_entry=scalar_entry,
                scalar_bypass_visits=counts[0x4F96],
                initial_tables_sha256={n: hashlib.sha256(b).hexdigest() for n, b in original.items()},
                final_tables_sha256=hashes(), milestones=milestones, table_writes=tables,
                table_write_count=len(tables), first_control_calls=counts[0x50F0], scalar_calls=counts[0x4D38],
                lookup_reads=scalar_reads, software_event_injections=injections, uscr_reads=uscr_reads,
                flash_command_requests=commands, visited=[hex(a) for a in sorted(visited)],
                repeated_site_counts=[dict(site=hex(a), count=n) for a, n in sorted(counts.items()) if n > 100],
                final_scalar_mode=cpu.mem_read(0x200425, 1)[0],
                final_config_mode=cpu.mem_read(0x2006ED, 1)[0],
                cpu_store_count=sum(writes.values()))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    specs = [dict(vector_match=v, config_accepted=c, pin17=p, uscr_read=u, spi_ready=True, wait_event=True)
             for v, c, p, u in itertools.product((False, True), (False, True), (0, 1), (0, 0xFFFFFFFF))]
    base = dict(vector_match=False, config_accepted=False, pin17=0, uscr_read=0, spi_ready=True, wait_event=True)
    specs += [base | dict(spi_ready=False), base | dict(wait_event=False)]
    cases = [run(raw, s) for s in specs]
    doc = dict(format='quadzilla-startup-table-lifetime-v1', raw_sha256=SHA, cases=cases,
               ready_cases=16, blocked_cases=2,
               limits=['original descriptor init followed by original 0x77B8 setup and selected first main cycles',
                       'ARM reset/clock setup, banked exception state, interrupt delivery and hardware timing are not modeled',
                       'page zero, physical application/config views, flash/SPI status, PIO pins and USART command reads are explicit synthetic inputs',
                       'optional software event sets 0x200718 at its first wait read; no interrupt handler is substituted',
                       'no transfer helper or other function result is stubbed; DMA does not populate receive buffers',
                       'blocked runs stop at an instruction budget, not a simulated timeout or real reset',
                       'later cycles, other config values, all remap states and external writers remain outside this sample',
                       'all flash commands target emulator memory; no physical device, host flash operation or firmware-file modification'])
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print('16 completed first cycles; 2 instruction-budget waits; blocked PCs: '+
          ', '.join(c['stop_pc'] for c in cases if c['outcome'] == 'instruction_budget'))


if __name__ == '__main__':
    main()
