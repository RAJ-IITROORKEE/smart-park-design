#!/usr/bin/env python3
"""Generate revision-d electrical intent, custom symbols, and review docs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PARTS = [
    {"ref": "U1", "libId": "SmartMark:XIAO_S3_WIO_STACK", "value": "XIAO ESP32-S3", "footprint": "SmartMark:XIAO_S3_STACK_SOCKET_2x7", "group": "Controller stack"},
    {"ref": "BT1", "libId": "SmartMark:Protected_LiPo", "value": "3.7V LiPo", "footprint": "", "group": "Battery harness"},
    {"ref": "J3", "libId": "Connector_Generic:Conn_01x02", "value": "PH2.0", "footprint": "", "group": "Battery harness"},
    {"ref": "J4", "libId": "SmartMark:XIAO_BAT_CONTACTS", "value": "XIAO BAT pad", "footprint": "", "group": "Battery harness"},
    {"ref": "U2", "libId": "SmartMark:TPS61099DRV", "value": "TPS61099DRVR", "footprint": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "group": "5V sensor supply"},
    {"ref": "U3", "libId": "Logic_LevelTranslator:SN74LVC1T45DBV", "value": "SN74LVC1T45DBVR", "footprint": "Package_TO_SOT_SMD:SOT-23-6", "group": "Optional RGB"},
    {"ref": "U4", "libId": "74xGxx:74LVC1G17", "value": "SN74LVC1G17DBVR", "footprint": "Package_TO_SOT_SMD:SOT-23-5", "group": "HC-SR04 interface"},
    {"ref": "J1", "libId": "Connector_Generic:Conn_01x04", "value": "HC-SR04 5V", "footprint": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "group": "HC-SR04 interface"},
    {"ref": "J2", "libId": "Connector_Generic:Conn_01x04", "value": "0.96in OLED", "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "group": "Optional OLED"},
    {"ref": "D1", "libId": "SmartMark:WS2812B_2020_V6", "value": "WS2812B-2020-V6", "footprint": "SmartMark:WS2812B_2020_V6", "group": "Optional RGB"},
    {"ref": "L1", "libId": "Device:L", "value": "2.2uH", "footprint": "SmartMark:VLS3012CX_2R2M", "group": "5V sensor supply"},
    {"ref": "C1", "libId": "Device:C", "value": "10uF 10V X7R", "footprint": "Capacitor_SMD:C_0805_2012Metric", "group": "5V sensor supply"},
    {"ref": "C2", "libId": "Device:C", "value": "22uF 16V X7R", "footprint": "Capacitor_SMD:C_1206_3216Metric", "group": "5V sensor supply"},
    {"ref": "C3", "libId": "Device:C", "value": "22uF 16V X7R", "footprint": "Capacitor_SMD:C_1206_3216Metric", "group": "5V sensor supply"},
    {"ref": "C4", "libId": "Device:C", "value": "100nF", "footprint": "Capacitor_SMD:C_0603_1608Metric", "group": "HC-SR04 interface"},
    {"ref": "C5", "libId": "Device:C", "value": "100nF", "footprint": "Capacitor_SMD:C_0603_1608Metric", "group": "Optional RGB"},
    {"ref": "C6", "libId": "Device:C", "value": "100nF", "footprint": "Capacitor_SMD:C_0603_1608Metric", "group": "Optional RGB"},
    {"ref": "C7", "libId": "Device:C", "value": "100nF", "footprint": "Capacitor_SMD:C_0603_1608Metric", "group": "Optional RGB"},
    {"ref": "R1", "libId": "Device:R", "value": "1M", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "5V sensor supply"},
    {"ref": "R2", "libId": "Device:R", "value": "249k", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "5V sensor supply"},
    {"ref": "R3", "libId": "Device:R", "value": "100k EN pulldown", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "5V sensor supply"},
    {"ref": "R4", "libId": "Device:R", "value": "100k HC_ECHO pulldown", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "HC-SR04 interface"},
    {"ref": "R5", "libId": "Device:R", "value": "330R LED series", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "Optional RGB"},
    {"ref": "R6", "libId": "Device:R", "value": "100k LED_DIN pulldown", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "Optional RGB"},
    {"ref": "R7", "libId": "Device:R", "value": "100k LED_DATA pulldown", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "Optional RGB"},
    {"ref": "R8", "libId": "Device:R", "value": "4.7k SDA pullup", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "Optional OLED"},
    {"ref": "R9", "libId": "Device:R", "value": "4.7k SCL pullup", "footprint": "Resistor_SMD:R_0603_1608Metric", "group": "Optional OLED"},
    {"ref": "TP1", "libId": "Connector:TestPoint", "value": "3V3", "footprint": "TestPoint:TestPoint_Pad_D1.0mm", "group": "Bring-up test points"},
    {"ref": "TP2", "libId": "Connector:TestPoint", "value": "GND", "footprint": "TestPoint:TestPoint_Pad_D1.0mm", "group": "Bring-up test points"},
    {"ref": "TP3", "libId": "Connector:TestPoint", "value": "5V_SENSOR", "footprint": "TestPoint:TestPoint_Pad_D1.0mm", "group": "Bring-up test points"},
    {"ref": "TP4", "libId": "Connector:TestPoint", "value": "HC_ECHO", "footprint": "TestPoint:TestPoint_Pad_D1.0mm", "group": "Bring-up test points"},
    {"ref": "TP5", "libId": "Connector:TestPoint", "value": "ECHO_GPIO", "footprint": "TestPoint:TestPoint_Pad_D1.0mm", "group": "Bring-up test points"},
]

NETS = [
    {"name": "BAT_POS", "kind": "power", "pins": ["BT1.1", "J3.1", "J4.1"]},
    {"name": "3V3", "kind": "power", "pins": ["U1.12", "U2.6", "U3.1", "U3.5", "U4.5", "J2.2", "L1.1", "C1.1", "C4.1", "C6.1", "R8.1", "R9.1", "TP1.1"]},
    {"name": "GND", "kind": "ground", "pins": ["BT1.2", "J3.2", "J4.2", "U1.13", "U2.1", "U2.7", "U3.2", "U4.3", "J1.4", "J2.1", "D1.2", "C1.2", "C2.2", "C3.2", "C4.2", "C5.2", "C6.2", "C7.2", "R2.2", "R3.2", "R4.2", "R6.2", "R7.2", "TP2.1"]},
    {"name": "5V_SENSOR", "kind": "power", "pins": ["U2.2", "U3.6", "J1.1", "D1.4", "C2.1", "C3.1", "C5.1", "C7.1", "R1.1", "TP3.1"]},
    {"name": "BOOST_SW", "kind": "signal", "pins": ["U2.5", "L1.2"]},
    {"name": "BOOST_FB", "kind": "signal", "pins": ["U2.3", "R1.2", "R2.1"]},
    {"name": "BOOST_EN", "kind": "signal", "pins": ["U2.4", "U1.4", "R3.1"]},
    {"name": "HC_TRIG", "kind": "signal", "pins": ["U1.1", "J1.2"]},
    {"name": "HC_ECHO", "kind": "signal", "pins": ["J1.3", "U4.2", "R4.1", "TP4.1"]},
    {"name": "ECHO_GPIO", "kind": "signal", "pins": ["U4.4", "U1.2", "TP5.1"]},
    {"name": "I2C_SDA", "kind": "signal", "pins": ["U1.5", "J2.4", "R8.2"]},
    {"name": "I2C_SCL", "kind": "signal", "pins": ["U1.6", "J2.3", "R9.2"]},
    {"name": "LED_DATA_3V3", "kind": "signal", "pins": ["U1.7", "U3.3", "R7.1"]},
    {"name": "LED_DATA_5V", "kind": "signal", "pins": ["U3.4", "R5.1"]},
    {"name": "LED_DIN", "kind": "signal", "pins": ["R5.2", "D1.3", "R6.1"]},
]

NO_CONNECTS = ["U1.3", "U1.8", "U1.9", "U1.10", "U1.11", "U1.14", "U4.1", "D1.1"]

SYMBOL_PINS = {
    "SmartMark:XIAO_S3_WIO_STACK": {str(n) for n in range(1, 15)},
    "SmartMark:Protected_LiPo": {"1", "2"},
    "SmartMark:XIAO_BAT_CONTACTS": {"1", "2"},
    "Connector_Generic:Conn_01x02": {"1", "2"},
    "SmartMark:TPS61099DRV": {str(n) for n in range(1, 8)},
    "Logic_LevelTranslator:SN74LVC1T45DBV": {str(n) for n in range(1, 7)},
    "74xGxx:74LVC1G17": {str(n) for n in range(1, 6)},
    "Connector_Generic:Conn_01x04": {str(n) for n in range(1, 5)},
    "SmartMark:WS2812B_2020_V6": {str(n) for n in range(1, 5)},
    "Device:L": {"1", "2"}, "Device:C": {"1", "2"}, "Device:R": {"1", "2"},
    "Connector:TestPoint": {"1"},
}


def q(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def symbol_pin(number: int, name: str, etype: str, x: float, y: float, angle: int, length: float = 5.08) -> str:
    return (
        f'\t\t(pin {etype} line (at {x:g} {y:g} {angle}) (length {length:g})\n'
        f'\t\t\t(name {q(name)} (effects (font (size 1 1))))\n'
        f'\t\t\t(number {q(str(number))} (effects (font (size 1 1))))\n\t\t)'
    )


def symbol_block(name: str, ref: str, value: str, description: str, body: list[str]) -> str:
    graphics = "\n".join(item for item in body if not item.lstrip().startswith("(pin "))
    pins = "\n".join(item for item in body if item.lstrip().startswith("(pin "))
    return f'''\t(symbol {q(name)}
\t\t(pin_names (offset 0.508))
\t\t(property "Reference" {q(ref)} (at 0 2.54 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Value" {q(value)} (at 0 -2.54 0) (effects (font (size 1.27 1.27)) (justify left top)))
\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "ki_description" {q(description)} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
\t\t(symbol {q(name + "_0_1")}\n{graphics}\n\t\t)
\t\t(symbol {q(name + "_1_1")}\n{pins}\n\t\t)
\t)'''


def custom_symbols() -> str:
    body = ["\t\t(rectangle (start -5.08 10.16) (end 5.08 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))"]
    left = [(1, "D0/GPIO1"), (2, "D1/GPIO2"), (3, "D2/GPIO3"), (4, "D3/GPIO4"), (5, "D4/SDA"), (6, "D5/SCL"), (7, "D6/TX43")]
    right = [(14, "VBUS"), (13, "GND"), (12, "3V3"), (11, "D10/MOSI"), (10, "D9/MISO"), (9, "D8/SCK"), (8, "D7/RX44")]
    for i, (num, name) in enumerate(left):
        body.append(symbol_pin(num, name, "bidirectional", -10.16, 7.62 - 2.54 * i, 0))
    for i, (num, name) in enumerate(right):
        etype = "power_in" if num in (13, 14) else "power_out" if num == 12 else "bidirectional"
        body.append(symbol_pin(num, name, etype, 10.16, 7.62 - 2.54 * i, 180))
    stack = symbol_block("XIAO_S3_WIO_STACK", "U", "XIAO ESP32-S3 + Wio-SX1262", "Seeed stack with outer-pad numbering per official XIAO footprint.", body)

    boost_body = ["\t\t(rectangle (start -5.08 7.62) (end 5.08 -7.62) (stroke (width 0.254) (type default)) (fill (type background)))"]
    boost_body += [
        symbol_pin(6, "VIN", "power_in", -10.16, 5.08, 0),
        symbol_pin(4, "EN", "input", -10.16, 0, 0),
        symbol_pin(1, "GND", "power_in", -10.16, -5.08, 0),
        # SW is a switching node into L1, not a DC power rail; passive avoids a false ERC source requirement.
        symbol_pin(5, "SW", "passive", 10.16, 5.08, 180),
        symbol_pin(3, "FB", "input", 10.16, 0, 180),
        symbol_pin(2, "VOUT", "power_out", 10.16, -5.08, 180),
        symbol_pin(7, "GND", "power_in", 0, -12.7, 90, 5.08),
    ]
    boost = symbol_block("TPS61099DRV", "U", "TPS61099DRVR", "TI adjustable boost; SW is a passive switching node to L1; PowerPAD pin 7 connects to GND.", boost_body)

    led_body = ["\t\t(rectangle (start -3.81 5.08) (end 3.81 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))"]
    led_body += [
        symbol_pin(1, "DOUT", "output", 8.89, 2.54, 180),
        symbol_pin(2, "GND", "power_in", -8.89, 2.54, 0),
        symbol_pin(3, "DIN", "input", -8.89, 0, 0),
        symbol_pin(4, "VDD", "power_in", -8.89, -2.54, 0),
    ]
    led = symbol_block("WS2812B_2020_V6", "D", "WS2812B-2020-V6", "Worldsemi pad map: 1 DOUT, 2 GND, 3 DIN, 4 VDD.", led_body)
    battery_body = ["\t\t(rectangle (start -5.08 5.08) (end 5.08 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))"]
    battery_body += [symbol_pin(1, "BAT+", "power_out", -10.16, 2.54, 0), symbol_pin(2, "GND", "power_out", -10.16, -2.54, 0)]
    battery = symbol_block("Protected_LiPo", "BT", "Protected 1S LiPo", "Off-board protected one-cell pack with JST-PH2 pigtail; verify protection, chemistry, connector, and polarity on the purchased pack.", battery_body)
    contact_body = ["\t\t(rectangle (start -5.08 5.08) (end 5.08 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))"]
    contact_body += [symbol_pin(1, "BAT+", "passive", 10.16, 2.54, 180), symbol_pin(2, "GND", "passive", 10.16, -2.54, 180)]
    contacts = symbol_block("XIAO_BAT_CONTACTS", "J", "XIAO underside BAT pads", "Off-board solder contacts: connect the protected battery pigtail to the XIAO ESP32-S3 underside BAT pads before mating the Wio stack.", contact_body)
    return '(kicad_symbol_lib\n\t(version 20231120)\n\t(generator "kicad_symbol_editor")\n' + stack + "\n" + boost + "\n" + led + "\n" + battery + "\n" + contacts + "\n)\n"


def stack_socket_footprint() -> str:
    # The XIAO component face points down. Keeping its USB edge toward board y=0 mirrors
    # the manufacturer front view across X, so D0 is on the carrier's right-hand row.
    pads = []
    for number in range(1, 8):
        pads.append(f'\t(pad "{number}" thru_hole roundrect (at 7.62 {-7.62 + 2.54 * (number - 1):g}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.15))')
    for number in range(8, 15):
        pads.append(f'\t(pad "{number}" thru_hole roundrect (at -7.62 {7.62 - 2.54 * (number - 8):g}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.15))')
    return '\n'.join([
        '(footprint "XIAO_S3_STACK_SOCKET_2x7" (version 20240108) (generator "pcbnew")',
        '\t(layer "F.Cu")',
        '\t(attr through_hole)',
        '\t(property "Reference" "U1" (at 0 -10.8 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        '\t(property "Value" "XIAO ESP32-S3 + Wio-SX1262" (at 0 10.8 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_rect (start -10.5 -8.9) (end 10.5 8.9) (stroke (width 0.12) (type default)) (fill none) (layer "F.Fab"))',
        '\t(fp_line (start -8.6 -9.6) (end 8.6 -9.6) (stroke (width 0.15) (type default)) (layer "F.SilkS"))',
        '\t(fp_text user "USB / REAR" (at 0 -9.2 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        *pads,
        ')',
        ''
    ])


def tdk_inductor_footprint() -> str:
    # TDK's published VLS3012CX land pattern is two 1.0 mm lands on 3.0 mm centers.
    return '''(footprint "VLS3012CX_2R2M" (version 20240108) (generator "pcbnew")
\t(layer "F.Cu")
\t(attr smd)
\t(property "Reference" "L1" (at 0 -2.3 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
\t(property "Value" "VLS3012CX-2R2M-1" (at 0 2.3 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))
\t(fp_rect (start -1.5 -1.5) (end 1.5 1.5) (stroke (width 0.12) (type default)) (fill none) (layer "F.Fab"))
\t(fp_rect (start -2 -2) (end 2 2) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
\t(pad "1" smd rect (at -1.5 0) (size 1 1) (layers "F.Cu" "F.Paste" "F.Mask"))
\t(pad "2" smd rect (at 1.5 0) (size 1 1) (layers "F.Cu" "F.Paste" "F.Mask"))
)
'''


def ws2812b_footprint() -> str:
    # F.Cu coordinates exactly match Worldsemi's package-top drawing. The PCB
    # generator flips this footprint to B.Cu, so KiCad mirrors X for the carrier.
    return '''(footprint "WS2812B_2020_V6" (version 20240108) (generator "pcbnew")
\t(layer "F.Cu")
\t(attr smd)
\t(property "Reference" "D1" (at 0 -1.7 0) (layer "F.SilkS") (effects (font (size 0.65 0.65) (thickness 0.1))))
\t(property "Value" "WS2812B-2020-V6" (at 0 1.7 0) (layer "F.Fab") (effects (font (size 0.55 0.55) (thickness 0.1))))
\t(fp_rect (start -1 -1) (end 1 1) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
\t(fp_circle (center 0.65 -0.65) (end 0.85 -0.65) (stroke (width 0.12) (type default)) (fill none) (layer "F.Fab"))
\t(fp_rect (start -1.4 -1.4) (end 1.4 1.4) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
\t(pad "3" smd rect (at -0.915 -0.55) (size 0.7 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))
\t(pad "4" smd rect (at -0.915 0.55) (size 0.7 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))
\t(pad "2" smd rect (at 0.915 -0.55) (size 0.7 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))
\t(pad "1" smd rect (at 0.915 0.55) (size 0.7 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))
)
'''


def pinout_doc() -> str:
    return """# XIAO and Wio carrier pin map

This page records the manufacturer pad map and the flipped carrier orientation used by this board.

| Carrier net | XIAO pad | Signal | GPIO | Use |
|---|---:|---|---:|---|
| HC_TRIG | 1 | D0 | GPIO1 | Sensor trigger |
| ECHO_GPIO | 2 | D1 | GPIO2 | Buffered sensor echo |
| NC | 3 | D2 | GPIO3 | Reserved; ESP32-S3 strapping pin |
| BOOST_EN | 4 | D3 | GPIO4 | Boost enable, active high |
| I2C_SDA | 5 | D4/SDA | GPIO5 | Optional OLED |
| I2C_SCL | 6 | D5/SCL | GPIO6 | Optional OLED |
| LED_DATA_3V3 | 7 | D6/TX | GPIO43 | RGB data; UART0 TX during boot |
| NC | 8 | D7/RX | GPIO44 | Reserved |
| NC | 9 | D8/SCK | GPIO7 | Wio radio SPI reserved |
| NC | 10 | D9/MISO | GPIO8 | Wio radio SPI reserved |
| NC | 11 | D10/MOSI | GPIO9 | Wio radio SPI reserved |
| 3V3 | 12 | 3V3_OUT | — | XIAO output |
| GND | 13 | GND | — | Return |
| NC | 14 | VBUS | — | USB-C stays on XIAO |

The carrier is 62×50 mm at KiCad coordinates x=0…62, y=0…50. The stack is centered at (31,10.5), USB facing the board's rear edge y=0, with XIAO components facing down toward the carrier. This mirrors the manufacturer's component-front diagram across X: from the carrier top, D0–D6 are on the right row; VBUS/GND/3V3/D10–D7 are on the left row. The rows are x=23.38 and x=38.62 at 2.54 mm pitch. Pad1/D0=(38.62,2.88), pad7/D6=(38.62,18.12), pad8/D7=(23.38,18.12), pad14/VBUS=(23.38,2.88). This orientation is supported by Seeed's front pinout image, not inferred from the STEP's unlabelled solids.

Board-to-case placement: case X = board X − 31, case Y = 25 − board Y, case Z = 21.535 + board Z. The 0.035 mm carrier datum leaves the outer copper seat at case Z=21.5 mm. This stack/board envelope is based on vendor CAD and still needs a physical sample fit.

Battery is an off-board harness. BT1 is a protected 1S LiPo pack, J3 its JST-PH2 pigtail connector, and J4 symbolizes the XIAO's actual underside BAT+/BAT− solder pads, not a carrier connector. Solder the lead before mating the Wio module, verify actual polarity and continuity, and confirm that the purchased pack includes protection. BT1, J3, and J4 are excluded from the carrier PCB.

The Wio-SX1262 radio connects internally to the XIAO stack. Its external DIO/BUSY/RESET/NSS/RF_SW connections are not carrier nets; D8/D9/D10 are reserved for radio SPI. Seeed references: [XIAO ESP32-S3 pinout and dimensions](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/), [XIAO KiCad library](https://files.seeedstudio.com/wiki/XIAO-KiCad-Library/New_XIAO_Series_Footprints.zip), [Wio-SX1262 STEP](https://files.seeedstudio.com/products/SenseCAP/Wio_SX1262/Wio-SX1262_for_XIAO_3D_file.step).

Firmware startup: leave D2/GPIO3 unconnected because it is an ESP32-S3 strapping pin. D6/GPIO43 is UART0 TX during boot, so hold BOOST_EN low and initialize the LED data output low before enabling 5V_SENSOR; then allow the pixel supply/data and HC-SR04 to settle for at least 60 ms before the first measurement cycle.
"""


def power_doc() -> str:
    return """# Electrical power and interface notes

This page records power boundaries and bench-test gates for the revision-d carrier.

Use only an externally regulated 5 V source through the XIAO USB-C connector. Solar panels must be regulated to 5 V upstream; no raw panel connection is on this PCB. Use service USB or the regulated solar feed, never both through a Y cable. The XIAO onboard charger is the only cell charger. A protected LiPo pigtail is soldered to the XIAO BAT pads before the stack is assembled; verify protection, chemistry, polarity, and connector on the actual pack.

U2 is TI TPS61099DRVR, adjustable boost from XIAO 3V3 to 5V_SENSOR. R1/R2=1M/249k set about 5.016 V using the 1.0 V feedback reference. Follow the TI reference circuit: 2.2 µH inductor, 10 µF input capacitor, and two 22 µF output capacitors; Murata GRM31CZ71C226ME15L provides about 15.6 µF typical per part at 5.016 V, leaving over 20 µF combined under the documented conservative derating. GPIO4/D3 drives EN; 100 kΩ pulls it low through reset. The TPS61099 provides true load disconnect in shutdown. In the project symbol, SW is typed passive because it is a switching node feeding L1, not a DC power rail; this avoids a false ERC driver requirement without adding a PWR_FLAG to that node.

5V_SENSOR powers HC-SR04 and the optional WS2812B-2020-V6. Reserve 75 mA for initial review (15 mA sensor plus conservative 60 mA pixel budget); firmware must limit pixel brightness. Verify XIAO/Wio 3V3 rail margin during radio transmit and sensor/pixel startup.

J1 pin order is 1=5V_SENSOR, 2=TRIG, 3=ECHO, 4=GND. GPIO1/D0 drives TRIG directly at 3.3 V; confirm the purchased HC-SR04 accepts that level. HC_ECHO feeds TI SN74LVC1G17 at U4, powered at 3V3; the device input accepts up to 5.5 V and output is 3.3 V logic. R4 pulls the cable input low when unplugged. Verify the exact module’s echo high level, ringing, cable pin order, trigger VIH, and current before release.

U3 SN74LVC1T45 translates GPIO43/D6 data from 3V3 to switched 5V_SENSOR. C5 decouples VCCB at U3, C6 decouples VCCA there, and C7 bypasses 5V_SENSOR beside the bottom-side pixel; C4 remains the local U4 bypass. DIR is high for A-to-B; 100 kΩ pulldowns hold both data nodes low and 330 Ω is in series with pixel DIN. Its Ioff behavior is intended to avoid back-driving the unpowered 5 V side. J2 is optional 2.54 mm OLED: 1 GND, 2 3V3, 3 SCL, 4 SDA; board pullups are 4.7 kΩ, so check module onboard pullups before fitting.

At reset, keep BOOST_EN low and initialize GPIO43/D6 low before turning on 5V_SENSOR. GPIO43 is UART0 TX during boot; GPIO3/D2 is an ESP32-S3 strapping pin and remains unused. Wait at least 60 ms after enabling the sensor/pixel supply before the first HC-SR04 measurement cycle.

This is not production-qualified without testing the selected HC-SR04, protected battery, solar regulator, XIAO/Wio stack, OLED, pixel, board assembly, radio-transmit brownout margin, and case fit. Primary sources: [TPS61099 datasheet](https://www.ti.com/lit/ds/symlink/tps61099.pdf), [SN74LVC1G17 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf), [SN74LVC1T45 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf), [Seeed XIAO pinout/power](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/), [Worldsemi WS2812B-2020-V6](https://www.world-semi.com/ws2812-family/223.html).
"""


def bom_doc() -> str:
    notes = {
        "U1": "Carrier mounting is two 1×7 2.54 mm female sockets, 8.5 mm high; mate the XIAO edge pads through 2.5 mm-shoulder male headers with a 0.6 mm air gap above the plastic (11.6 mm total carrier-to-XIAO plane separation). Seeed module stack is off-carrier and not SMT-placed.",
        "U2": "TI TPS61099DRVR; adjustable 5 V boost.",
        "U3": "TI SN74LVC1T45DBVR; 3.3-to-switched-5 V RGB data translation.",
        "U4": "TI SN74LVC1G17DBVR; 5.5 V tolerant sensor echo buffer.",
        "J1": "JST-PH sensor cable; confirm actual harness pin continuity.",
        "J2": "Optional GoldenMorning GME12864-11 0.96-inch OLED (Robu SKU 617725); connect by cable, not a carrier-mounted display.",
        "BT1": "Protected 1S LiPo pack with JST-PH2 pigtail. Off-board; verify a real protection circuit and pack polarity.",
        "J3": "Battery pack's PH2 cable connector, off-board; mating and continuity checks required.",
        "J4": "Symbolic contact to XIAO underside BAT pads; not a PCB-mounted connector.",
        "D1": "Worldsemi WS2812B-2020-V6; custom pads follow the official package-top drawing; it is flipped to B.Cu for the case-floor light pipe.",
        "L1": "TDK VLS3012CX-2R2M-1; TDK 3×3×1.2 mm part, 1.7 A max inductance-change rating; local 1.0 mm land pads on 3.0 mm centers.",
        "C1": "Murata GRM21BR71A106KE51L; 10 µF, 10 V, X7R, 0805 boost input bypass.",
        "C2": "Murata GRM31CZ71C226ME15L; 22 µF, 16 V, X7R, 1206 boost output capacitor.",
        "C3": "Murata GRM31CZ71C226ME15L; 22 µF, 16 V, X7R, 1206 boost output capacitor.",
        "C4": "100 nF local bypass for the SN74LVC1G17 sensor buffer.",
        "C5": "100 nF local bypass for SN74LVC1T45 VCCB (switched 5 V).",
        "C6": "100 nF local bypass for SN74LVC1T45 VCCA (3.3 V).",
        "C7": "100 nF local 5 V bypass adjacent to the bottom-side RGB pixel.",
        "TP1": "3V3 bare copper test pad.", "TP2": "GND bare copper test pad.",
        "TP3": "5V_SENSOR bare copper test pad.", "TP4": "HC_ECHO bare copper test pad.",
        "TP5": "ECHO_GPIO bare copper test pad.",
    }
    lines = ["# Bill of materials", "", "Electrical BOM; generic passives are specified by value and size. Unselected MPNs remain procurement gates.", "", "| Refdes | Value | Footprint | MPN / status | Notes |", "|---|---|---|---|---|"]
    for part in PARTS:
        ref = part["ref"]
        mpn = {"U1": "Seeed module stack", "BT1": "Protected pack MPN not frozen; confirm protection", "J3": "Off-board JST-PH2 pigtail", "J4": "XIAO underside pads (symbol only)", "U2": "TPS61099DRVR", "U3": "SN74LVC1T45DBVR", "U4": "SN74LVC1G17DBVR", "D1": "WS2812B-2020-V6", "C1": "GRM21BR71A106KE51L", "C2": "GRM31CZ71C226ME15L", "C3": "GRM31CZ71C226ME15L"}.get(ref, "UNSELECTED generic value")
        if ref == "L1":
            mpn = "TDK VLS3012CX-2R2M-1"
        if ref == "J2":
            mpn = "GoldenMorning GME12864-11 (Robu SKU 617725; optional display)"
        if ref.startswith("TP"):
            mpn = "test pad"
        lines.append(f"| {ref} | {part['value']} | {part['footprint']} | {mpn} | {notes.get(ref, 'Generic passive; confirm effective value and rating at bias.')} |")
    lines += ["", "U1 is a socket interface: fit two 1×7 2.54 mm female sockets (8.5 mm body height) on the carrier and mating male headers with a 2.5 mm shoulder and at least 3 mm short legs on the XIAO edge pads. Use a removable 0.6 mm soldering shim to leave air above the shoulder; remove it after soldering. This clears the USB anchors and gives 11.6 mm total separation. The assembled XIAO ESP32-S3/Wio-SX1262 stack plugs into the carrier; do not SMT-place the Seeed module as a PCB component. Verify the actual socket/header heights and sample fit before release.", "BT1/J3/J4 are off-board battery components and contacts; do not place them on the carrier. Verify pack protection, polarity and continuity; HC-SR04 module/revision and cable; OLED unit fit; and TDK land-pattern compatibility with the chosen assembly process. Capacitor bias estimates are typical supplier curves and need board-level startup/transient validation.", ""]
    return "\n".join(lines)


def subsystems_doc() -> str:
    return """# Subsystems

Electrical blocks grouped by the revision-d deterministic schematic generator.

## Controller stack

U1 represents the XIAO ESP32-S3 with Wio-SX1262 stacked above it. The carrier connects the XIAO outer header pads; the Wio radio signals remain internal to the stack.

## Battery harness

BT1 and J3 are the off-board protected LiPo and its JST-PH2 pigtail, wired to J4, a symbol for the XIAO underside BAT pads rather than a carrier connector.

## HC-SR04 interface

J1 carries 5V_SENSOR, TRIG, ECHO, and GND. U4 buffers the module echo to 3.3 V GPIO; XIAO D0/GPIO1 drives the trigger directly.

## 5V sensor supply

U2 boosts 3V3 to a GPIO4-enabled 5V_SENSOR rail for the sensor and optional RGB pixel, with TI reference feedback and bypassing.

## Optional OLED

J2 is a 4-pin 3.3 V I2C header with board pullups. The selected display is GoldenMorning GME12864-11 (Robu 617725); confirm the delivered module matches its drawing.

## Optional RGB

U3 shifts XIAO D6 data to switched 5V_SENSOR for the pixel. Pulldowns and a series resistor keep the pixel stable during power transitions.

## Bring-up test points

TP1–TP5 expose 3V3, GND, 5V_SENSOR, HC_ECHO, and ECHO_GPIO during controlled validation.
"""


def models_doc() -> str:
    return """# STEP component models

The local KiCad model package is incomplete, so project-local clearance envelopes fill only the missing footprints.

| Footprint | STEP bounds (mm) | Basis and limit |
|---|---:|---|
| D1 WS2812B-2020-V6 | 2.1 × 2.1 × 0.90 | Worldsemi package drawing; the STEP is an opaque maximum envelope, not optical or cosmetic CAD. The luminous aperture/transparency is not modeled. [Worldsemi datasheet](https://www.world-semi.com/downloads/datasheets/en/ws2812b-2020-v6-1.0.pdf) |
| U2 WSON-6 | 2.1 × 2.1 × 0.8 | Conservative package clearance envelope around TI's 2 × 2 mm DRV body and lead/thermal-pad footprint. [TI TPS61099 datasheet](https://www.ti.com/lit/ds/symlink/tps61099.pdf) |
| U3, U4 DBV SOT-23 | 3.1 × 3.1 × 1.45 | Conservative clearance cube including lead span and max body height; not a molded-body model. [TI SN74LVC1T45](https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf), [TI SN74LVC1G17](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf) |
| C2, C3 Murata GRM31 1206 | 3.4 × 1.8 × 1.8 | Conservative case maximum using the GRM31 family 1206 nominal body plus tolerance allowance. [Murata GRM31CZ71C226ME15L](https://www.murata.com/en-us/products/productdetail?partno=GRM31CZ71C226ME15L) |
| L1 TDK VLS3012CX | 3.2 × 3.2 × 1.3 | Conservative case maximum for the 3 × 3 × 1.2 mm part with tolerance allowance. [TDK VLS3012CX-2R2M-1](https://product.tdk.com/en/search/inductor/inductor/smd/info?part_no=VLS3012CX-2R2M-1) |
| J2 generic 1×4 header | 2.54 × 10.16 × 2.5 housing; 0.64 mm pins | Generic, unselected header envelope; 2.54 mm row pitch and 3.5 mm below / 6.0 mm above board-plane pin length are assembly assumptions. Confirm the chosen header before enclosure release. |

The KiCad STEP board includes these project-local models plus available stock KiCad 3D models, the complete routed board, and copper. It intentionally excludes U1's XIAO/Wio stack because the mechanical assembly inserts Seeed's combined vendor STEP model with vendor-stack translation Z=39.835 mm; the carrier FR4 datum is Z=21.535 mm. BT1/J3/J4 are off-board and absent. scripts/build_component_envelopes.py regenerates the local envelopes.
"""


def footprint_lib_table() -> str:
    libraries = sorted({part["footprint"].split(":", 1)[0] for part in PARTS if part["footprint"] and ":" in part["footprint"] and part["footprint"].split(":", 1)[0] != "SmartMark"} | {"MountingHole"})
    entries = [f'\t(lib (name "{name}") (type "KiCad") (uri "${{KICAD10_FOOTPRINT_DIR}}/{name}.pretty") (options "") (descr "KiCad stock footprints"))' for name in libraries]
    entries.append('\t(lib (name "SmartMark") (type "KiCad") (uri "${KIPRJMOD}/SmartMark.pretty") (options "") (descr "Revision-d carrier footprints"))')
    return "(fp_lib_table (version 7)\n" + "\n".join(entries) + "\n)\n"


def symbol_lib_table() -> str:
    libraries = sorted({part["libId"].split(":", 1)[0] for part in PARTS if part["libId"].split(":", 1)[0] != "SmartMark"} | {"copperhead_power"})
    entries = [f'\t(lib (name "{name}") (type "KiCad") (uri "${{KIPRJMOD}}/../sym-lib-cache/{name}.kicad_sym") (options "") (descr "Cached KiCad symbols"))' for name in libraries]
    entries.append('\t(lib (name "SmartMark") (type "KiCad") (uri "${KIPRJMOD}/SmartMark.kicad_sym") (options "") (descr "Revision-d symbols"))')
    return "(sym_lib_table (version 7)\n" + "\n".join(entries) + "\n)\n"


def generated_files() -> dict[str, str]:
    config = {"schematic": "hardware/SmartMark.kicad_sch", "board": "hardware/SmartMark.kicad_pcb", "docs": "docs/", "model": None}
    intent = {"version": 1, "parts": PARTS, "nets": NETS, "noConnect": NO_CONNECTS, "hints": {"groupOrder": ["Controller stack", "Battery harness", "HC-SR04 interface", "5V sensor supply", "Optional OLED", "Optional RGB", "Bring-up test points"], "paper": "A3", "date": "2026-10-26"}}
    return {
        "hardware/SmartMark.kicad_sym": custom_symbols(),
        "hardware/SmartMark.pretty/XIAO_S3_STACK_SOCKET_2x7.kicad_mod": stack_socket_footprint(),
        "hardware/SmartMark.pretty/VLS3012CX_2R2M.kicad_mod": tdk_inductor_footprint(),
        "hardware/SmartMark.pretty/WS2812B_2020_V6.kicad_mod": ws2812b_footprint(),
        "hardware/schematic.intent.json": json.dumps(intent, indent=2, ensure_ascii=False) + "\n",
        "hardware/sym-lib-table": symbol_lib_table(),
        "hardware/fp-lib-table": footprint_lib_table(),
        ".copperhead/config.json": json.dumps(config, indent=2) + "\n",
        "docs/BOM.md": bom_doc(), "docs/SUBSYSTEMS.md": subsystems_doc(),
        "docs/PINOUT.md": pinout_doc(), "docs/POWER_AND_IO.md": power_doc(),
        "docs/3D_MODELS.md": models_doc(),
    }


def check_invariants() -> None:
    refs = {part["ref"]: part["libId"] for part in PARTS}
    assert len(refs) == len(PARTS), "Duplicate reference"
    net_names: set[str] = set()
    used: set[str] = set()
    for net in NETS:
        assert net["name"] not in net_names, f"Duplicate net {net['name']}"
        net_names.add(net["name"])
        assert len(net["pins"]) >= 2
        for endpoint in net["pins"]:
            ref, number = endpoint.split(".", 1)
            assert ref in refs and number in SYMBOL_PINS[refs[ref]], f"Unknown endpoint {endpoint}"
            assert endpoint not in used, f"Pin appears in multiple nets: {endpoint}"
            used.add(endpoint)
    nc = set(NO_CONNECTS)
    assert len(nc) == len(NO_CONNECTS) and not (used & nc), "Duplicate or connected no-connect"
    covered = used | nc
    for endpoint in nc:
        ref, number = endpoint.split(".", 1)
        assert ref in refs and number in SYMBOL_PINS[refs[ref]], f"Unknown no-connect {endpoint}"
    for ref, lib in refs.items():
        for number in SYMBOL_PINS[lib]:
            assert f"{ref}.{number}" in covered, f"Unassigned pin {ref}.{number}"
    net_by_pin = {pin: net["name"] for net in NETS for pin in net["pins"]}
    expected = {"BT1.1": "BAT_POS", "BT1.2": "GND", "J3.1": "BAT_POS", "J3.2": "GND", "J4.1": "BAT_POS", "J4.2": "GND", "U1.1": "HC_TRIG", "U1.2": "ECHO_GPIO", "U1.4": "BOOST_EN", "U1.5": "I2C_SDA", "U1.6": "I2C_SCL", "U1.7": "LED_DATA_3V3", "U1.12": "3V3", "U1.13": "GND", "U2.2": "5V_SENSOR", "U2.4": "BOOST_EN", "U2.6": "3V3", "U4.2": "HC_ECHO", "U4.4": "ECHO_GPIO", "U3.3": "LED_DATA_3V3", "U3.4": "LED_DATA_5V", "U3.6": "5V_SENSOR", "D1.4": "5V_SENSOR", "D1.3": "LED_DIN"}
    assert all(net_by_pin.get(pin) == net for pin, net in expected.items()), "Critical rail and signal mapping changed"
    assert {"U1.14", "U1.3", "U1.8", "U1.9", "U1.10", "U1.11", "U4.1", "D1.1"} == nc
    assert custom_symbols().count("(") == custom_symbols().count(")"), "Custom symbol S-expression is unbalanced"
    assert '(pad "1" thru_hole roundrect (at 7.62 -7.62)' in stack_socket_footprint(), "XIAO D0 must be on carrier-right at the USB end"
    assert '(pad "14" thru_hole roundrect (at -7.62 -7.62)' in stack_socket_footprint(), "XIAO VBUS must be on carrier-left at the USB end"
    assert '(at -1.5 0) (size 1 1)' in tdk_inductor_footprint() and '(at 1.5 0) (size 1 1)' in tdk_inductor_footprint(), "TDK recommended inductor land pattern changed"
    assert '(pad "3" smd rect (at -0.915 -0.55)' in ws2812b_footprint() and '(pad "1" smd rect (at 0.915 0.55)' in ws2812b_footprint(), "Worldsemi top-view LED pad orientation changed"
    bom_refs = {line.split("|", 2)[1].strip() for line in bom_doc().splitlines() if line.startswith("| ") and not line.startswith("| Refdes") and not line.startswith("|---")}
    assert bom_refs == set(refs), "BOM and schematic intent references differ"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated files match checked-in files")
    args = parser.parse_args()
    check_invariants()
    failures = []
    files = generated_files()
    for relative, content in files.items():
        target = ROOT / relative
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                failures.append(relative)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
    if failures:
        print("Generated inputs differ or are missing:\n" + "\n".join(f"  {path}" for path in failures))
        return 1
    print(f"{'Checked' if args.check else 'Generated'} {len(files)} files; pin, net, S-expression, and BOM checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
