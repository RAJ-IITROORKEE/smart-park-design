# SmartPark Revision D

[Public GitHub repository](https://github.com/RAJ-IITROORKEE/smart-park-design)

Final retained design for an indoor ceiling mounted parking pilot using XIAO ESP32S3, Wio-SX1262, HC-SR04, protected 1S LiPo, programmable RGB indication and an optional 0.96 inch OLED. Updated 26 October 2026.

![Complete product and electronics previews](previews/05-images/final-preview.png)

[Watch the supplied SmartPark recording](media/videos/smartpark-revd-preview.mp4). The MP4 is retained unchanged under `media/videos`; its copy checksum is recorded in `verification/video-copy.json`.

The sensor faces downward from a ceiling up to 2.8 m above the floor. Firmware measures distance every 5 to 10 seconds, compares it with an empty bay baseline, and reports occupancy through a separate LoRa receiver or gateway. A gateway, dashboard and parking firmware are not included. HC-SR04 is an indoor nominal 4 m sensor; the case has no IP rating.

## Read and build

| Need | Open this |
|---|---|
| Illustrated complete guide | [Word guide](docs/SmartPark-RevD-Build-Guide.docx) or [matching Markdown](docs/SmartPark-RevD-Build-Guide.md) |
| Parts to buy and solder with product links | [Modules and components](docs/SmartPark-RevD-Build-Guide.md#purchased-modules-and-power-parts), [parts CSV](docs/parts-and-product-links.csv), [native electrical BOM](outputs/BOM.csv) |
| Program connections | [GPIO and harness tables](docs/SmartPark-RevD-Build-Guide.md#programming-pinout-and-peripheral-cables), [full pad map](docs/PINOUT.md) |
| Full schematic | [PNG](outputs/schematics.png), [PDF](outputs/schematics.pdf), [SVG](outputs/schematic-svg/SmartMark.svg) |
| Fabricate the PCB | [Gerbers and drills ZIP](outputs/SmartPark-RevD-PCB-Fabrication.zip), [fabrication specifications](docs/FABRICATION.md) |
| Edit PCB and schematic | [KiCad project](hardware/SmartMark.kicad_pro), [PCB](hardware/SmartMark.kicad_pcb), [schematic](hardware/SmartMark.kicad_sch) |
| Print the case | [Individual STL and 3MF ZIP](Case-Print-Files.zip), [part quantities](docs/SmartPark-RevD-Build-Guide.md#enclosure-print-parts-and-assembly) |
| All 3D previews | [Preview index](previews/README.md) with numbered folders, GLB, STEP and images |
| Battery and lifetime | [Battery fit and charging](docs/SmartPark-RevD-Build-Guide.md#battery-fit-charging-and-external-solar), [runtime assumptions](docs/SmartPark-RevD-Build-Guide.md#estimated-battery-runtime) |
| Assembly and print measurements | [Assembly](docs/BUILD_AND_RELEASE.md), [print checks](docs/PRINT_CHECK.md) |
| Checks and integrity | [Electrical audit](verification/release-electrical.json), [delivery check](verification/delivery-check.json), [SHA256 manifest](SHA256SUMS.txt) |

## PCB front and back

These are copper and silkscreen previews. The underside is mirrored for viewing from below. Upload fabrication files unchanged.

| Front | Back |
|---|---|
| ![Front copper](previews/01-pcb/pcb-front.png) | ![Back copper](previews/01-pcb/pcb-back.png) |
| [Front SVG](previews/01-pcb/pcb-front.svg) | [Back SVG](previews/01-pcb/pcb-back.svg) |

The carrier is 62 x 50 x 1.6 mm, two copper layers, 35 um nominal copper. The same Gerbers serve both variants. OLED population uses `BOM.csv` and `placements-smd.csv`; no OLED uses `BOM-no-OLED.csv` and `placements-smd-no-OLED.csv`, omitting J2, R8 and R9. D1 RGB and C7 are on the bottom. A bare fabricated PCB still needs the documented parts soldered onto it.

## Battery placement and capacity

![Battery position and connection destination](previews/05-images/battery-location.png)

The battery rests in the case base below the carrier, next to the ultrasonic sensor and toward the front panel. There is **no battery socket on the carrier**. A matching protected pack pigtail is soldered to XIAO BAT plus and BAT minus before mating Wio. Check actual pad labels, insulation, strain relief and connector polarity.

Use a protected **3.7 V single cell LiPo, target 1500 mAh**, about 5.55 Wh nominal. The whole pack must fit the **51 x 34 x 5 mm reference envelope**, plus 1 mm insulating foam below. Use a nonconductive strap without compressing the pouch. Confirm PCM, seals and lead exit dimensions. A [Probots protected pack candidate](https://probots.co.in/lithium-ion-rechargeable-battery-3-7v-1500mah-kp-053450.html) advertises about 50 x 34 x 5 mm but was out of stock and still needs supplier confirmation. An 18650 or larger pouch needs a new fit check or case revision.

For 1500 mAh with 80% usable capacity, brief sensing, deep sleep, radio asleep between occasional reports, and OLED off or omitted:

| Sample interval | Short 0.12 s wake | Longer 0.30 s wake |
|---|---:|---:|
| 5 seconds | about 32 days | about 12 days |
| 10 seconds | about 61 days | about 23 days |

These are model scenarios with assumed whole node battery currents, not measured results. See the guide and [calculation data](docs/battery-runtime-scenarios.json). Continuous RGB keeps the shared sensor supply on and can reduce life to about 20 to 40 hours. Continuous OLED, radio receive, WiFi, retries and extended awake time also reduce life.

Research basis: [Seeed XIAO power data](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/), [Wio module currents](https://files.seeedstudio.com/products/SenseCAP/Wio_SX1262/Wio-SX1262_Module_Datasheet.pdf) and the [HC-SR04 supplier manual](docs/sources/robu-HC-SR04-manual.pdf). The guide distinguishes manufacturer values from assumptions.

## External solar and programming

Use an **externally regulated 5 V USB solar output** to XIAO USB-C, for example [DFRobot FIT0601](https://www.dfrobot.com/product-1774.html). Use solar or service USB one at a time. The XIAO onboard charger is the only charger; the carrier has no raw panel input, MPPT or parallel cell charger. Seeed's general XIAO page lists 50 mA charging while its kit page lists 100 mA; verify the delivered board.

| Peripheral | Connection |
|---|---|
| HC-SR04 TRIG | J1 pin 2 to D0 / GPIO1 |
| HC-SR04 ECHO | J1 pin 3 through U4 buffer to D1 / GPIO2; never raw 5 V ECHO to MCU |
| HC-SR04 supply | J1 pin 1 switched 5V_SENSOR, pin 4 GND |
| Sensor and RGB supply enable | D3 / GPIO4, active high |
| OLED | J2 pins 1 GND, 2 3V3, 3 SCL / GPIO6, 4 SDA / GPIO5 |
| Onboard RGB data | D6 / GPIO43 through U3; one WS2812B-2020-V6 pixel |
| Firmware upload | XIAO USB-C data cable, XIAO ESP32S3 target; remove external solar |

Keep BOOST_EN low through startup, initialize TRIG and RGB data low, then enable the supply and wait at least 60 ms before sensing. RGB shares the HC-SR04 switched rail. Leave D2 / GPIO3 unused and reserve D8 to D10 for Wio. Stock kit firmware does not implement the parking application.

## Case parts and module stack

Closed body: **70 x 66 x 50.4 mm**, **94 mm wide with ears**. Four 4.5 mm mounting holes are spaced 82 x 42 mm. Only the two ultrasonic faces and status light pipe appear on the bottom; the sensor PCB is concealed. The OLED faces the aisle.

| Version | Installed printed parts |
|---|---|
| OLED, seven parts | base, lid, sensor_mask, sensor_retainer, light_pipe, front_oled, oled_retainer |
| No OLED, six parts | base, lid, sensor_mask, sensor_retainer, light_pipe, front_blank |
| Trial print only | fit_coupon, not installed |

![Case print parts](previews/05-images/parts-review.png)

Use PETG, print the coupon first and check clip clearances. Four releasable snap clips lock the lid; the front panel and retainers use screws. Individual print files are in `cad/STL` and `cad/3MF`. Product assemblies are previews, not whole product print files.

Use two 8.5 mm female sockets, 2.5 mm male shoulders and a **0.6 mm air gap above male plastic**, giving 11.6 mm carrier to XIAO PCB separation. Set the gap with a removable soldering shim. Male short legs must be at least 3 mm. XIAO components face the carrier; use its 14 edge pads, not Wio radio only outer rows.

## Release status

Retained RevD electrical and print geometry is unchanged. Native ERC, DRC, unrouted and schematic parity counts are zero; 42 critical package pin checks are retained. The mechanical report contains 116 checks with no failures and one unverified commodity sensor dimension assumption. Nine printable meshes and five complete product or electronics assemblies were checked. New enclosure only previews contain seven or six valid solids.

This is the **final retained pilot design**, not a physically qualified mass production release. Confirm actual battery, sensor, headers and OLED fit, electrical startup, measured current, runtime, latch life, mounting strength and India RF configuration before batch manufacture. Solder fillets, wiring and antenna cosmetics are incomplete. Historical check reports may mention the removed working folder; hashes identify the unchanged files retained here.

Older FireBeetle revisions, superseded archives and the redundant RevD working folder are removed during final cleanup. Tool runtimes stay separately in the parent `tools` folder. Sources, build steps and model provenance remain in this folder.
