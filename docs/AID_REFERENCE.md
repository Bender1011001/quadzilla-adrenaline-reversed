# Quadzilla Adrenaline — Complete AID Reference

*All 117 known AIDs mapped from 14 vehicle profiles + firmware analysis.*
*110 undocumented AIDs in range 0-226 need probing on live device.*

---

## AID Data Size Rules (from firmware + libx2com-jni.so)

| AID Range | Byte Width | Firmware Segment | X2com Buffer |
|-----------|-----------|-----------------|--------------|
| 0 – 74 | 1 byte | Segment 1 | one_byte_rx/tx |
| 75 – 149 | 2 bytes | Segment 2 | two_byte_rx/tx |
| 150 – 184 | 3 bytes | Segment 3 | three_byte_rx/tx |
| 185 – 219 | 4 bytes | Segment 4 | four_byte_rx/tx |
| 220+ | variable | — | var_byte_rx/tx |

---

## Segment 1 — Sensors & Status (1-byte, AIDs 0-74)

### Live Sensors
| AID | Name | Unit | Min | Max | Scale | Vehicles |
|-----|------|------|-----|-----|-------|----------|
| 0 | Fuel Pressure | PSI | 0 | 100 | — | Dodge 98-02 |
| 1 | Boost Pressure | PSI | 0 | 57 | — | ALL |
| 3 | Fuel Temp | °F | -40 | 215 | — | Dodge 98-02 |
| 4 | Intake Air Temperature | °F | 0 | 215 | — | ALL |
| 5 | Throttle Position | % | 0 | 100 | — | ALL |
| 6 | Oil Pressure | PSI | 0 | 158 | — | Dodge 98-04 |
| 7 | Engine Load | % | 0 | 100 | — | ALL |
| 8 | Vehicle Speed | MPH | 0 | 130 | — | ALL |
| 12 | ECM Voltage | V | 0 | 18 | — | Dodge/Ford |
| 13 | Backdown Percentage | % | 0 | 100 | — | ALL |
| 29 | Barometer | PSI | 10 | 16.9 | — | Chevy/Dodge 06+/Ford |
| 30 | Commanded EGR | % | 0 | 100 | — | Dodge 07-09/Ford |
| 31 | EGR Error | % | -100 | 100 | — | Dodge 07-09/Ford |
| 33 | Ambient Air Temperature | °F | 0 | 150 | — | Dodge 06-09 |
| 34 | Fuel Level | % | 0 | 100 | — | Dodge 06+/Ford 05+ |
| 38 | Warmups Since DTC Cleared | count | 0 | 255 | — | Dodge 06+/Ford 05+ |
| 40 | Transmission Slip | % | 0 | 100 | — | ALL |
| 41 | Driver Demand Torque | % | 0 | 100 | — | Chevy only |
| 42 | Nominal Friction Torque | % | 0 | 100 | — | Chevy only |

### Status Indicators
| AID | Name | Format | Vehicles |
|-----|------|--------|----------|
| 9 | Power Level | Level# | ALL |
| 32 | Current Gear | Gear# | ALL |
| 39 | Torque Converter Lock | Boolean | ALL |
| 53 | Soot Regeneration | Boolean | Chevy/Dodge 07+ |
| 54 | SOX Regeneration | Boolean | Chevy/Dodge 07+ |

### Tuning Parameters (1-byte)
| AID | Name | Unit | Min | Max | Section | Vehicles |
|-----|------|------|-----|-----|---------|----------|
| 15 | Number of Power Levels | — | 6 | 15 | Tune Parameters | ALL |
| 16 | Timing Limit | DEG | 0 | 15 | Tune Parameters | Dodge 98-02/Ford |
| 17 | Max Load Timing Offset | DEG | 0 | 3 | Timing Parameters | Dodge 98-02/Ford |
| 18 | TPS Pump Maximum | % | 0 | 100 | Pump Tap Parameters | Dodge 98-02 |
| 19 | TPS Pump Minimum | % | 0 | 100 | Pump Tap Parameters | Dodge 98-02 |
| 20 | TPS CAN Maximum | % | 0 | 100 | Tune Parameters | Dodge 98-02 |
| 21 | TPS CAN Minimum | % | 0 | 100 | Tune Parameters | Dodge 98-02 |
| 22 | Boost Scaling | PSI | 20 | 40 | Pump Tap Parameters | ALL |
| 24 | Reset Factory Defaults | — | — | — | Tune Parameters | Dodge 07+/Ford 05+ |
| 47 | Rail Pressure Scaling | % | 0 | 100 | Tuning Parameters | Chevy/Dodge 03+/Ford |
| 48 | TPS Rail Pressure Max | % | 0 | 100 | Tuning Parameters | Chevy/Dodge 03+/Ford |
| 49 | TPS Rail Pressure Min | % | 0 | 100 | Tuning Parameters | Chevy/Dodge 03+/Ford |
| 50 | TPS Fuel Stretch Max | % | 0 | 100 | Tuning Parameters | Chevy/Ford |
| 51 | TPS Fuel Stretch Min | % | 0 | 100 | Tuning Parameters | Chevy/Ford |
| 52 | % of Max Injector Stretch | % | 0 | 100 | Tuning Parameters | Chevy/Dodge 03+/Ford |
| 59 | Low PSI Timing Reduction | DEG | 0 | 5 | Timing Parameters | V2 Dodge |
| 60 | Timing Reduction Scaling | % | 0 | 100 | Timing Parameters | V2 Dodge |
| 61 | Light Throttle Timing Adv | DEG | 0 | 8 | Timing Parameters | V2 Dodge |
| 62 | Light Throttle Load Limit | % | 0 | 40 | Timing Parameters | V2 Dodge |

---

## Segment 2 — Gauges & Tuning Curves (2-byte, AIDs 75-149)

### Live Gauges
| AID | Name | Unit | Min | Max | Vehicles |
|-----|------|------|-----|-----|----------|
| 75 | EGT | °F | 0 | 1800 | ALL |
| 76 | Transmission Temperature | °F | 0 | 280 | ALL |
| 77 | ECM Voltage | V | 0 | 18 | Dodge 06-09 |
| 78 | RPM | RPM | 0 | 4500 | ALL |
| 83 | Rail Pressure | PSI | 0 | 29300 | Chevy/Dodge 03+/Ford |
| 84 | Coolant | °F | 0 | 280 | ALL |
| 86 | MAF | g/s | 0 | 655.35 | Dodge 07+/Ford |
| 87 | Runtime Since Start | SEC | 0 | 65535 | Dodge 06+/Ford 05+ |
| 88 | Distance With MIL On | MI | 0 | 40704 | Dodge 07-09 |
| 89 | Distance Since DTC Cleared | MI | 0 | 40704 | Dodge 06+/Ford 05+ |
| 90 | Output Shaft Speed | RPM | 0 | 8191 | Chevy/Dodge 06+ |
| 93 | Distance With MIL On | MI | 0 | 40704 | Dodge 06+/Ford 05+ |
| 94 | Time Since DTC Cleared | SEC | 0 | 65535 | Dodge 06-09 |
| 96 | Regeneration Filter Load | % | 0 | 45.5 | Dodge 07-09 |
| 97 | Total Regens Complete | count | 0 | 65535 | Dodge 07-09 |
| 98 | Total Regens Desired | count | 0 | 65535 | Dodge 07-09 |
| 100 | O2 Sensor 1 | — | 0 | 2 | Dodge 07-09 |
| 101 | O2 Sensor 2 | — | 0 | 2 | Dodge 07-09 |
| 102 | Cat Temp Bank 1 Sensor 1 | °F | 0 | 1800 | Dodge 07-09 |
| 103 | Cat Temp Bank 1 Sensor 2 | °F | 0 | 1800 | Dodge 07-09 |
| 105 | Gallon Trip | — | 0 | 1000 | V2 Dodge |
| 147 | ECO | — | 0 | 1000 | V2 Dodge |
| 148 | CanBus Fuel | — | 0 | 5000 | V2 Dodge |
| 149 | Timing | DEG | 0 | 30.0 | V2 Dodge |

### Settings (2-byte)
| AID | Name | Unit | Min | Max | Vehicles |
|-----|------|------|-----|-----|----------|
| 81 | Boost Defuel Setting | PSI | 23 | 57 | ALL |
| 85 | Maximum Fuel Stretch | μsec | 1200 | 2200 | Dodge 98-02/Chevy |
| 91 | Gear Change Defuel | % | 0 | 100 | Chevy/Dodge 07+/Ford |
| 92 | Trans Slip Defuel | % | 0 | 20 | Chevy |
| 104 | RPM Limit | RPM | 3200 | 3700 | V2 Dodge/4K |
| 110 | Min Pump Tap Fueling % | % | 0 | 50 | V2 Dodge |
| 111 | Max Valet Mode Power | % | 0 | 100 | V2 Dodge |
| 112 | Pump Low Boost Scale PSI | PSI | 0 | 25 | V2 Dodge |
| 145 | AVG MPG Reset | — | 0 | 1 | **HIDDEN** (QZTEST only) |
| 146 | MPG Offset | % | 90 | 254 | V2 Dodge |

### Boost Level Fueling Curve (24-point, AIDs 113-136)
This is the money — a user-adjustable fueling curve indexed by boost pressure:

| AID | Boost Point | Unit | Min | Max | Default |
|-----|------------|------|-----|-----|---------|
| 113 | 0 PSI | % | 50 | 150 | 100 |
| 114 | 1 PSI | % | 50 | 150 | 100 |
| 115 | 2 PSI | % | 50 | 150 | 100 |
| 116 | 3 PSI | % | 50 | 150 | 100 |
| 117 | 4 PSI | % | 50 | 150 | 100 |
| 118 | 5 PSI | % | 50 | 150 | 100 |
| 119 | 6 PSI | % | 50 | 150 | 100 |
| 120 | 7 PSI | % | 50 | 150 | 100 |
| 121 | 8 PSI | % | 50 | 150 | 100 |
| 122 | 9 PSI | % | 50 | 150 | 100 |
| 123 | 10 PSI | % | 50 | 150 | 100 |
| 124 | 11 PSI | % | 50 | 150 | 100 |
| 125 | 12 PSI | % | 50 | 150 | 100 |
| 126 | 13 PSI | % | 50 | 150 | 100 |
| 127 | 14 PSI | % | 50 | 150 | 100 |
| 128 | 15 PSI | % | 50 | 150 | 100 |
| 129 | 16 PSI | % | 50 | 150 | 100 |
| 130 | 18 PSI | % | 50 | 150 | 100 |
| 131 | 20 PSI | % | 50 | 150 | 100 |
| 132 | 22 PSI | % | 50 | 150 | 100 |
| 133 | 24 PSI | % | 50 | 150 | 100 |
| 134 | 26 PSI | % | 50 | 150 | 100 |
| 135 | 28 PSI | % | 50 | 150 | 100 |
| 136 | 30+ PSI | % | 50 | 150 | 100 |

*Note: 1 PSI resolution from 0-16 PSI, then 2 PSI steps from 16-30+ PSI.*

### RPM Timing Max Table (AIDs 137-143)
| AID | RPM Point | Unit | Min | Max | Vehicles |
|-----|----------|------|-----|-----|----------|
| 137 | 1500 RPM | DEG | 0 | 20 | V2 Dodge |
| 138 | 2000 RPM | DEG | 0 | 26 | V2 Dodge |
| 139 | 2500 RPM | DEG | 0 | 30 | V2 Dodge |
| 140 | 3000 RPM | DEG | 0 | 30 | V2 Dodge |
| 141 | Max RPM | DEG | 0 | 30 | V2 Dodge |
| 142 | 3500 RPM | DEG | 0 | 32 | 4K only |
| 143 | 4000 RPM | DEG | 0 | 32 | 4K only |

---

## Segment 3 — Settings & Thresholds (3-byte, AIDs 150-184)

| AID | Name | Unit | Min | Max | Vehicles |
|-----|------|------|-----|-----|----------|
| 150 | EGT Defuel Setting | °F | 1200 | 1800 | ALL |
| 152 | Turbo Timer Setting | °F | 100 | 500 | ALL |
| 153 | High Idle Delay Setting | SEC | 0 | 900 | Dodge 98-02 |
| 154 | Warmup Mode Setting | °F | 120 | 200 | ALL |
| 155 | Rail Pressure Defuel | PSI | 24000 | 29000 | Chevy only |
| 181 | Average MPG | — | 0 | 1000 | **HIDDEN** (QZTEST only) |

---

## Segment 4 — Large Values (4-byte, AIDs 185-219)

| AID | Name | Unit | Min | Max | Vehicles |
|-----|------|------|-----|-----|----------|
| 187 | Regen Last Time | SEC | 0 | 1677721 | Dodge 07-09 |
| 188 | Build Date | — | 0 | 100000 | V2 Dodge |

---

## Variable-Length (AIDs 220+)

| AID | Name | Unit | Min | Max | Vehicles |
|-----|------|------|-----|-----|----------|
| 226 | Drive Train Info | INCHES | 95.7 | 120.9 | ALL |

---

## Undocumented AID Gaps (110 unknown)

| Gap Range | Count | Segment | Notes |
|-----------|-------|---------|-------|
| AID 2 | 1 | Seg 1 (1B) | Between Boost and Fuel Temp — what is it? |
| AID 10-11 | 2 | Seg 1 | Near ECM Voltage |
| AID 14 | 1 | Seg 1 | Between Backdown% and PowerLevels |
| AID 23 | 1 | Seg 1 | Between Boost Scaling and Reset |
| AID 25-28 | 4 | Seg 1 | Between Reset and Barometer |
| AID 35-37 | 3 | Seg 1 | Near Fuel Level |
| AID 43-46 | 4 | Seg 1 | Between Friction Torque and Rail Pressure |
| AID 55-58 | 4 | Seg 1 | Near Timing parameters |
| AID 63-74 | 12 | Seg 1 | Entire block before segment 2 boundary |
| AID 79-80 | 2 | Seg 2 | Between RPM and Boost Defuel |
| AID 82 | 1 | Seg 2 | Between Boost Defuel and Rail Pressure |
| AID 95 | 1 | Seg 2 | Near DTC data |
| AID 99 | 1 | Seg 2 | Between Regen filters and O2 sensors |
| AID 106-109 | 4 | Seg 2 | Between RPM Limit and Min Pump Tap |
| AID 144 | 1 | Seg 2 | Between 4000RPM timing and AVG MPG reset |
| AID 151 | 1 | Seg 3 | Between EGT Defuel and Turbo Timer |
| AID 156-180 | 25 | Seg 3 | **HUGE gap** — likely reserved/diagnostic |
| AID 182-186 | 5 | Seg 3/4 | Between Average MPG and Regen Last Time |
| AID 189-225 | 37 | Seg 4 | **HUGE gap** — likely internal calibration |

**Total documented: 117  |  Total undocumented: 110  |  To probe on live device: ALL 256**

---

## Vehicle Profile Coverage Matrix

| AID Category | Dodge 98-02 | Dodge 03-05 | Dodge 06-09 | Chevy 01-05 | Ford 03-07 | V2 Dodge | QZTEST |
|-------------|-------------|-------------|-------------|-------------|------------|----------|--------|
| Basic sensors | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| EGR/DPF data | — | — | ✓ | — | ✓ | — | — |
| Boost fueling curve | — | — | — | — | — | ✓ | ✓ |
| RPM timing curve | — | — | — | — | — | ✓ | ✓ |
| Pump tap parameters | ✓ | — | — | — | — | ✓ | ✓ |
| Hidden MPG AIDs | — | — | — | — | — | — | ✓ |
| Rail pressure tuning | — | ✓ | ✓ | ✓ | ✓ | — | — |
| 4K RPM features | ✓ | — | — | — | — | ✓ | — |

---

*Generated by Claude 4.6 Opus from 14 vehicle profiles + firmware decompilation.*
*To complete: probe AIDs 0-255 on live device to discover undocumented parameters.*
