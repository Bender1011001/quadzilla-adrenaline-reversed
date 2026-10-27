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
| F5 | The device clamps most values, but its limits differ from the app's (AID 85 floor 800 vs 1200 us; timing points 137-138 up to 30 deg vs 20/26) | 602 | Low | **Verified** statically; run-time behaviour untested |
| F6 | AID 255 crosses the staging pointer-table boundary; complete and incomplete values can alter coefficients consumed by the same original control cycle | 125, 787 | Unassigned; live impact unverified | **Reproduced in controlled emulation**, including original CRC/receive and control instructions; physical delivery untested |

Severity is a qualitative judgement of potential impact. Exploitation requirements
depend on the entry path and have not been established for every finding. The
ratings above do not establish physical delivery or engine consequences. F6 has
no live-impact severity pending that evidence.

## Scope, method and limits

**Did:** decrypted and parsed the update container; cross-checked the firmware image in two
disassemblers; inspected the APK's dex, manifest and native library; decompiled and searched
the native X2com library; enumerated the vendor's 14 published vehicle profiles.

**Did not:** connect to a device (none was on the bench in the passes recorded here); capture or
inject Bluetooth traffic; analyse the on-device bootloader (it is not part of the update image);
flash any modified image; test pairing behaviour of the unit. Findings that hinge on those say so.

**Tooling:** Python 3, Ghidra 11.3.2, IDA Pro 9.3 (headless), `ilspycmd`, `zipfile`/dex string
parsing. AI coding assistants were used under the owner's direction for scripting and
note-taking; every number below is backed by a test or a command in this repository.

## Findings

### F6. AID-255 table-boundary alias reaches control consumers (live impact unassigned)

The [AID table boundary review](AID_TABLE_BOUNDARY_REVIEW.md) establishes that
AID 255 indexes beyond both firmware pointer tables. Original helper execution
reproduces a staging write alias and a separate response read from `0x43C02097`.
The [writer and admission review](GENERIC_WRITER_FOOTPRINT_REVIEW.md) extends
the staging finding through three complete original `0x76CC` cycles without
function stubs, starting from a supplied completed receive buffer and controlled
peripheral state. These are computational admission tests, not radio or DMA tests.

With valid CRC, both a complete 13-byte value and a value declaring 14 bytes but
providing 13 write `0x200BBA..0x200BC6`. This fixed interval includes response
coefficients `0x200BC2/BC3`. Original control code consumes the supplied 200/240
before automatic producers replace them with 100/80. The incomplete receive
status does not roll back the stores or prevent that cycle's control call.
A damaged-CRC comparison produces zero alias stores.

Under the documented fixture, telemetry changes from 1041 to 1280 and the
filtered response average from 313 to 387. Those values depend on explicitly
controlled source values and retained filter history; they are not vehicle
measurements. Full response and scalar results agree with the independent
bounded models. Exact inputs, store traces and reproduction commands are linked
in the review and its source-bound artifacts.

**Established:** an out-of-table ID admits a fixed-interval write whose values
reach same-cycle computations, including an incomplete-value path. This is not
an arbitrary-address write. Physical delivery, pairing/authentication, real
source ranges, asynchronous ordering, waveforms and engine consequences remain
unverified. The separate response-read alias has no additional complete-cycle
reachability claim from these three cases.

**Corrective direction:** reject out-of-table IDs before both lookups, restrict
writable parameters, check complete width and destination capacity before
storing, and isolate or roll back incomplete staging. CRC checking alone does
not enforce those conditions. No firmware patch has been deployed.

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

F1 permits construction of altered packages with valid line checksums. Updater and bootloader acceptance of an altered package has not been tested.
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
  directly, so the frame format itself supplies no replay defense (CWE-294); device replay acceptance remains untested.
- A keyword search of the full decompile (`decompiled_x2com.c`) finds no occurrence of
  `auth`, `hmac`, `nonce`, `encrypt`, `decrypt`, `aes`, `cipher`, `challenge`, `secret`, `password` or `signature`.
- On the device, the audited AID ingest dispatcher (`0x601C`) validates incoming values (it includes an AID 85 clamp) and
  the audited resolver `0x7C1C` maps an AID to its SRAM location. The reviewed entries do not establish an authentication,
  session or key check. Fresh IDA and Binary Ninja traces of the multi-AID write routine (`0x7CC4`) show it copying received
  value bytes to the address `0x7C1C` returns; it also checks message type and byte-parser state, and caps the processed payload count at 14.
  The [write-path review](OFFLINE_WRITE_PATH_REVIEW.md) subsequently traces the receive dispatcher and ordinary validation caller.
  Physical transport checks, interrupts and every indirect handler remain outside that bounded review; this is not proof of universal absence.

Per the vendor profiles, the writable AIDs include a 24-point fueling-versus-boost curve (AIDs 113-136,
50-150 %) and RPM timing limits (AIDs 137-143). Reproduce with `python tools/diff_profiles.py`.

**Impact:** any peer that can complete the Bluetooth link can rewrite those parameters. That includes a
nearby attacker if F3's pairing is weak, and a modified or malicious phone app. The consequence is over-fueling
and engine damage, not data loss.
**Fix:** require authenticated, encrypted pairing; add an application-level challenge-response with a MAC;
enforce limits on the device (F5); rate-limit and log writes.

### F5. Selected device-side limits differ from the app's (Low, static and bounded execution evidence)

The app's limits are fields of the vendor's JSON profiles (`QuadAttribute`: `minValue`, `maxValue`, `multiplyFactor`). The firmware does
not rely only on them: the ingest dispatcher (`0x601C`) selects 57 non-default handlers, including copies, masks, range checks and shared continuations.
The [local handler accounts](REMAINING_AID_UPDATE_REVIEW.md), [selector/count review](AID_DISPATCH_SELECTOR_UPDATES.md)
and [compound review](COMPOUND_AID_UPDATE_REVIEW.md) now trace all those local paths with bounded original-byte execution.
`python tools/aid_clamps.py` remains a lexical clamp-literal listing, not a control-flow or transport-width evaluator.

| AIDs | App limit | Device clamp (raw) | Relation |
|---|---|---|---|
| 113-136 (curve, low staged byte) | 50-150 % | 50-150 on the low byte; upper staged byte ignored by these handlers | low-byte range agrees; transport width is separately documented |
| 139-141 (timing, 2500 RPM and up) | 0-30 deg | 0-300 at x0.1 = 30.0 deg | equal |
| 17, 59, 61, 62, 110, 112 | per profile | source-bound local limits documented in the handler account | raw extents agree with the earlier profile comparison; widths remain distinct |
| 22 | per profile | conditional rule using working AID 112 value; not a universal 20-40 clamp | coupled behavior established; intended relationship unverified |
| **85** (max fuel stretch) | **1200-2200 us** | **800-2200** (upper bound operand 2201 read from the image at `0x67C0`) | **device allows 400 us lower** |
| **137, 138** (timing at 1500 and 2000 RPM) | **0-20 and 0-26 deg** | 0-30.0 deg | **device allows more advance** |
| 15 | 6-15 | 5-14, then quotient/remainder mapping derivation | different raw range; app count encoding needs review before calling it an off-by-one defect |
| 104 (RPM limit) | 3200-3700 | 3200-3700 (literal 3701 at `0x67D8`, upper branch subtracts one) | equal statically |
| 146, 150-154 | per profile | local copies/masks; AID 154 narrows a 16-bit comparison/store and continues into AID 146 | local contracts established; intended ranges and downstream impact remain unresolved |
| 226 | compound profile value | independent selector bounds and positive floating-coefficient guard | local guards established; variable-width transport remains separate |

These local bounds constrain selected successful ingest paths, but do not prove every raw-staging consumer enforces them.
The AID 85 handler accepts raw values 800-1199, and the two lower timing-point handlers accept raw 300, outside the corresponding profile limits.
The scaling (raw = display / `multiplyFactor`) is inferred; five AIDs (17, 59, 139-141) corroborate that interpretation through their declared scales and limits.
This is firmware-path evidence, not measured acceptance by a physical device. The [compound review](COMPOUND_AID_UPDATE_REVIEW.md)
also reproduces partial staging later applied through a different AID under an explicit receive-result contract.
Complete framing/transport reachability, app encoding and live effects remain unverified. Passing the local bounds does not establish safe operation.

```bash
python tools/aid_clamps.py
python -c "import struct;print(struct.unpack_from('<I', open('fw.bin','rb').read(), 0x67c0-0x4000)[0])"   # 2201
```

## Unrated local memory-safety observation

The [frame reader review](FRAME_READER_REVIEW.md) found that `0x7D80` appends
rejected response AIDs into a 16-byte stack list without checking the list
count. A direct original-byte call with 17 null AIDs writes into saved
register storage; 22 cause an unmapped write in the emulator after the
saved destination pointer changes. The examined queue copier at `0x7FD8`
caps its output to 14 bytes, and the complete state-count provenance into
`0x7D80` has not yet been established. This is a conditional local finding,
with no assigned remote exploitability or device severity. The fault is
an offline emulator observation; hardware effects were not measured.

The neighboring [outgoing queue filter](OUTGOING_QUEUE_FILTER_REVIEW.md)
also uses a 16-byte stack scratch list without bounding its initial
current-list count. A direct call with 17 unmatched AIDs reaches saved
register storage. Its four direct call sites, zero-initialized queue
fields and the inspected 14-byte copy caps narrow the normal-path risk;
the complete writer provenance for those fields is still under review.
The [outgoing state review](OUTGOING_STATE_REVIEW.md) confirms the local
14-byte working-queue copies and shows that the response reader rewrites
the distinct source counts after each frame. It does not establish every
source-count producer or physical reachability of either stack boundary.
The [queue state owner review](QUEUE_STATE_OWNER_REVIEW.md) also checks the
guarded third-queue setup, flag reset and all aligned image literals into
the shared state block. Neither reviewed helper fills the two outgoing AID
source counts; indirect or computed-pointer writers remain to be excluded.

The [cycle queue selector](CYCLE_QUEUE_SELECTION_REVIEW.md) has a separate
conditional source-boundary issue. Its five initialized telemetry lists
occupy eight bytes each and start with counts 5–7. A controlled count of
nine makes the otherwise 14-capped queue copier read the first byte of
the following list. The source-count writers have not yet been fully
traced, so this is a demonstrated local condition, not an established
ordinary operating state or hardware effect.

## Also checked, no issue found

- Secure RFCOMM variant used; no insecure-socket call.
- No cleartext-traffic flag; vendor profile JSON is fetched over HTTPS.
- The free flash in the image is only 2,888 bytes (`0xB1B8-0xBCFF`), which bounds what could be added.
- This repository's own tooling: the USB tool's CLI sends only `LINK_CHECK`, `MODULE_INFO`, `FEATURE_READ` and `DISCONNECT`;
  flashing, serial-number and feature-code opcodes are constants only.

## Not tested

Modified-firmware acceptance by the bootloader; Bluetooth pairing mode and PIN; on-air traffic capture and replay;
run-time behaviour of the device-side range checks (F5 is from static analysis); behaviour of the updater when the `.qz` is tampered with.

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
| `0x4D38` "fueling calculator", `0x59E8` "analog sensor processor" (first pass and the June audit) | Audited roles: scalar arithmetic feeding the `0x200604` telemetry word; incoming-capture unpacker. `0x200604` is telemetry, not the pump output | two-tool audit + static chain trace |
| AID pointer table 2 at `0xAE80` | `0xAD18`-`0xB113` | audit (`0xAE82` lies inside it) |
| "`FirmwareUpdate.pwk` is 4 bytes, not the full key" (a lab note) | The 4-byte file was a truncated extraction. The full key is 8 bytes, derived from the 8-byte `.pwd`, and decrypts the `.qz` to the audited image | end-to-end run, SHA-256 match |

## Suggested disclosure

The [offline software floating point review](SOFT_FLOAT_REVIEW.md) identifies
reproducible exceptional-input numeric differences and a binary64 add path
dependent on the caller's R4 value. No connected-controller effect or security
severity is established by these offline calls.
The [configured ratio scorer review](DRIVETRAIN_SCORE_REVIEW.md) also records
an original-byte case where integer score 512 narrows to byte zero and wins
the candidate comparison. Its upstream input units and any live consequence
remain unresolved; this is not assigned a security severity.

The product is an old aftermarket part, but the pattern (static obfuscation key, unsigned updates, unauthenticated control
channel) is common. If this is reported, send the vendor F2 and F4 first, with the recommendations above.
