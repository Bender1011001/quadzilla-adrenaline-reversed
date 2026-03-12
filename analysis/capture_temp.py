#!/usr/bin/env python3
"""
Monitor temp directory for files extracted by the self-extracting EXE.
The EXE has unzipToTemp=true, so it extracts to %TEMP% before running.

Strategy:
1. Take a snapshot of temp before running
2. Run the EXE
3. Compare to find new files
4. Copy them out before the EXE cleans up

We'll also monitor using a filesystem watcher.
"""
import os
import sys
import shutil
import time
import threading
from pathlib import Path

TEMP_DIR = os.environ.get('TEMP', os.environ.get('TMP', r'C:\Users\admin\AppData\Local\Temp'))
CAPTURE_DIR = r'extracted\captured'
EXE_PATH = r'ADR9802v2.8.4.exe'

def snapshot_temp():
    """Take a snapshot of all files in temp."""
    files = {}
    for root, dirs, filenames in os.walk(TEMP_DIR):
        for fn in filenames:
            full = os.path.join(root, fn) 
            try:
                files[full] = os.path.getmtime(full)
            except:
                pass
    return files

def monitor_loop(stop_event, before_snapshot):
    """Continuously monitor temp for new files and copy them."""
    captured = set()
    while not stop_event.is_set():
        try:
            for root, dirs, filenames in os.walk(TEMP_DIR):
                for fn in filenames:
                    full = os.path.join(root, fn)
                    if full in captured:
                        continue
                    if full not in before_snapshot:
                        # New file!
                        try:
                            rel = os.path.relpath(full, TEMP_DIR)
                            dest = os.path.join(CAPTURE_DIR, rel)
                            os.makedirs(os.path.dirname(dest), exist_ok=True)
                            shutil.copy2(full, dest)
                            size = os.path.getsize(full)
                            print(f"  CAPTURED: {rel} ({size} bytes)")
                            captured.add(full)
                        except Exception as e:
                            pass  # File might be locked/in-use
                    else:
                        # Check if modified
                        try:
                            mtime = os.path.getmtime(full)
                            if mtime > before_snapshot[full]:
                                rel = os.path.relpath(full, TEMP_DIR)
                                dest = os.path.join(CAPTURE_DIR, 'modified_' + rel.replace(os.sep, '_'))
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                shutil.copy2(full, dest)
                                print(f"  MODIFIED: {rel}")
                                captured.add(full)
                        except:
                            pass
        except:
            pass
        time.sleep(0.1)  # Check every 100ms
    
    print(f"\nTotal files captured: {len(captured)}")

def main():
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    
    # Also check for existing FirmwareUpdate dirs in temp
    for item in os.listdir(TEMP_DIR):
        full = os.path.join(TEMP_DIR, item)
        if 'firmware' in item.lower() or 'quadzilla' in item.lower():
            print(f"FOUND EXISTING: {full}")
            if os.path.isdir(full):
                for root, dirs, files in os.walk(full):
                    for f in files:
                        src = os.path.join(root, f)
                        rel = os.path.relpath(src, TEMP_DIR)
                        dest = os.path.join(CAPTURE_DIR, rel)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(src, dest)
                        print(f"  Copied: {rel} ({os.path.getsize(src)} bytes)")
            elif os.path.isfile(full):
                shutil.copy2(full, os.path.join(CAPTURE_DIR, item))
                print(f"  Copied: {item}")
    
    # Also look for any existing temp patterns from this EXE
    # The EXE might use a pattern like tmp_XXXX or similar
    for item in os.listdir(TEMP_DIR):
        full = os.path.join(TEMP_DIR, item)
        if os.path.isdir(full):
            # Check if it contains FirmwareUpdate
            fw_dir = os.path.join(full, 'FirmwareUpdate')
            if os.path.isdir(fw_dir):
                print(f"\nFOUND FirmwareUpdate in: {full}")
                for root, dirs, files in os.walk(fw_dir):
                    for f in files:
                        src = os.path.join(root, f)
                        rel = os.path.relpath(src, full)
                        dest = os.path.join(CAPTURE_DIR, rel)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(src, dest)
                        size = os.path.getsize(src)
                        print(f"  Copied: {rel} ({size} bytes)")
    
    print(f"\nDone scanning temp directory: {TEMP_DIR}")
    print(f"Capture directory: {os.path.abspath(CAPTURE_DIR)}")

if __name__ == '__main__':
    main()
