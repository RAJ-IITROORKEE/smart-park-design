# Revision D hardware review and procurement notes

Price and stock snapshot checked 2026-10-26 for the India pilot. Retail listings can change; “in stock” means the retailer page reported it at review time. This is a procurement estimate, not a compliance or production release.

## Recommended stack

| Function | Exact part | Review |
|---|---|---|
| Controller and radio | Seeed XIAO ESP32S3 + Wio-SX1262 kit, SKU 102010611 | Use the complete kit, including both antennas. The maker lists the SX1262 range as 862–930 MHz. The kit page lists 100 mA charging while the general XIAO page lists 50 mA; verify the delivered board. The XIAO 5 V pin is USB VBUS, not a 5 V battery rail, so the HC-SR04 needs its own switched boost. |
| Ultrasonic sensor | HC-SR04, Robu SKU 2444 | Listed 5 V, 15 mA working current and 45 × 20 × 15 mm module. The supplied Robu manual does not dimension the transducer centers or mounting holes; measure the delivered module before finalizing the mask. |
| 5 V sensor and pixel supply | Texas Instruments TPS61099DRVR | Adjustable boost in WSON-6, 2 × 2 mm. It supports true shutdown/load disconnect; use 1.6 µA as the conservative specified shutdown-current maximum (VIN = 3.7 V, VOUT = 0). Drive EN active-high from D3/GPIO4 and add a pull-down so reset/boot leaves the 5V_SENSOR rail off. The board reserves 75 mA for the HC-SR04 and pixel together. Rev D uses one 10 µF input capacitor and two Murata GRM31CZ71C226ME15L 22 µF, 16 V, X7R 1206 output capacitors in parallel. |
| Sensor echo buffer | Texas Instruments SN74LVC1G17DBVR | A 5.5 V-tolerant input buffer powered from 3V3; HC_ECHO is translated to 3.3 V logic before GPIO2/D1. Do not connect the HC-SR04 ECHO wire directly to an MCU pin or use the former 10 kΩ/20 kΩ divider instruction. |
| Pixel data translator | Texas Instruments SN74LVC1T45DBVR | Translates GPIO43/D6 data from 3V3 to the switched 5V_SENSOR pixel rail. The board includes 330 Ω series resistance on DIN and pulldowns on both translator sides. |
| Status pixel | Worldsemi WS2812B-2020-V6 | Single-wire addressable RGB pixel, 2 × 2 mm, compatible with the WS2812 protocol used by FastLED. It is powered from switched 5V_SENSOR; its DIN is driven through the SN74LVC1T45DBVR, not directly from the MCU. Reserve up to 60 mA for initial system review and limit firmware brightness. Do not substitute an unspecified older WS2812B. |
| Optional display | GoldenMorning GME12864-11, Robu SKU 617725 | 0.96-inch white SSD1306 I²C module. Power at 3V3; use a 1 × 4, 2.54 mm connection in supplier order GND, VDD, SCK/SCL, SDA. |
| Battery (not selected) | 51 × 34 × 5 mm 1500 mAh 1S LiPo is a fit target only | No battery pack is approved for purchase or assembly. The KP-503450 manufacturer SDS gives 3.7 V nominal, 4.2 V charge, 0.2C standard charge (300 mA) and 1C maximum charge, but PCM and connector are configurable. Require written vendor confirmation of an integrated protection circuit, matching JST-PH2 polarity, and total protected pack dimensions. Resolve the 50/100 mA charger documentation difference on the delivered board. |
| Optional solar input | DFRobot FIT0601 regulated 5 V solar panel | Use its regulated USB-A 5 V output to feed the XIAO USB-C input through an appropriate cable. It is a 6 W, 275 × 170 mm panel with integrated voltage regulation; it has no energy buffer. Do not connect the raw panel leads or its 7.2 V open-circuit input side to USB-C or directly to the cell. This arrangement retains the XIAO charger as the only charger. No MPPT behavior or all-weather charge budget is claimed. |

### Power and interface checks

- HC-SR04 ECHO goes through the board’s SN74LVC1G17DBVR, powered from 3V3, which accepts up to 5.5 V at its input and presents 3.3 V logic to GPIO2/D1. The old 10 kΩ/20 kΩ divider is not the Rev D circuit; do not wire ECHO directly to the MCU. Confirm the selected sensor’s high level and cable pin order during bench testing.
- A 3.3 V MCU TRIG output is a common interface, but the supplied HC-SR04 sheet does not give a guaranteed TRIG high threshold; verify trigger recognition on the selected module lot.
- The HC-SR04 manual quotes 15 mA operating current and a 10 µs trigger pulse. The TPS61099 has ample current margin for the board’s 75 mA initial sensor-plus-pixel budget, but its layout must follow TI guidance: keep the 2.2 µH inductor and input/output ceramic capacitors close to the IC. TI recommends 10 µF input capacitance and 20 µF nominal total output capacitance for the 1–2.2 µH range; account for ceramic DC-bias derating. Rev D selects two Murata GRM31CZ71C226ME15L 22 µF, 16 V, X7R 1206 capacitors in parallel on the boost output; the design notes estimate about 15.6 µF typical each at 5.016 V, leaving over 20 µF combined after conservative derating. A 5 V design uses a 1.0 V FB reference; TI shows 1 MΩ top and 249 kΩ bottom resistors as a 5 V example.
- The WS2812B-2020-V6 is powered from switched 5V_SENSOR. SN74LVC1T45DBVR translates GPIO43/D6 data to that rail; the 330 Ω DIN resistor and low-state pulldowns are part of the PCB design. Reserve 60 mA for the pixel during initial review and validate the XIAO/Wio 3V3 rail margin during radio transmit and sensor/pixel startup.
- Keep the boost disabled except during a sensor measurement. Allow supply startup before triggering and space trigger events by more than 60 ms. These are starting firmware gates; confirm startup, echo capture, EMI, and battery impact on the assembled board.
- The display module PCB is 27.8 ± 0.2 × 27.5 ± 0.5 × 1.2 mm, max module thickness 3.5 mm. The active area is 21.744 × 10.864 mm and viewing area is 23.744 × 12.864 mm. The supplied drawing implies the active-area center is offset about 2.1 mm toward the 4-pin-header edge along the short PCB axis. Treat this as a drawing-derived estimate and verify the real module before cutting the display opening. Allow about 7.5 mm for the soldered header pins and connector/cable below the OLED PCB.
- Keep the battery free of compression and metal edges, allow lead routing and strain relief, and verify the actual pack before closing the case. The cell maker specifies charging only from 0–45 °C; the XIAO temperature protection behavior and the installed enclosure temperature have not been established. Replace any swollen or damaged pouch cell.
- HC-SR04 sensing is not qualified by its nominal range/resolution alone. At the intended ceiling mount height, calibrate an empty-bay baseline and test different vehicle roofs, adjacent bays, timeout/no-echo cases, temperature, and sensor aim. The manual gives inconsistent angle descriptions (effective angle under 15° and measuring angle 30°), so do not use a nominal cone as proof of bay isolation.

## India RF configuration gate

The Seeed kit is capable of 862–930 MHz; that hardware capability is not permission to transmit throughout that span. DoT/WPC G.S.R. 853(E) defines India’s 865–868 MHz short-range-device licence exemption subject to the rule tables and conditions. DoT also describes Equipment Type Approval for devices operating in licence-exempt bands. Before deployment, select an India-specific profile, verify the exact allowed frequency/power/duty-cycle/antenna conditions against the current rules, and resolve finished-device ETA or other approval requirements. Keep transmit disabled by default until this review is complete. No certification or compliance status is asserted here.

## Indicative India price list

Prices are the retailer’s displayed amounts on 2026-10-26. Inclusive/exclusive tax basis is shown as listed; shipping, PCB fabrication, enclosure, assembly and cable/connector/passive costs are excluded.

| Qty | Item | Price basis | Listed price | Procurement note |
|---:|---|---|---:|---|
| 1 | XIAO ESP32S3 + Wio-SX1262 kit, 102010611 | Incl. GST | INR 1,625 | Robocraze page showed Add to Cart; stock quantity not shown. Seeed datasheet lists official price USD 10.90 ex VAT. |
| 1 | HC-SR04, SKU 2444 | Incl. GST | INR 79 | Robu listing showed Add to Cart; stock quantity not shown. |
| 1 | GoldenMorning OLED, SKU 617725 | Incl. GST | INR 219 | Robu listing showed in stock. |
| 1 | TPS61099DRVR | Incl. GST | INR 82 | Robu listing showed in stock, cut tape; MOQ 1, full reel 3,000. Supporting L/C/R and prototype assembly are not included. |
| 1 | WS2812B-2020-V6 | Tax basis not stated | INR 12.07 at 5-piece minimum | Microplacer/LCSC India listing showed stock and MOQ 5; quantity-one pricing is not available. Do not count this as a one-off gross/tax-inclusive quote. |
| 1 price-only lead | KP-503450, 1500 mAh | INR 335 ex IGST 18%; INR 395.30 if 18% applies | INR 395.30 calculated | Not approved for purchase or assembly: the BatteriesShop listing did not confirm PCM protection and its dimensions conflict. This price lead is excluded from any approved battery selection. |
| 1 | Protected KP-053450 price cross-check | Incl. GST | INR 435 | Probots listing explicitly describes battery protection and 50 × 34 × 5 mm size, but showed out of stock. Confirm current availability and exact pack details before ordering. |
| 1 optional | DFRobot FIT0601 solar panel | Incl. GST | INR 1,475 | Evelta showed 6 in stock; listing also itemizes INR 1,250 ex GST. Cable, mount and sunlight/seasonal energy sizing are excluded. |

Using the displayed INR prices, the core listed basket (kit + HC-SR04 + boost IC) is INR 1,786 before the OLED, pixel, SN74LVC1G17DBVR, SN74LVC1T45DBVR, other board passives, PCB fabrication, assembly and shipping. Adding OLED and the unapproved battery price lead gives approximately INR 2,400–2,440; that lead is not a purchase recommendation. Adding the FIT0601 panel gives approximately INR 3,875–3,915. These are planning totals, not a complete or procurement-cleared assembly cost. The pixel’s quoted price is excluded because its tax basis differs/was not stated and its listed minimum is five pieces.

## Sources

- Seeed kit datasheet: https://files.seeedstudio.com/Bazaar/product_pdf/102010611.pdf
- Seeed kit wiki and charging/interface details: https://wiki.seeedstudio.com/wio_sx1262_with_xiao_esp32s3_kit/
- XIAO ESP32S3 5 V pin/battery notes: https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
- Robocraze kit listing: https://robocraze.com/products/xiao-esp32s3-wio-sx1262-kit-for-meshtastic-lora
- Robu HC-SR04 price listing: https://robu.in/product-tag/hc-sr04/
- Robu HC-SR04 manual (local copy: docs/sources/robu-HC-SR04-manual.pdf): https://robu.in/wp-content/uploads/2020/02/edited_HC-SR04-User-Manual-1-converted-converted.pdf
- TI TPS61099 product page: https://www.ti.com/product/TPS61099
- TI TPS61099 datasheet, Rev. M: https://www.ti.com/lit/ds/symlink/tps61099.pdf
- TI SN74LVC1G17 datasheet: https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf
- TI SN74LVC1T45 datasheet: https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf
- Robu TPS61099DRVR listing: https://robu.in/product/tps61099drvr-texas-instruments-boost-type-adjustable-700mv5-5v-300ma-1-8v5-5v-wson-6-ep2x2-dc-dc-converters-rohs/
- Worldsemi WS2812B-2020-V6 product page: https://www.world-semi.com/products/ws2812b-2020-v6.html
- Worldsemi WS2812B family table: https://www.world-semi.com/ws2812-family/223.html
- Worldsemi V6 change notice: https://www.world-semi.com/web/index.php?classid=19&id=587&lanstr=en&topclassid=19
- India pixel listing, MOQ and price: https://lcscindia.com/part/WS2812B-2020-V6
- Robu GoldenMorning OLED listing: https://robu.in/product/0-96-inch-i2c-iic-oled-lcd-module-4pin-with-vcc-gnd-white/
- GoldenMorning GME12864-11 supplier drawing (local copy: docs/sources/goldenmorning-GME12864-11.pdf): https://robu-prod-media.s3.ap-south-1.amazonaws.com/products/attachments/D0c2gqmckZX1fpgA7JGeebYH7AGDDGJeD1SyuDaw.pdf
- KP-503450 SDS / cell maker specifications: https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/SDS-503450.pdf
- BatteriesShop KP-053450 price lead: https://www.batteriesshop.in/products/37v-1500mah-lithium-polymer-lipo-rechargeable-battery-model-kp-053450
- Probots protected-battery price cross-check: https://probots.co.in/lithium-ion-rechargeable-battery-3-7v-1500mah-kp-053450.html
- DFRobot FIT0601 product page: https://www.dfrobot.com/product-1774.html
- Evelta FIT0601 India listing: https://evelta.com/monocrystalline-solar-panel-5v-1a/
- DoT/WPC G.S.R. 853(E), 2021 short-range-device rules: https://www.dot.gov.in/static/uploads/2025/07/84f33f09e137fa81930f44bcd5f2d238.pdf
- DoT Equipment Type Approval information: https://www.eservices.dot.gov.in/equipment-type-approval-eta
