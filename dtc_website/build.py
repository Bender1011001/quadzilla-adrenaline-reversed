#!/usr/bin/env python3
"""Build the DTC website by injecting the database JSON into the HTML template."""
import json, os

base = r'E:\code.projects\quadzilla_rev'

# Load DTC data
with open(os.path.join(base, 'dtc_database.json'), 'r') as f:
    dtc_data = json.load(f)

# Load HTML template
with open(os.path.join(base, 'dtc_website', 'index_template.html'), 'r', encoding='utf-8') as f:
    html = f.read()

# Inject data - compact JSON to minimize size
dtc_json = json.dumps(dtc_data, separators=(',', ':'))
html = html.replace('INJECT_DTC_DATA', dtc_json)

# Write final HTML
out_path = os.path.join(base, 'dtc_website', 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Built DTC website: {out_path}")
print(f"  DTC entries: {len(dtc_data)}")
print(f"  HTML size: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
