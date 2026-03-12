#!/usr/bin/env python3
import sys, os

MAGICS = [
    (b'BZh', 'BZIP2 header'),
    (b'1AY&SY', 'BZIP2 block magic'),
    (b'PK\x03\x04', 'ZIP local header'),
    (b'MSCF', 'CAB header'),
    (b'7z\xBC\xAF\x27\x1C', '7-Zip header'),
    (b'Rar!', 'RAR header'),
    (b'\xFD7zXZ\x00', 'XZ header'),
    (b'\x1F\x8B\x08', 'GZIP header'),
    (b'\x7FELF', 'ELF header'),
    (b'MZ', 'DOS/PE header'),
    (b'ustar', 'TAR ustar marker'),
    (b'hsqs', 'SquashFS (LE)'),
    (b'sqsh', 'SquashFS (BE)'),
]

def find_all(data, sig):
    i = 0
    out = []
    while True:
        i = data.find(sig, i)
        if i < 0:
            break
        out.append(i)
        i += 1
    return out

def first_bytes(data, n=64):
    n = min(n, len(data))
    h = ' '.join(f'{b:02X}' for b in data[:n])
    a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[:n])
    return h, a

def find_ff_runs(data, min_run=256):
    runs = []
    i = 0
    L = len(data)
    while i < L:
        if data[i] == 0xFF:
            j = i+1
            while j < L and data[j] == 0xFF:
                j += 1
            if j - i >= min_run:
                runs.append((i, j - i))
            i = j
        else:
            i += 1
    return runs

def main():
    paths = sys.argv[1:] or ['overlay.bin']
    for p in paths:
        if not os.path.isfile(p):
            print(f'FILE {p}: not found')
            continue
        data = open(p, 'rb').read()
        print('='*72)
        print(f'FILE: {p}')
        print(f'SIZE: {len(data)} bytes')
        h, a = first_bytes(data, 64)
        print(f'HEAD64: {h}')
        print(f'ASCII : {a}')
        for sig, desc in MAGICS:
            hits = find_all(data, sig)
            print(f'  {desc:22s} {sig!r:20s} hits={len(hits)} first={ [hex(x) for x in hits[:6]] }')
        ff = find_ff_runs(data, 256)
        if ff:
            off, ln = ff[0]
            print(f'FF RUN: first run at {hex(off)} len={ln} (showing first only, total runs={len(ff)})')
        else:
            print('FF RUN: none >=256 bytes')
    print('='*72)

if __name__ == '__main__':
    main()