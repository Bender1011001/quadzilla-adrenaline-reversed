# Technical reference

Facts about the Adrenaline update package, firmware image, USB/X2com protocol and parameter system. Each section
says where the fact comes from. For conclusions see [SECURITY_ASSESSMENT.md](SECURITY_ASSESSMENT.md).

## Hardware

| | |
|---|---|
| Model | Adrenaline `DADR9802`, firmware V2.8.4HF (`FirmwareUpdate.opt`) |
| MCU | ARM7TDMI, SAM7S-class (every peripheral reference in the image maps to the SAM7S address layout, see [FIRMWARE_AUDIT.md](FIRMWARE_AUDIT.md)) |
| Image | 32,000 bytes at `0x4000`-`0xBCFF`, SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780` |
| USB | CDC ACM, VID `0x1A18` PID `0x0002`, 921600 baud 8N1 |
| Phone link | Bluetooth Classic RFCOMM (not BLE), carrying X2com frames |
| Pump output | Static chain reaches AT91 TC0_RC; electrical bus topology is not established by this image alone |

## Update package (`.qz`)

Keyed XOR chain over an Intel HEX file: `E[i] = P[i] ^ K[i % 8] ^ E[i-1]`. The key derives from an 8-byte password via a
256-entry table (AES `Te0`). The plaintext is 2,000 type-`00` records, 0 checksum errors, no EOF record, no signature.
Details and reproduction: [SECURITY_ASSESSMENT.md F1/F2](SECURITY_ASSESSMENT.md), `tools/firmware_crypto.py`.

## Memory map (application image)

```
0x4000-0x401B  seven ARM branch-vector words; 0x401C is MOV R9,R0
0x4044        reset-vector target; ARM startup and Thumb transition nearby
0x4100-0xA91B  application code, literal pools, data and ARM/Thumb interworking
0xA91C-0xAD17  AID pointer table 1
0xAD18-0xB113  AID pointer table 2
0xB114-0xB1B7  executable helpers and literal data
0xB1B8-0xBCFF  erased (0xFF), 2,888 bytes
```

Source: IDA Pro and Ghidra audit of the decrypted image. Earlier notes claimed a 48 KB part with ~19 KB free, build-date and
device-ID strings at `0xFD00`/`0xFE00`, and a second table at `0xAE80`; none of that holds for this image.

Each AID table has 255 slots (0..254). The resolvers also accept AID 255 and
read into the next region. See the [boundary review](AID_TABLE_BOUNDARY_REVIEW.md)
for the complete pointer map and original-helper emulator evidence; this is not
evidence that every in-range slot is supported or that a hardware fault occurred.

## Functions

The baseline inventory is the two-tool audit: 145 confirmed execution entries, 94 with an evidence-backed role. The initial 14 roles are listed below
from `audit/data/semantic_labels.json`. `trace` means a static instruction trace; `chain` means part of the closed static chain below. The labels describe
static roles and do not prove live engine behaviour.

| Entry | Role | Assurance |
|---|---|---|
| `0x4818` | TPS/input gate that reads SRAM byte `0x2005D7` | trace |
| `0x499C` | backdown-percentage threshold walk used to update AID 13 | chain |
| `0x4A94` | applied-stretch percentage arithmetic using the AID 85 working copy | chain |
| `0x4B38` | capture/fuel path that copies `0x2005E8` to telemetry word `0x200604` | trace |
| `0x4D38` | percentage/scalar arithmetic feeding the `0x200604` telemetry path | trace |
| `0x50F0` | main control loop that applies the AID 13 derate and drives the TC0 path | chain |
| `0x59E8` | incoming-capture unpacker and writer for the `0x2005C4` SRAM structure | trace |
| `0x5F34` | writer of SRAM byte `0x200BE7`; live AID meaning remains unproven | trace |
| `0x601C` | AID ingest and validation dispatcher, including the AID 85 clamp/echo | trace |
| `0x6FA0` | AT91 timer-channel write helper used for the TC0_RC output | chain |
| `0x7BF8` | AID payload-width selector using the 75/150/185/220 brackets | trace |
| `0x7C1C` | AID-to-SRAM resolver for pointer table 1 | trace |
| `0x7C68` | AID-to-SRAM resolver for pointer table 2 | trace |
| `0x7D80` | AID data reader that consumes the pointer returned by the table-2 resolver | trace |

Earlier first-pass labels (for example "fueling calculator" for `0x4D38`, "analog sensor processor" for `0x59E8`, "CAN handler" for `0x6C94`) are **not**
carried forward; the audit replaced or did not confirm them.

Seven additional roles (`0x76CC`, `0x7B60`, `0x7CC4`, `0x7E64`, `0x7EB4`,
`0x7EFC`, `0x8038`) and their instruction anchors are documented in the
[offline write-path review](OFFLINE_WRITE_PATH_REVIEW.md). Together these make
the earlier 21-role catalog.

Fifteen USART0, buffer, flag and header/CRC roles are detailed in the
[USART0 review](USART0_BUFFER_REVIEW.md), yielding 36 roles in that baseline.
The separate [entry adjudications](../audit/data/entry_adjudications.json) extend
the known source-entry minimum to 157 after the [software floating point review](SOFT_FLOAT_REVIEW.md); they are not counted twice for RAM aliases.

The [integer execution review](INTEGER_ARITHMETIC_REVIEW.md) adds six baseline
runtime roles and establishes the helpers' R0-remainder/R1-quotient convention.
That pass brought baseline semantic coverage to 42. The
[control helper review](CONTROL_HELPER_REVIEW.md) adds eight entries, bringing
that total to 50. The [software floating point review](SOFT_FLOAT_REVIEW.md)
adds 34 baseline roles, bringing the current total to 84 with 61 pending.
Unreviewed paths and exceptional-value behavior remain under review.
The [configured ratio scorer review](DRIVETRAIN_SCORE_REVIEW.md) adds one
baseline role, bringing the total to 85 with 60 pending. Its upstream input
units and live effect require further review.
The [PIOA and interrupt setup review](PIO_INTERRUPT_REVIEW.md) adds four
baseline roles, bringing the total to 89 with 56 pending. It traces source-2
vector setup, a conditional timer trigger callback, and AIC mask helpers.
The [timer setup review](TIMER_SETUP_REVIEW.md) adds three baseline roles,
bringing the total to 92 with 53 pending. It traces the three-channel setup
and two short callbacks; the third callback remains pending.
The [SPI setup review](SPI_SETUP_REVIEW.md) adds the setup coordinator and
source-5 no-op callback, bringing the total to 94 with 51 pending.

### The static pulse-stretch chain

The tuner acts on the pump through an AT91 timer channel, not by editing ECM tables:

```
AID 85 (requested stretch) -> SRAM 0x200B30 / 0x200590 -> 0x601C clamp -> 0x4A94 -> minus AID 13 (backdown) -> 0x6FA0 -> TC0_RC
```

`0x200604` is a telemetry word (a scaled copy surfaced as AID 149), **not** the timer operand. This is a structural trace of the image; it has not been
measured on a bench or with the engine running. Converting the timer value to microseconds needs a measured clock.

Known SRAM locations: the TPS-gate input byte `0x2005D7`, the capture structure at `0x2005C4`, telemetry `0x200604`, and the boost-curve AIDs 113-136 at
`0x200B3B`-`0x200B69`.

### Disassembly caveat

The firmware mixes ARM startup, Thumb application code, ARM interworking bodies and literal pools. A single ISA split at byte 256 is an approximation, not a complete map. Ghidra's
auto-analysis marked about 96 % of it as data. The working approach: clear all code units, set Thumb mode, then disassemble each
known entry with an address range capped at the next entry to stop cascading (`ghidra/scripts/ghidra_nuclear.py`).
The two-tool audit then replaced hand-seeded entry lists with reconciled ones.

## X2com protocol

Frames on the phone link (and the same framing family over USB): `[type:4 | last_pos:4] + AID list/values + CRC-8`.
Source: decompile of `libx2com-jni.so` (x86_64, 62 functions). CRC-8/SAE-J1850, implemented in `tools/x2com_crc.py`.

| Type | Name | Direction | Meaning |
|---|---|---|---|
| 0 | CWA | app to tuner | write AIDs, wait for ACK |
| 1 | CMD | app to tuner | write AIDs, no ACK |
| 2 | ACK | tuner to app | acknowledgement |
| 3 | NOTIFY | tuner to app | unsolicited data (live gauges) |
| 4 | REQ | app to tuner | read AIDs, triggers RESP |
| 5 | RESP | tuner to app | values |

The MCU walker processes up to **14 payload bytes** per frame. A read list can fit 14 one-byte AIDs; a value-bearing frame fits fewer because each AID also carries value bytes. ACK/RESP state handling is visible statically. See [the write-path review](OFFLINE_WRITE_PATH_REVIEW.md). Value width is fixed by
AID range:

| AID range | Width |
|---|---|
| 0-74 | 1 byte |
| 75-149 | 2 bytes |
| 150-184 | 3 bytes |
| 185-219 | 4 bytes |
| 220+ | variable |

## USB update protocol

Recovered from the updater (`Quadzilla.dll`, `X2Updater.exe`); 11 opcodes. The lab copy of the DLL used for the original
decompile is damaged, so the table was not re-verified in the latest revision.

| Opcode | Name | Data |
|---|---|---|
| `0x00` | LINK_CHECK | reply `0x01` |
| `0x02` | DISCONNECT | |
| `0x03` | BOOTLOAD_MODE | mode |
| `0x04` | MODULE_INFO | reply 25 bytes |
| `0x06` | KEY_TRANSFER | 8-byte key |
| `0x07` | DATA_TRANSFER | length + 61 bytes |
| `0x0B` | XFER_COMPLETE | |
| `0x0D` | SN_PROGRAM | 8-byte serial |
| `0x0E` | FEATURE_CODE | op + 8-byte code |
| `0x10` | ABORT | |
| `0x11` | FEATURE_READ | reply count + data |

Flash sequence: LINK_CHECK, MODULE_INFO, BOOTLOAD_MODE, KEY_TRANSFER, DATA_TRANSFER (repeated), XFER_COMPLETE, DISCONNECT.
`tools/quadzilla_tool.py` implements only LINK_CHECK, MODULE_INFO, FEATURE_READ and DISCONNECT.

## AIDs

117 unique AIDs are declared across the 14 vendor profiles in `vehicles/` (`python tools/diff_profiles.py`). AIDs 145 and 181
(AVG MPG reset / Average MPG) appear only in the vendor's internal "Quadzilla Only" (QZTEST) profile. 110 AID numbers in 0-226
appear in no profile. Catalogue: [AID_REFERENCE.md](AID_REFERENCE.md).
