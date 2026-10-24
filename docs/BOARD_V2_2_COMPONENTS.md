# Board V2.2: reported component inventory

Recorded 2026-10-24 from the owner's board inspection and supplied component
list. Board revision: **V2.2**. These are user-reported markings, not an
independent inspection of board photographs or electrical measurements by
this project. No photograph, schematic, continuity map, oscillator measurement
or installed-firmware readback accompanied this report.

The owner's later identifications of U9/U10 supersede their earlier
partially legible ST markings. They do not resolve U11.

| Position | Reported marking | Interpretation and evidence limit |
|---|---|---|
| U1 | AT91SAM7S64 | Reported main MCU; consistent with the firmware's SAM7S peripheral map. Exact package/suffix unrecorded. |
| U2 | MCP2515 | Reported CAN controller; independently corroborates the firmware's MCP2515-compatible command interpretation. Wiring and live operation remain unmeasured. |
| U3 | Appears to read MCP2551 | Tentative CAN transceiver identification; marking needs confirmation. |
| U7 | ST `2903` | Likely LM2903-family dual comparator; exact device/suffix and circuit function unresolved. |
| U8 | AD597A | Reported thermocouple amplifier marking; AD597 is specified for Type K thermocouples. Installed probe, calibration and MCU signal path unverified. |
| U9 | ST `2902` | High-confidence reported LM2902-family quad op amp identification; exact suffix and individual channel functions unresolved. |
| U10 | ST `2902` | Same family interpretation as U9; channel functions unresolved. |
| U11 | `04227AN` or similar | Unidentified. Preserve the tentative transcription; do not assign a part number from this alone. |
| Y1 | `EC18.4` | Possible 18.4 MHz crystal; nominal frequency and connected device unconfirmed. |
| Metal package near U2 | Partially legible | Possible second crystal; marking, frequency and connections unresolved. |
| Metal package marked `250` | `250` | Possible power-supply inductor; component type, units and value unconfirmed. |

## Manufacturer references and interpretation

ST's [LM2902 datasheet](https://www.st.com/resource/en/datasheet/lm2902.pdf)
lists the quad op amp family and a `2902` marking in its order-code table.
This supports the family interpretation when the reported ST logo, marking
and package agree; it does not identify the board's analog channel functions.
Analog Devices' [AD597 product page](https://www.analog.com/en/products/ad597.html)
specifies Type K thermocouple operation. Microchip's
[MCP2515 product page](https://www.microchip.com/en-us/product/mcp2515)
identifies it as a standalone CAN controller with an SPI interface.

The firmware [SPI/CAN command audit](SPI_CAN_CONTROLLER_REVIEW.md) was derived
from the exact V2.8.4HF image independently of these reported markings. U2's
identification supplies corroborating hardware context. Its generated artifact
retains `physical_part_verified: false`: the artifact is an offline image audit,
not a physical inspection record. The installed firmware version has not yet
been matched to the analyzed image.

The op amps, comparator and thermocouple amplifier provide candidates for
tracing the analog interfaces. Assigning any of their pins to a sensor,
pump signal, ADC channel or control output requires connectivity evidence.
Do not infer a schematic from proximity alone.

## Most useful next observations

1. Preserve clear photographs of both board faces, revision text, IC markings
   and connector orientation, including U3, U7, U11 and both crystal packages.
2. With the board unpowered, establish continuity from MCU SPI pins to U2,
   U2 to the tentative U3, and U3 to connector pins. Record actual pin numbers
   and measured connections rather than assumed signal names.
3. Identify which device each crystal connects to before using its frequency
   to calculate MCU clocks or CAN bit timing. Y1's tentative marking cannot
   establish the MCP2515 oscillator frequency.
4. Trace U8's output and U9/U10/U7 channels toward the MCU and connectors;
   record resistor networks and measured values where accessible.
5. Establish the installed firmware version through the existing normal
   interface, then plan passive captures of normal startup and operation.

No power, programming, traffic injection or board modification was performed
to create this inventory. Input power pins and test-point voltages remain
unverified; this document is not a bench wiring guide.
