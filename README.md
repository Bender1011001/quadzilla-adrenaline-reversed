<p align="center">
  <h1 align="center">⚡ Quadzilla Adrenaline — Reverse Engineered</h1>
  <p align="center">
    <em>Complete firmware RE, protocol documentation, and custom tuning toolkit for the Quadzilla Adrenaline inline diesel tuner</em>
  </p>
  <p align="center">
    <strong>Done entirely by AI (Claude, Anthropic — running as the "Antigravity" agent)</strong>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MCU-ARM7TDMI-blue?style=flat-square" alt="ARM7TDMI">
  <img src="https://img.shields.io/badge/Flash-48KB-green?style=flat-square" alt="48KB Flash">
  <img src="https://img.shields.io/badge/Functions-57%20decompiled-orange?style=flat-square" alt="57 Functions">
  <img src="https://img.shields.io/badge/AIDs-117%20mapped-red?style=flat-square" alt="117 AIDs">
  <img src="https://img.shields.io/badge/Protocol-X2com%20BLE-purple?style=flat-square" alt="X2com BLE">
  <img src="https://img.shields.io/badge/by-AI%20🤖-black?style=flat-square" alt="By AI">
</p>

---

## What Is This?

This repository contains the **complete reverse engineering** of the [Quadzilla Adrenaline](https://www.quadzillapower.com/) inline diesel tuner (DADR9802), targeting 1998-2002 Dodge Ram Cummins 24-valve trucks with VP44 injection pumps.

**Everything here was produced by an AI** — Claude (Anthropic), running autonomously as the "Antigravity" agent. The human provided the hardware, files, and direction. The AI performed all analysis, scripting, decompilation, and documentation.

### What We Cracked

| Component | Result |
|-----------|--------|
| 🔓 **Firmware encryption** | XOR cipher-chain — key extracted from .NET DLL, roundtrip verified |
| 🧠 **Firmware code** | 57/60 functions decompiled to **125KB of C code** |
| 📡 **BLE protocol (X2com)** | Complete: CRC-8, frame format, 6 message types, state machine |
| 🔌 **USB protocol** | 15 opcodes, 921600 baud, full flash sequence |
| 🎛️ **Parameters (AIDs)** | 117 mapped from 14 vehicle profiles — including 2 hidden |
| 📱 **iQuad app** | APK decompiled, native library (62 functions, 224KB C) |

---

## Repository Structure

```
quadzilla_rev/
├── README.md                          ← You are here
├── CONTEXT.md                         ← Technical reference (function map, protocol spec)
│
├── docs/
│   ├── QUADZILLA_RE_COMPLETE.md       ← 📖 THE MAIN DOCUMENT — full RE writeup from AI's perspective
│   ├── AID_REFERENCE.md              ← Complete parameter database (117 AIDs)
│   ├── FINDINGS.md                    ← Initial findings summary
│   ├── quadzilla_firmware_analysis.md ← Firmware architecture notes
│   └── quadzilla_custom_firmware_findings.md ← Custom firmware possibilities
│
├── tools/
│   ├── firmware_crypto.py             ← 🔑 Encrypt/decrypt firmware (XOR cipher-chain)
│   ├── quadzilla_tool.py              ← 🔌 USB serial communication tool
│   ├── analyze_binary.py              ← 🔍 Raw binary analysis (find functions, ISA, memory map)
│   ├── diff_profiles.py               ← 📊 Vehicle profile differ (finds hidden AIDs)
│   ├── analyze_firmware.py            ← Firmware structure analysis
│   └── analyze_calibration.py         ← Calibration table mapper
│
├── ghidra/
│   └── scripts/
│       ├── ghidra_decompile_all.py    ← ⭐ THE script — decompiles all 57 firmware functions
│       ├── ghidra_nuclear.py          ← Nuclear approach for mixed ARM/Thumb analysis
│       ├── ghidra_x2com.py            ← X2com library decompilation
│       └── (6 more iterative scripts) ← Earlier attempts, kept for reference
│
├── vehicles/                          ← 14 vehicle profile JSONs from Quadzilla's server
│
├── decompiled_firmware_full.c         ← 💎 All 57 firmware functions (125KB)
├── decompiled_x2com.c                 ← 💎 All 62 X2com protocol functions (224KB)
│
└── analysis/                          ← Intermediate outputs, scratch scripts, raw data
```

---

## The Main Document

**📖 [docs/QUADZILLA_RE_COMPLETE.md](docs/QUADZILLA_RE_COMPLETE.md)** — The full reverse engineering writeup, written from the AI's first-person perspective. It covers:

1. **How I got in** — 4 attack surfaces (Windows updater, encrypted firmware, Android app, native BLE library)
2. **The encryption** — Why it's not really encryption (XOR cipher-chain with key shipped alongside)
3. **Firmware architecture** — Memory map, boot sequence, 60 functions with purposes
4. **The Ghidra struggle** — What went wrong, 6 failed scripts, and the nuclear option that worked
5. **X2com BLE protocol** — Complete spec: CRC-8 (poly 0x1D), frame format, 6 message types
6. **USB serial protocol** — 15 opcodes with the full firmware flash sequence
7. **AID parameter system** — 117 tunable parameters, 4-segment architecture, hidden features
8. **Custom firmware possibilities** — 5 tiers from parameter tweaks to complete new features
9. **What I got wrong** — Honest mistakes and lessons learned

---

## Quick Start

### Decrypt Firmware
```bash
# Extract the key from X2Updater's Quadzilla.dll, then:
python tools/firmware_crypto.py decrypt FirmwareUpdate.qz decrypted.hex --key-file key.pwk

# Verify roundtrip
python tools/firmware_crypto.py verify FirmwareUpdate.qz --key-file key.pwk
```

### Talk to the Tuner (USB)
```bash
pip install pyserial

# Get module info
python tools/quadzilla_tool.py info

# Read feature codes
python tools/quadzilla_tool.py features

# Scan for responding AIDs
python tools/quadzilla_tool.py scan --start 0 --end 255
```

### Decompile the Firmware (Ghidra)
```bash
# Requires Ghidra 11.3.2 + Java 17
analyzeHeadless ghidra_project QuadzillaFW \
  -process "decrypted.hex" \
  -noanalysis \
  -postScript ghidra/scripts/ghidra_decompile_all.py
```

### Diff Vehicle Profiles
```bash
python tools/diff_profiles.py
# Outputs all 117 AIDs with names, units, ranges, and which vehicles use them
```

---

## Key Findings

### The "Encryption"
```
E[i] = P[i] ^ KEY[i % 8] ^ E[i-1]     (that's it)
```
Key is shipped inside the .NET DLL. No code signing. No integrity check. Firmware modifications flash without complaint.

### The Boost Fueling Curve (AIDs 113-136)
The tuner has a **24-point user-adjustable fuel curve indexed by boost pressure**:
```
AID 113: Fueling at 0 PSI   (50-150%)
AID 114: Fueling at 1 PSI   (50-150%)
...
AID 128: Fueling at 15 PSI  (50-150%)     ← 1 PSI resolution
AID 129: Fueling at 16 PSI  (50-150%)
AID 130: Fueling at 18 PSI  (50-150%)     ← 2 PSI resolution
...
AID 136: Fueling at 30+ PSI (50-150%)
```
100% = stock fueling. Each point is independently adjustable via BLE or USB.

### Hidden Parameters
By diffing the QZTEST diagnostic profile against the standard V2 profile, I found 2 AIDs that Quadzilla hides from regular users:
- **AID 145**: AVG MPG Reset — resets the fuel economy counter
- **AID 181**: Average MPG — reads the calculated average MPG

### 19KB of Free Flash
The firmware uses 22KB of the 48KB flash. There are **19KB of unused space** at 0xB200-0xFCFF — enough for substantial custom functionality:
- Dual-mode auto-tune (cruise MPG + max power) — ~4KB
- PID boost controller — ~1KB
- Data logger — ~3KB
- Launch control — ~1KB
- Limp mode protection — ~1KB

---

## Custom Firmware Possibilities

| Tier | What | Risk | Difficulty |
|------|------|------|-----------|
| **1** | Change AID parameters (fuel curve, limits, timing) | None | Easy |
| **2** | Edit calibration tables (fuel/timing maps) | Medium | Medium |
| **3** | Patch code (speed-based fueling, bypass checks) | High | Hard |
| **4** | New features in free flash (auto-tune, PID, logging) | High | Hard |
| **5** | Complete custom firmware (dual-mode, adaptive) | Very High | Expert |

See [docs/QUADZILLA_RE_COMPLETE.md](docs/QUADZILLA_RE_COMPLETE.md#custom) for detailed breakdowns of each tier.

---

## Hardware

| Component | Detail |
|-----------|--------|
| **Device** | Quadzilla Adrenaline DADR9802 |
| **MCU** | ARM7TDMI (mixed ARM/Thumb ISA) |
| **Flash** | 48KB (22KB code + 7KB cal + 19KB free) |
| **USB** | CDC ACM — VID `0x1A18`, PID `0x0002`, 921600 baud |
| **BLE** | X2com protocol via iQuad app |
| **Bus** | CAN (ECU ↔ VP44 injection pump) |
| **Sensors** | Boost, EGT, TPS, oil pressure, battery, speed |

---

## About This Project

This is a research and documentation project. The goal is to understand how the Quadzilla Adrenaline works at a fundamental level — the firmware, the protocols, the tuning parameters — and share that knowledge with the diesel performance community.

### Why AI?

This entire project was done by Claude (Anthropic) running as the "Antigravity" agent. The AI:
- Wrote all the Python tools
- Created custom Ghidra scripts (including 6 failed iterations before the nuclear option worked)
- Decompiled and analyzed 119 functions across firmware and BLE library
- Mapped all 117 parameters from 14 vehicle profiles
- Wrote all documentation
- Made mistakes, figured out why, and fixed them

The [main document](docs/QUADZILLA_RE_COMPLETE.md) is written from the AI's first-person perspective because it's more honest and more interesting than pretending a human did the work.

### ⚠️ Safety Warning

Modifying fueling and timing on a diesel engine can cause **catastrophic failure**:
- Excessive fuel without airflow → EGT > 1600°F → melted pistons, cracked heads
- Over-fueling damages the VP44 injection pump ($1500+ replacement)
- Always have EGT monitoring, start conservative, and have K-TAG backups

---

## License

This is research documentation of publicly available consumer hardware and software. All analysis was performed through clean-room decompilation of legally purchased products. No proprietary source code or copyrighted materials are included in this repository.

---

<p align="center">
  <em>Built by an AI. For the diesel community. 🏴‍☠️</em>
</p>
