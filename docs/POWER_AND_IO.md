# Electrical power and interface notes

This page records power boundaries and bench-test gates for the revision-d carrier.

Use only an externally regulated 5 V source through the XIAO USB-C connector. Solar panels must be regulated to 5 V upstream; no raw panel connection is on this PCB. Use service USB or the regulated solar feed, never both through a Y cable. The XIAO onboard charger is the only cell charger. A protected LiPo pigtail is soldered to the XIAO BAT pads before the stack is assembled; verify protection, chemistry, polarity, and connector on the actual pack.

U2 is TI TPS61099DRVR, adjustable boost from XIAO 3V3 to 5V_SENSOR. R1/R2=1M/249k set about 5.016 V using the 1.0 V feedback reference. Follow the TI reference circuit: 2.2 µH inductor, 10 µF input capacitor, and two 22 µF output capacitors; Murata GRM31CZ71C226ME15L provides about 15.6 µF typical per part at 5.016 V, leaving over 20 µF combined under the documented conservative derating. GPIO4/D3 drives EN; 100 kΩ pulls it low through reset. The TPS61099 provides true load disconnect in shutdown. In the project symbol, SW is typed passive because it is a switching node feeding L1, not a DC power rail; this avoids a false ERC driver requirement without adding a PWR_FLAG to that node.

5V_SENSOR powers HC-SR04 and the optional WS2812B-2020-V6. Reserve 75 mA for initial review (15 mA sensor plus conservative 60 mA pixel budget); firmware must limit pixel brightness. Verify XIAO/Wio 3V3 rail margin during radio transmit and sensor/pixel startup.

J1 pin order is 1=5V_SENSOR, 2=TRIG, 3=ECHO, 4=GND. GPIO1/D0 drives TRIG directly at 3.3 V; confirm the purchased HC-SR04 accepts that level. HC_ECHO feeds TI SN74LVC1G17 at U4, powered at 3V3; the device input accepts up to 5.5 V and output is 3.3 V logic. R4 pulls the cable input low when unplugged. Verify the exact module’s echo high level, ringing, cable pin order, trigger VIH, and current before release.

U3 SN74LVC1T45 translates GPIO43/D6 data from 3V3 to switched 5V_SENSOR. C5 decouples VCCB at U3, C6 decouples VCCA there, and C7 bypasses 5V_SENSOR beside the bottom-side pixel; C4 remains the local U4 bypass. DIR is high for A-to-B; 100 kΩ pulldowns hold both data nodes low and 330 Ω is in series with pixel DIN. Its Ioff behavior is intended to avoid back-driving the unpowered 5 V side. J2 is optional 2.54 mm OLED: 1 GND, 2 3V3, 3 SCL, 4 SDA; board pullups are 4.7 kΩ, so check module onboard pullups before fitting.

At reset, keep BOOST_EN low and initialize GPIO43/D6 low before turning on 5V_SENSOR. GPIO43 is UART0 TX during boot; GPIO3/D2 is an ESP32-S3 strapping pin and remains unused. Wait at least 60 ms after enabling the sensor/pixel supply before the first HC-SR04 measurement cycle.

This is not production-qualified without testing the selected HC-SR04, protected battery, solar regulator, XIAO/Wio stack, OLED, pixel, board assembly, radio-transmit brownout margin, and case fit. Primary sources: [TPS61099 datasheet](https://www.ti.com/lit/ds/symlink/tps61099.pdf), [SN74LVC1G17 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf), [SN74LVC1T45 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf), [Seeed XIAO pinout/power](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/), [Worldsemi WS2812B-2020-V6](https://www.world-semi.com/ws2812-family/223.html).
