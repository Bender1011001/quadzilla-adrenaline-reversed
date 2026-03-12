#!/usr/bin/env python3
"""
Run the self-extracting ADR9802 EXE while monitoring for extracted files.
Uses a background thread to continuously scan temp for new files.
"""
import os
import sys
import shutil
import time
import subprocess
import threading
from datetime import datetime

TEMP_DIR = os.environ.get('TEMP', r'C:\Users\admin\AppData\Local\Temp')
CAPTURE_DIR = r'extracted\from_exe'
EXE_PATH = os.path.abspath(r'ADR9802v2.8.4.exe')

def get_all_files(directory):
    """Get all files with their mtimes."""
    result = {}
    try:
        for root, dirs, files in os.walk(directory):
            for f in files:
                full = os.path.join(root, f)
                try:
                    result[full] = os.path.getmtime(full)
                except:
                    pass
    except:
        pass
    return result

def main():
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    
    print(f"Taking snapshot of TEMP: {TEMP_DIR}")
    before = get_all_files(TEMP_DIR)
    print(f"  {len(before)} files in temp before launch")
    
    print(f"\nLaunching: {EXE_PATH}")
    print(f"  (The EXE will extract to temp and try to run the updater)")
    print(f"  (Close the updater window when it appears)")
    
    # Launch the EXE
    proc = subprocess.Popen([EXE_PATH], shell=False)
    
    # Monitor for new files
    captured = {}
    print(f"\nMonitoring temp for new files...")
    
    start_time = time.time()
    while time.time() - start_time < 60:  # Monitor for 60 seconds
        time.sleep(0.5)
        
        after = get_all_files(TEMP_DIR)
        
        for path, mtime in after.items():
            if path not in before and path not in captured:
                # New file!
                try:
                    rel = os.path.relpath(path, TEMP_DIR)
                    dest = os.path.join(CAPTURE_DIR, rel)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(path, dest)
                    size = os.path.getsize(path)
                    captured[path] = size
                    print(f"  CAPTURED: {rel} ({size:,} bytes)")
                except Exception as e:
                    print(f"  FAILED: {path}: {e}")
        
        # Check if process is still running
        if proc.poll() is not None:
            # Process exited, do one more scan
            time.sleep(1)
            after = get_all_files(TEMP_DIR)
            for path, mtime in after.items():
                if path not in before and path not in captured:
                    try:
                        rel = os.path.relpath(path, TEMP_DIR)
                        dest = os.path.join(CAPTURE_DIR, rel)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(path, dest)
                        size = os.path.getsize(path)
                        captured[path] = size
                        print(f"  CAPTURED: {rel} ({size:,} bytes)")
                    except:
                        pass
            break
    
    print(f"\n{'='*60}")
    print(f"Captured {len(captured)} files")
    total_size = sum(captured.values())
    print(f"Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"Output: {os.path.abspath(CAPTURE_DIR)}")
    
    # List what we got
    if captured:
        print(f"\nFiles captured:")
        for path, size in sorted(captured.items()):
            rel = os.path.relpath(path, TEMP_DIR)
            print(f"  {rel}: {size:,} bytes")

if __name__ == '__main__':
    main()
