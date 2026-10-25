#!/usr/bin/env python3
"""Run exact receive-dispatch instructions for controlled completed USART frames."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_aid_tables import SHA
from emulate_short_value_admission import AdmissionRunner
from x2com_crc import add_crc


BASE = 0x2007C8


class ReceiveRunner(AdmissionRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x80A2, 0x81A2), (0x7B28, 0x7B38),
                                (0x7F58, 0x800A))

    def sample(self, label, kind=None, payload=b'', flags=(), good_crc=True,
               buffer=0x2007F0):
        self.setup()
        self.word(0x2007E8, buffer)
        for offset, value in flags:
            self.cpu.mem_write(BASE + offset, bytes([value]))
        if kind is None:
            frame = b''
            self.cpu.mem_write(0x200AFD, b'\x00')
        else:
            if len(payload) > 14:
                raise ValueError('frame payload is longer than 14 bytes')
            frame = add_crc(bytes([(kind << 4) | (len(payload) + 1)]) + payload)
            if not good_crc:
                frame = frame[:-1] + bytes([frame[-1] ^ 1])
            self.cpu.mem_write(buffer, frame + bytes(16 - len(frame)))
            self.cpu.mem_write(0x200AFD, b'\x01')
        self.word(0xFFFC0104, 0)
        self.cpu.mem_write(0x201000, bytes(0x100))
        self.cpu.mem_write(0x201100, b'\x00')
        self.writes.clear()
        self.visited.clear()
        self.calls.clear()
        status = self.checked_call(0x8038, [0x201000, 0x201100])
        return {'label': label, 'kind': kind, 'payload': payload.hex(),
                'frame': frame.hex(), 'good_crc': good_crc,
                'completed_buffer': hex(buffer),
                'status': status, 'parsed_count': self.cpu.mem_read(0x201100, 1)[0],
                'parsed_list_prefix': bytes(self.cpu.mem_read(0x201000, 16)).hex(),
                'state_counts': {hex(o): self.cpu.mem_read(BASE + o, 1)[0]
                                 for o in (6, 0xA, 0xD, 0x13, 0x14, 0x18, 0x19)},
                'state_flags': {hex(o): self.cpu.mem_read(BASE + o, 1)[0]
                                for o in (0, 1, 2, 3, 4, 5, 7, 8, 9,
                                          0xB, 0xC, 0xE, 0xF, 0x11, 0x12,
                                          0x16, 0x17)},
                'writes': self.writes.copy(),
                'visited_receive': [hex(a) for a in sorted(self.visited)
                                    if 0x8038 <= a < 0x81A2],
                'calls': self.calls.copy()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected firmware image')
    runner = ReceiveRunner(raw)
    cases = [
        ('no_pending', None, b'', (), True),
        ('type0', 0, bytes([9]), (), True),
        ('type1', 1, bytes([9, 1]), (), True),
        ('type2_guarded', 2, bytes([9]), (), True),
        ('type2_armed', 2, bytes([9]), ((0x11, 1), (0x12, 1)), True),
        ('type2_finish', 2, bytes([9]),
         ((0x11, 1), (0x12, 1), (4, 1), (3, 1)), True),
        ('type3', 3, bytes([9, 1]), (), True),
        ('type4', 4, bytes([9]), (), True),
        ('type5_guarded', 5, bytes([9]), (), True),
        ('type5_armed', 5, bytes([9]), ((0x16, 1), (0x17, 1)), True),
        ('type5_finish', 5, bytes([9]),
         ((0x16, 1), (0x17, 1), (5, 1), (2, 1)), True),
        ('bad_crc', 1, bytes([9, 1]), (), False),
        ('unknown_type', 6, bytes([9]), (), True),
        ('alternate_buffer', 1, bytes([9, 1]), (), True, 0x200800),
    ]
    rows = [runner.sample(*case) for case in cases]
    seen = {int(a, 0) for row in rows for a in row['visited_receive']}
    output = {'format': 'quadzilla-receive-state-emulation-v1',
              'raw_sha256': SHA, 'cpu': 'ARM926 functional surrogate',
              'emulator': 'Unicorn ' + runner.uc.__version__,
              'cases': rows, 'visited_receive_starts': [hex(a) for a in sorted(seen)],
              'limitations': ['completed frame and receive flag supplied synthetically',
                              'USART register page is passive memory',
                              'not physical transport, DMA, timing or state reachability']}
    args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(f'{len(rows)} cases, {len(seen)} receive instruction starts visited')
    for row in rows:
        print(row['label'], row['status'], row['parsed_count'], row['state_counts'])


if __name__ == '__main__':
    main()
