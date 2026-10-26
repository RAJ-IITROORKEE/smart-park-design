# Bill of materials

Electrical BOM; generic passives are specified by value and size. Unselected MPNs remain procurement gates.

| Refdes | Value | Footprint | MPN / status | Notes |
|---|---|---|---|---|
| U1 | XIAO ESP32-S3 | SmartMark:XIAO_S3_STACK_SOCKET_2x7 | Seeed module stack | Carrier mounting is two 1×7 2.54 mm female sockets, 8.5 mm high; mate the XIAO edge pads through 2.5 mm-shoulder male headers with a 0.6 mm air gap above the plastic (11.6 mm total carrier-to-XIAO plane separation). Seeed module stack is off-carrier and not SMT-placed. |
| BT1 | 3.7V LiPo |  | Protected pack MPN not frozen; confirm protection | Protected 1S LiPo pack with JST-PH2 pigtail. Off-board; verify a real protection circuit and pack polarity. |
| J3 | PH2.0 |  | Off-board JST-PH2 pigtail | Battery pack's PH2 cable connector, off-board; mating and continuity checks required. |
| J4 | XIAO BAT pad |  | XIAO underside pads (symbol only) | Symbolic contact to XIAO underside BAT pads; not a PCB-mounted connector. |
| U2 | TPS61099DRVR | Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm | TPS61099DRVR | TI TPS61099DRVR; adjustable 5 V boost. |
| U3 | SN74LVC1T45DBVR | Package_TO_SOT_SMD:SOT-23-6 | SN74LVC1T45DBVR | TI SN74LVC1T45DBVR; 3.3-to-switched-5 V RGB data translation. |
| U4 | SN74LVC1G17DBVR | Package_TO_SOT_SMD:SOT-23-5 | SN74LVC1G17DBVR | TI SN74LVC1G17DBVR; 5.5 V tolerant sensor echo buffer. |
| J1 | HC-SR04 5V | Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical | UNSELECTED generic value | JST-PH sensor cable; confirm actual harness pin continuity. |
| J2 | 0.96in OLED | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | GoldenMorning GME12864-11 (Robu SKU 617725; optional display) | Optional GoldenMorning GME12864-11 0.96-inch OLED (Robu SKU 617725); connect by cable, not a carrier-mounted display. |
| D1 | WS2812B-2020-V6 | SmartMark:WS2812B_2020_V6 | WS2812B-2020-V6 | Worldsemi WS2812B-2020-V6; custom pads follow the official package-top drawing; it is flipped to B.Cu for the case-floor light pipe. |
| L1 | 2.2uH | SmartMark:VLS3012CX_2R2M | TDK VLS3012CX-2R2M-1 | TDK VLS3012CX-2R2M-1; TDK 3×3×1.2 mm part, 1.7 A max inductance-change rating; local 1.0 mm land pads on 3.0 mm centers. |
| C1 | 10uF 10V X7R | Capacitor_SMD:C_0805_2012Metric | GRM21BR71A106KE51L | Murata GRM21BR71A106KE51L; 10 µF, 10 V, X7R, 0805 boost input bypass. |
| C2 | 22uF 16V X7R | Capacitor_SMD:C_1206_3216Metric | GRM31CZ71C226ME15L | Murata GRM31CZ71C226ME15L; 22 µF, 16 V, X7R, 1206 boost output capacitor. |
| C3 | 22uF 16V X7R | Capacitor_SMD:C_1206_3216Metric | GRM31CZ71C226ME15L | Murata GRM31CZ71C226ME15L; 22 µF, 16 V, X7R, 1206 boost output capacitor. |
| C4 | 100nF | Capacitor_SMD:C_0603_1608Metric | UNSELECTED generic value | 100 nF local bypass for the SN74LVC1G17 sensor buffer. |
| C5 | 100nF | Capacitor_SMD:C_0603_1608Metric | UNSELECTED generic value | 100 nF local bypass for SN74LVC1T45 VCCB (switched 5 V). |
| C6 | 100nF | Capacitor_SMD:C_0603_1608Metric | UNSELECTED generic value | 100 nF local bypass for SN74LVC1T45 VCCA (3.3 V). |
| C7 | 100nF | Capacitor_SMD:C_0603_1608Metric | UNSELECTED generic value | 100 nF local 5 V bypass adjacent to the bottom-side RGB pixel. |
| R1 | 1M | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R2 | 249k | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R3 | 100k EN pulldown | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R4 | 100k HC_ECHO pulldown | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R5 | 330R LED series | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R6 | 100k LED_DIN pulldown | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R7 | 100k LED_DATA pulldown | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R8 | 4.7k SDA pullup | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| R9 | 4.7k SCL pullup | Resistor_SMD:R_0603_1608Metric | UNSELECTED generic value | Generic passive; confirm effective value and rating at bias. |
| TP1 | 3V3 | TestPoint:TestPoint_Pad_D1.0mm | test pad | 3V3 bare copper test pad. |
| TP2 | GND | TestPoint:TestPoint_Pad_D1.0mm | test pad | GND bare copper test pad. |
| TP3 | 5V_SENSOR | TestPoint:TestPoint_Pad_D1.0mm | test pad | 5V_SENSOR bare copper test pad. |
| TP4 | HC_ECHO | TestPoint:TestPoint_Pad_D1.0mm | test pad | HC_ECHO bare copper test pad. |
| TP5 | ECHO_GPIO | TestPoint:TestPoint_Pad_D1.0mm | test pad | ECHO_GPIO bare copper test pad. |

U1 is a socket interface: fit two 1×7 2.54 mm female sockets (8.5 mm body height) on the carrier and mating male headers with a 2.5 mm shoulder and at least 3 mm short legs on the XIAO edge pads. Use a removable 0.6 mm soldering shim to leave air above the shoulder; remove it after soldering. This clears the USB anchors and gives 11.6 mm total separation. The assembled XIAO ESP32-S3/Wio-SX1262 stack plugs into the carrier; do not SMT-place the Seeed module as a PCB component. Verify the actual socket/header heights and sample fit before release.
BT1/J3/J4 are off-board battery components and contacts; do not place them on the carrier. Verify pack protection, polarity and continuity; HC-SR04 module/revision and cable; OLED unit fit; and TDK land-pattern compatibility with the chosen assembly process. Capacitor bias estimates are typical supplier curves and need board-level startup/transient validation.
