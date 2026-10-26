# XIAO and Wio carrier pin map

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
