# Quadzilla Adrenaline: firmware and protocol security analysis

[![tests](https://github.com/Bender1011001/quadzilla-adrenaline-reversed/actions/workflows/ci.yml/badge.svg)](https://github.com/Bender1011001/quadzilla-adrenaline-reversed/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Static security analysis of the **Quadzilla Adrenaline** (DADR9802), an aftermarket inline tuner for 1998.5-2002 Dodge Ram 5.9 Cummins trucks. It sits between the
ECM and the VP44 injection pump and changes fuel quantity and timing in real time, so an unauthorised write to it can damage an engine.

The work covers the firmware update package, the ARM7 firmware image, the iQuad Android app and its native protocol library, and the vendor's parameter profiles.
Everything is reproducible from scripts and tests in this repository. Claims that could not be verified are labelled, and corrections to earlier versions of this
repository are listed in the [errata](docs/SECURITY_ASSESSMENT.md#errata-corrections-made-to-earlier-claims-in-this-repository).

## Results

| # | Finding | Severity | Evidence |
|---|---|---|---|
| F1 | "Encrypted" firmware is a keyed XOR chain; password, key and algorithm ship in the installer; key recoverable from 8 bytes of known plaintext | Low | verified |
| F2 | Update package has no signature, MAC or hash, only Intel HEX line checksums | Medium (potential) | verified for package; device check untested |
| F3 | Phone link is Bluetooth **Classic** RFCOMM with no app-level pairing or crypto | Info | verified; pairing strength untested |
| F4 | X2com control protocol has no authentication, nonce or encryption; CRC-8/SAE-J1850 only | Medium | verified statically |
| F5 | The device clamps most values, but its limits differ from the app's (AID 85 floor 800 vs 1200 us; timing 137-138 up to 30 deg vs 20/26) | Low | verified statically |

Full write-up with CWE mappings, reproduction commands, recommendations and what was *not* tested: **[docs/SECURITY_ASSESSMENT.md](docs/SECURITY_ASSESSMENT.md)**.

Supporting analysis:

- **Two-tool firmware audit:** IDA Pro 9.3 and Ghidra 11.3.2 independently reconciled to 145 execution entries in a 32,000-byte image, asserted by tests
  ([docs/FIRMWARE_AUDIT.md](docs/FIRMWARE_AUDIT.md)).
- **Reverse engineering report:** method, dead ends and open questions ([docs/REVERSE_ENGINEERING_REPORT.md](docs/REVERSE_ENGINEERING_REPORT.md)).
- **Technical reference:** memory map, X2com frames, USB opcodes, AIDs ([docs/TECHNICAL_REFERENCE.md](docs/TECHNICAL_REFERENCE.md)).

## Try it

Python 3.10+, standard library only (`pyserial` for the USB tool).

```bash
python -m unittest discover -s tests -t . -v     # 30 tests, no vendor files needed
python tools/diff_profiles.py                     # 14 vendor profiles, 117 unique AIDs, QZTEST-only {145, 181}
python tools/x2com_crc.py                         # CRC-8/SAE-J1850 check value: 0x4B
python tools/aid_clamps.py                        # device-side value clamps for 57 AIDs vs the app's limits
```

With your own copy of the vendor update package (not included):

```bash
python tools/firmware_crypto.py recover-key FirmwareUpdate.qz          # key from ciphertext alone
python tools/firmware_crypto.py decrypt FirmwareUpdate.qz fw.hex --pwd-file FirmwareUpdate.pwd --bin fw.bin
# expected image SHA-256: 1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780
python -m unittest tests.test_firmware_audit -v                        # audit numbers vs the committed data
```

## Layout

```
docs/    SECURITY_ASSESSMENT.md  findings, errata        FIRMWARE_AUDIT.md   two-tool cross-check
         REVERSE_ENGINEERING_REPORT.md                   TECHNICAL_REFERENCE.md   AID_REFERENCE.md
         RE_VERIFICATION_2026-05-02.md  earlier audit    archive/   superseded notes, kept as a record
tools/   firmware_crypto.py  x2com_crc.py  diff_profiles.py  quadzilla_tool.py (read-only USB subset)  analyze_*.py
audit/   data/ (IDA + Ghidra exports, reconciliation)   tools/ (export and reconcile scripts)
ghidra/  scripts used for the first-pass decompile
tests/   unit tests (crypto, CRC, profiles, audit numbers)
vehicles/  14 vendor profile JSONs     decompiled_*.c  decompiler output (see NOTICE.md)     analysis/  working notes and scratch scripts
```

## Methodology and AI assistance

The analysis was done with AI coding assistants (Claude) working under the repository owner's direction on hardware and files the owner supplied.
Nothing is accepted on an assistant's say-so: a result stays only if a script, a test, or a second independent tool reproduces it, and several earlier
claims did not survive that check (see the errata). The two-disassembler audit and the test suite exist for that reason.

## Scope and responsible use

Independent research on a product the author owns. No vendor binaries, installers, firmware images or APKs are included (`.gitignore` blocks them); see
[NOTICE.md](NOTICE.md) for what is and is not in the tree. No modified firmware has been flashed and no radio traffic was captured. No vendor contact is
recorded here. Changing fuel or timing on a diesel can destroy an engine and may be illegal for road use; nothing here is a tuning guide.

## License

MIT for original work ([LICENSE](LICENSE)). Decompiler output, vendor profile JSON and derived analysis artifacts remain the property of their owners and are
included for analysis and interoperability documentation only.
