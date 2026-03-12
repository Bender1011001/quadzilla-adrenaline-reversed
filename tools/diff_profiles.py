#!/usr/bin/env python3
"""Diff all Quadzilla vehicle profiles - find hidden AIDs and build master AID database."""
import json, os, sys

def extract_aids(profile):
    """Extract all AIDs from a vehicle profile JSON."""
    aids = {}
    params = profile.get('parameters', {})
    
    # Sensors
    for s in params.get('sensors', []):
        aids[int(s['aid'])] = {
            'name': s['name'], 'section': 'sensor',
            'unit': s.get('unit',''), 'minValue': s.get('minValue',''),
            'maxValue': s.get('maxValue',''), 'multiplyFactor': s.get('multiplyFactor',''),
            'offset': s.get('offset',''), 'warningValue': s.get('warningValue',''),
            'decimalDigits': s.get('decimalDigits',''), 'formatter': s.get('formatter',''),
        }
    
    # Settings
    for s in params.get('settings', []):
        aids[int(s['aid'])] = {
            'name': s['name'], 'section': 'setting',
            'unit': s.get('unit',''), 'minValue': s.get('minValue',''),
            'maxValue': s.get('maxValue',''), 'formatter': s.get('formatter',''),
            'options': s.get('options',[]), 'toggable': s.get('toggable', False),
        }
    
    # Tuning groups
    for group in params.get('tuning', []):
        gname = group.get('name', 'unknown')
        gtype = group.get('type', 'list')
        for item in group.get('items', []):
            aids[int(item['aid'])] = {
                'name': item['name'], 'section': f"tuning:{gname}",
                'type': gtype, 'unit': item.get('unit',''),
                'minValue': item.get('minValue',''), 'maxValue': item.get('maxValue',''),
                'multiplyFactor': item.get('multiplyFactor',''),
                'formatter': item.get('formatter',''),
            }
    
    # Special entries (status indicators)
    for key in ['currentGear', 'torqueLock', 'powerLevel', 'sootReg', 'soxReg']:
        if key in params:
            s = params[key]
            aids[int(s['aid'])] = {
                'name': s['name'], 'section': 'status',
                'unit': s.get('unit',''), 'formatter': s.get('formatter',''),
            }
    
    return aids

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    
    # Load profiles
    profiles = {}
    profile_files = {
        'V2 Dodge': 'vehicle_v2_dodge9802.json',
        'QZTEST': 'vehicle_qztest.json',
        '4K': 'vehicle_v2_dodge9802_4k.json',
    }
    
    # Also try to load all downloaded vehicle profiles
    for f in os.listdir(base):
        if f.startswith('vehicle_') and f.endswith('.json') and f not in profile_files.values():
            key = f.replace('vehicle_','').replace('.json','')
            profile_files[key] = f
    
    for label, fname in profile_files.items():
        fpath = os.path.join(base, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            profiles[label] = {
                'data': data,
                'aids': extract_aids(data),
                'vehicle': data.get('vehicle', label),
                'version': data.get('version', '?'),
            }
    
    print(f"=== LOADED {len(profiles)} PROFILES ===")
    for label, p in sorted(profiles.items()):
        print(f"  {label:30s} v{p['version']:6s} {len(p['aids']):3d} AIDs  ({p['vehicle']})")
    
    # Build master AID database
    all_aids = {}
    for label, p in profiles.items():
        for aid, info in p['aids'].items():
            if aid not in all_aids:
                all_aids[aid] = {'name': info['name'], 'info': info, 'sources': []}
            all_aids[aid]['sources'].append(label)
    
    # QZTEST-only AIDs (hidden features!)
    v2_aids = profiles.get('V2 Dodge', {}).get('aids', {})
    qz_aids = profiles.get('QZTEST', {}).get('aids', {})
    
    if qz_aids:
        qz_only = {k:v for k,v in qz_aids.items() if k not in v2_aids}
        print(f"\n=== QZTEST-ONLY AIDs ({len(qz_only)}) — HIDDEN FEATURES ===")
        for aid in sorted(qz_only.keys()):
            info = qz_only[aid]
            unit = info.get('unit', '')
            rng = f"{info.get('minValue','')}-{info.get('maxValue','')}" if info.get('minValue') else ''
            print(f"  AID {aid:3d}: {info['name']:45s} {unit:6s} {rng:15s} [{info['section']}]")
    
    # Parameters that differ between profiles
    if v2_aids and qz_aids:
        print(f"\n=== PARAMETER DIFFERENCES (V2 vs QZTEST) ===")
        for aid in sorted(set(v2_aids.keys()) & set(qz_aids.keys())):
            v2n = v2_aids[aid]['name']
            qzn = qz_aids[aid]['name']
            if v2n != qzn:
                print(f"  AID {aid:3d}: V2='{v2n}' vs QZ='{qzn}'")
    
    # Complete master AID table
    print(f"\n=== MASTER AID TABLE ({len(all_aids)} unique parameters) ===")
    print(f"{'AID':>4s}  {'Name':45s} {'Unit':8s} {'Range':20s} {'Section':30s} {'Sources'}")
    print("-" * 140)
    for aid in sorted(all_aids.keys()):
        info = all_aids[aid]
        detail = info['info']
        unit = detail.get('unit', '')
        rng = ''
        if detail.get('minValue') is not None and detail.get('minValue') != '':
            rng = f"{detail.get('minValue','')}-{detail.get('maxValue','')}"
        section = detail.get('section', '')
        sources = ','.join(info['sources'])
        print(f"{aid:4d}  {info['name']:45s} {unit:8s} {rng:20s} {section:30s} {sources}")
    
    # Find gaps in AID numbering
    used = sorted(all_aids.keys())
    max_aid = max(used)
    gaps = [i for i in range(max_aid+1) if i not in all_aids]
    print(f"\n=== UNUSED AIDs (gaps in 0-{max_aid}) — {len(gaps)} undocumented ===")
    # Group consecutive gaps
    ranges = []
    start = None
    for g in gaps:
        if start is None:
            start = g
            end = g
        elif g == end + 1:
            end = g
        else:
            ranges.append((start, end))
            start = g
            end = g
    if start is not None:
        ranges.append((start, end))
    for s, e in ranges:
        if s == e:
            print(f"  AID {s}")
        else:
            print(f"  AID {s}-{e} ({e-s+1} slots)")

if __name__ == '__main__':
    main()
