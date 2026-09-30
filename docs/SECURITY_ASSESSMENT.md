# Security assessment: Quadzilla Adrenaline (DADR9802)

| | |
|---|---|
| **Target** | Quadzilla Adrenaline inline diesel tuner, firmware V2.8.4HF, iQuad Android app (`com.quadzillapower.iquad`), X2Updater installer `ADR9802v2.8.4` |
| **Fitment** | 1998.5-2002 Dodge Ram 5.9 Cummins (VP44 pump); the unit sits between the ECM and the injection pump |
| **Type** | Static analysis of the update package, the Android app and the firmware image. No radio testing, no bench flashing. |
| **Status** | Independent research on hardware and software the author owns. No vendor contact is recorded in this repository. |

## Summary

The tuner changes fuel quantity and timing in real time, so a bad write can damage an
engine. This assessment asks who can change what, and what stops them.

| # | Finding | CWE | Severity | Evidence |
|---|---|---|---|---|
| F1 | Firmware "encryption" is a keyed XOR chain; password, key and algorithm ship in the same installer | 321, 327 | Low | **Verified** (reproduced on the real `.qz`) |
| F2 | Update package carries only Intel HEX line checksums: no signature, MAC or hash | 345, 494 | Medium (potential) | **Verified** for the package; device-side check **untested** |
| F3 | Phone link is Bluetooth Classic RFCOMM with no app-level pairing or crypto | 287 | Info | **Verified** in the APK; pairing strength **untested** |
| F4 | X2com protocol has no authentication, nonce or encryption; a CRC-8 is the only check | 306, 294 | Medium | **Verified** (static); on-air behaviour **untested** |
| F5 | Parameter limits (e.g. fueling 50-150 %) are defined in app-side JSON; device-side clamping not located | 602 | Low | **Inferred** |

Severity is a qualitative judgement of realistic impact. Every attack needs proximity or
physical access to a 20-year-old aftermarket part, and the asset is engine health, not
personal data. "Medium" reflects that the consequence of an unauthorised write is physical.

## Scope, method and limits

**Did:** decrypted and parsed the update container; cross-checked the firmware image in two
disassemblers; inspected the APK's dex, manifest and native library; decompiled and searched
the native X2com library; enumerated the vendor's 14 published vehicle profiles.

**Did not:** capture or inject Bluetooth traffic; analyse the on-device bootloader (it is not
part of the update image); flash any modified image; test pairing behaviour of the unit.
Findings that hinge on those say so.

**Tooling:** Python 3, Ghidra 11.3.2, IDA Pro 9.3 (headless), `ilspycmd`, `zipfile`/dex string
parsing. AI coding assistants were used under the owner's direction for scripting and
note-taking; every number below is backed by a test or a command in this repository.

## Findings

### F1. Firmware container is obfuscated, not encrypted (Low, verified)

The `.qz` update file is an Intel HEX file passed through a ciphertext-feedback XOR chain:

```
E[i] = P[i] ^ K[i % 8] ^ E[i-1]        (E[-1] = 0)
```

The 8-byte key `K` (`.pwk`) is derived from an 8-byte password (`.pwd`) by `X2Crypt.GeneratePasswordKey`,
which indexes a 256-entry table. **That table is the standard AES `Te0` table** (256/256 entries
identical to `Te0` computed from the Rijndael S-box; `tests/test_firmware_crypto.py`). No AES rounds
are used for the data.

Why it fails:

1. Password, derived key and algorithm are all inside the installer, next to the ciphertext.
2. The key is recoverable from the ciphertext alone. Intel HEX records start with `:`, and this image
   loads at `0x4000` in 16-byte records, so the first eight plaintext bytes are `:1040000`. Since
   `K[i] = P[i] ^ E[i] ^ E[i-1]`, eight known bytes yield the whole key.

```bash
python tools/firmware_crypto.py recover-key FirmwareUpdate.qz
# key (from known plaintext): 111d6f202ee5a103
# validation: 2000 Intel HEX records, 0 checksum errors
python tools/firmware_crypto.py decrypt FirmwareUpdate.qz fw.hex --pwd-file FirmwareUpdate.pwd --bin fw.bin
# sha256(fw.bin) = 1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780
```

**Impact:** anyone can read or rewrite the firmware offline. The firmware holds no user data, so
confidentiality impact is limited to vendor IP and making F2 practical.
**Fix:** treat it as integrity, not secrecy. Use signatures (F2). Do not rely on the obfuscation.

### F2. No signature or authenticity check in the update package (Medium, potential)

The decrypted package is exactly 2,000 type-`00` data records covering `0x4000-0xBCFF`
(32,000 bytes). There is no signature, MAC, hash, version binding or end-of-file record. The only
integrity mechanism is the per-record Intel HEX checksum, which detects accidents, not tampering, and
which anyone can recompute. The cipher is also malleable: flipping one ciphertext bit changes exactly two
plaintext bytes (`test_chain_propagates_errors`).

Anyone who can build a valid `.qz` (F1 makes that easy) produces a package the updater treats as genuine.
The recovered opcode table also shows the updater sending the key to the device (`KEY_TRANSFER`, `0x06`),
so the device decrypts with a value the public already has.

**Not tested:** whether the on-device bootloader rejects an altered image. The bootloader lies outside the
`0x4000+` application image and was not analysed. "Flashes without complaint" is therefore *not*
claimed; only "nothing in the package would let the device tell the difference" is.
**Fix:** verify an asymmetric signature (for example Ed25519 or ECDSA) in the bootloader, with the public key in ROM.

### F3. Phone link is Bluetooth Classic (RFCOMM), not BLE (Info, verified)

Earlier revisions of this repository called the link "BLE". That was wrong. In the app's dex:

| API string | Count |
|---|---|
| `createRfcommSocketToServiceRecord` (secure RFCOMM) | 1 |
| `createInsecureRfcommSocketToServiceRecord` | 0 |
| `BluetoothGatt`, `connectGatt`, `BluetoothLeScanner` | 0 |
| `createBond`, `setPin`, `ACTION_PAIRING_REQUEST` | 0 |

The app uses the secure RFCOMM variant (good) and never pairs on its own, so link security is whatever
the Bluetooth module and the phone OS negotiate. Whether the module accepts Just Works, a fixed legacy PIN or
Secure Simple Pairing with MITM protection is **untested** and decides how serious F4 is.
Also present: a leftover `listenUsingRfcommWithServiceRecord` server path and the `BluetoothChatService` name,
both from Google's sample code. Web traffic uses HTTPS (no cleartext flag in the manifest).

### F4. The application protocol has no authentication (Medium, verified statically)

X2com frames are `[type:4 | last_pos:4] + AID list/values + CRC-8`. The CRC is **CRC-8/SAE-J1850**
(init `0xFF`, poly `0x1D`, final XOR `0xFF`; check value `0x4B` for `"123456789"`, valid-frame residue `0x3B`),
implemented and tested in `tools/x2com_crc.py`.

- A CRC detects noise. It is not a MAC: anyone can compute it.
- There is no nonce, counter, session or encryption field. Commands (`CMD`, `CWA`) write values
  directly, so a captured frame replays (CWE-294).
- A keyword search of the full decompile (`decompiled_x2com.c`) finds no occurrence of
  `auth`, `hmac`, `nonce`, `encrypt`, `decrypt`, `aes`, `cipher`, `challenge`, `secret`, `password` or `signature`.
- On the device, the multi-AID write routine (`0x7CC4`) copies received value bytes to the RAM address returned by the
  AID lookup (`0x7C1C`). Inside that function the only conditions are "the AID exists" and "at most 14 AIDs per
  frame". Callers were not audited.

Per the vendor profiles, the writable AIDs include a 24-point fueling-versus-boost curve (AIDs 113-136,
50-150 %) and RPM timing limits (AIDs 137-143). Reproduce with `python tools/diff_profiles.py`.

**Impact:** any peer that can complete the Bluetooth link can rewrite those parameters. That includes a
nearby attacker if F3's pairing is weak, and a modified or malicious phone app. The consequence is over-fueling
and engine damage, not data loss.
**Fix:** require authenticated, encrypted pairing; add an application-level challenge-response with a MAC;
enforce limits on the device (F5); rate-limit and log writes.

### F5. Limits are client-side (Low, inferred)

Minimum and maximum values (for example 50-150 % on AIDs 113-136) are fields of the vendor's JSON profiles
(`QuadAttribute`: `minValue`, `maxValue`, `multiplyFactor`, `offset`), enforced by the app's UI. A peer that speaks
X2com directly is not subject to them unless the firmware clamps independently. No clamp was found in the write
routine; consumers of the stored values were not audited. **Needs a device test.**

## Also checked, no issue found

- Secure RFCOMM variant used; no insecure-socket call.
- No cleartext-traffic flag; vendor profile JSON is fetched over HTTPS.
- The free flash in the image is only 2,888 bytes (`0xB1B8-0xBCFF`), which bounds what could be added.
- This repository's own tooling: the USB tool's CLI sends only `LINK_CHECK`, `MODULE_INFO`, `FEATURE_READ` and `DISCONNECT`;
  flashing, serial-number and feature-code opcodes are constants only.

## Not tested

Modified-firmware acceptance by the bootloader; Bluetooth pairing mode and PIN; on-air traffic capture and replay;
device-side range checks; behaviour of the updater when the `.qz` is tampered with.

## Errata: corrections made to earlier claims in this repository

Finding your own mistakes before a reader does is part of the method. These were all wrong or unsupported:

| Earlier claim | Correction | How it was caught |
|---|---|---|
| "X2com BLE" | Bluetooth Classic RFCOMM | dex API search (F3) |
| APK analysed with apktool, 30,609 files; `apk_strings.txt` | That file was the **Aptoide store client**, not iQuad (8,419 Aptoide vs 0 x2com mentions in dex). The real APK has 689 files. String dump removed. | dex comparison of both APKs |
| 19 KB free flash | 2,888 bytes | IDA audit, June 2026 |
| Build-date and device-ID strings at `0xFD00`/`0xFE00` | Not present in the image | IDA audit |
| 57 of 60 functions | First pass only. IDA and Ghidra independently reconcile to 145 execution entries ([FIRMWARE_AUDIT.md](FIRMWARE_AUDIT.md)) | two-tool cross-check |
| "Firmware modifications flash without complaint" | Never tested on a device | review of project notes |
| "15 USB opcodes" | 11 recovered | opcode table |
| "Key extracted from the .NET DLL" | Key derives from `.pwd`; both files ship beside the DLL | `decrypt_firmware.py` reproduction |
| `firmware_crypto.py` derived the key from a CRC32 table and zero-padded short keys | Real derivation implemented; wrong-length keys rejected | end-to-end run on the real `.qz` |
| `quadzilla_tool.py scan` | Was a stub that printed "0 responding AIDs"; now says it is not implemented | code review |

## Suggested disclosure

The product is an old aftermarket part, but the pattern (static obfuscation key, unsigned updates, unauthenticated control
channel) is common. If this is reported, send the vendor F2 and F4 first, with the recommendations above.
