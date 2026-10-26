# SmartPark Rev D — build and release

Revision D is an indoor ceiling-mounted parking pilot with an HC-SR04 sensor, a socketed XIAO ESP32-S3/Wio-SX1262 stack, and an optional OLED. The enclosure has print-oriented STL and 3MF assets; the PCB is maintained as a native KiCad project. Treat this as a digitally prepared pilot, not a physically qualified production release.

## Print package

Print `base`, `lid`, `sensor_mask`, `sensor_retainer`, `light_pipe`, and one front panel: `front_blank` for no display or `front_oled` with `oled_retainer` for the optional display. `fit_coupon` is a useful first print. STL and 3MF parts are normalized to Z=0; the lid is already inverted with its outside face on the bed. Do not print the electronics stack or product/exploded assemblies.

Use PETG for the indoor pilot. Start at 0.2 mm layers, 0.4 mm nozzle, 4 perimeters, 5 top/bottom layers, and 30% infill. Use clear PETG or a straight 3 mm light rod for the light pipe. Add local supports under front-opening roofs and mounting-ear ramps where the slicer needs them; keep the four 1.6 mm lid clips and their gaps clear of fused support. Check the actual slicer preview and print a fit coupon before the enclosure set. See [PRINT_CHECK.md](PRINT_CHECK.md) for mesh measurements and limitations.

The closed shell is 70 × 66 × 50.4 mm; the mounting ears extend the overall width to 94 mm. Their four Ø4.5 mm holes have 82 × 42 mm center spacing. The carrier outline is 62 × 50 mm. These are model dimensions, not printer-calibrated tolerances. Choose anchors for the ceiling material and add a secondary retention method; no printed-anchor load rating is claimed.

## Assembly

1. Inspect the purchased HC-SR04 before fitting it. The mask assumes two nominal Ø16 mm cans at 26 mm pitch, but commodity modules vary. Secure the module edge clamp from above with two M2×4 screws and the replaceable mask from below with two M2×4 screws. Confirm both sensor faces remain unobstructed.
2. Fit the protected 1S LiPo reference pack (51 × 34 × 5 mm) over 1 mm insulating foam. Use an insulating strap without compressing the pouch. Confirm the exact pack protection, polarity, connector, and dimensions before purchase. Replace a damaged or swollen pack.
3. Solder the battery pigtail to the XIAO BAT pads before mating the Wio module. Use 8.5 mm female sockets and 2.5 mm male shoulders. Leave a 0.6 mm air gap above the male plastic using a removable soldering shim, then remove the shim; this clears USB mounting tabs in the vendor model and sets 11.6 mm carrier-to-XIAO separation. Use male short legs at least 3 mm long, leaving about 0.8 mm through the XIAO PCB. The XIAO component face points down toward the carrier. Connect through the XIAO's 14 edge pads; do not use the Wio radio-only outer rows. Keep the pigtail and solder away from the board-to-board connector. Mount the 62 × 50 mm carrier on its four M2.5-class pilot positions and verify the selected screws do not damage the printed bosses.
4. For the OLED option, use the GoldenMorning GME12864-11 (Robu SKU 617725) only after checking the delivered module against its 27.8 × 27.5 mm supplier drawing. Fit its header edge up, route a flexible cable, secure the front panel with two M2×6 screws, then retain the display with four M2×5 screws selected to avoid bottoming. The modeled front panel is 56 × 40 mm (Z=5–45 mm); the OLED board is at Z=11.75–39.25 mm with active-area center at Z=27.6 mm. Retainer bottom Z=9.2 mm leaves 0.8 mm nominal clearance above the battery top at Z=8.4 mm. These are placement dimensions; sample fit is not qualified. The blank option uses `front_blank` and omits the display and retainer.
5. Fit the 3 mm light pipe and the selected SMA/U.FL antenna pigtail only after checking the actual connector shoulder, nut, cable bend, and antenna. Close the lid until all four clips engage. To reopen, remove the node from the ceiling, press the side clips inward with a thin nonmetal tool, and lift the lid. Do not pry against the battery or OLED glass.

## Power and operating limits

Use one regulated 5 V source at the XIAO USB-C port: service USB or a regulated 5 V solar USB feed. Never connect a raw panel to USB-C, BAT, or 3V3; the panel regulator and any energy storage are external. The XIAO's onboard charger is the only cell charger; do not parallel another charger. Seeed lists 50 mA on the general XIAO page and 100 mA on the kit page, so verify the delivered board. See [POWER_AND_IO.md](POWER_AND_IO.md), [PINOUT.md](PINOUT.md) and the illustrated guide for bench checks and battery estimates.

The HC-SR04 is an indoor sensor with a nominal maximum range of 4 m. Do not claim 5 m or assume that the nominal maximum is usable in a ceiling installation; validate detection with the actual mounting height, target, angle, and room. Test the exact sensor's trigger threshold, echo level, cable order, and current. Never connect a 5 V echo directly to an ESP32-S3 GPIO; the carrier's buffer is part of the design.

## Sources and reproducible builds

The electrical source of truth is `hardware/SmartMark.kicad_sch`, `hardware/SmartMark.kicad_pcb`, and the project/library inputs alongside them. Component sourcing and unresolved purchase gates are in [BOM.md](BOM.md) and [hardware-review-procurement.md](hardware-review-procurement.md). Parametric enclosure sources are in `cad/src/`; vendor STEP and drawing evidence are retained under `cad/imported/` and `docs/sources/`. STL/3MF outputs are in `cad/STL/` and `cad/3MF/`; `cad/checks/manufacturing-manifest.json` records source/export hashes for base, lid, and front_oled. The front_oled STL/3MF now use native OCCT tessellation; this resolves mesh seams without changing the CAD geometry.

Run these from this final design root with the matching KiCad Python and build123d environments available:

```powershell
python scripts/build_board.py
python scripts/build_board.py --finish
python cad/rebuild.py
python cad/checks/check_fit.py
python cad/checks/check_assemblies.py
python scripts/export_release.py
python scripts/render_schematics.py
```

`scripts/add_local_decoupling.py` adds the C6/C7 schematic symbols and power connections after editing the electrical intent; it is idempotent. `scripts/build_component_envelopes.py` creates local STEP clearance envelopes when a stock KiCad model is unavailable. `build_board.py` rebuilds the placement board and router DSN; `--finish` imports the saved Freerouting session and fills ground planes. The project minimum track width is 0.18 mm (about 7 mil), while routed signal classes target 0.25 mm and power classes target 0.30 mm; the shortest low-current signal neckdowns in this revision are 0.1874 mm. Confirm the selected fabrication service supports the 0.18 mm minimum before ordering. `cad/rebuild.py` regenerates the CAD exports, and `check_fit.py` reports digital geometry and mesh checks. Re-run the checks against the exact board and enclosure files you intend to release. Generate PCB fabrication plots from the reviewed native board only after the final KiCad ERC, DRC, schematic/netlist/board parity, and routing evidence is recorded in `verification/`; release those plots with the matching board revision and review reports.

Use KiCad's Python for the PCB scripts and the cadgen/build123d environment for CAD and image scripts. On Windows, set `$env:CADGEN_DAEMON='0'` before a large CAD rebuild if the warm geometry worker fails. The export script audits the actual critical package pins and creates both OLED/no-OLED population tables. See [fabrication notes](FABRICATION.md) for upload files and assembly boundaries.

## Qualification boundary

Digital geometry and mesh checks do not establish physical fit, latch force or cycle life, ceiling-anchor strength, ingress protection, RF performance, battery runtime, or electrical startup/transient margin. The four clips have 1.6 mm beams; their beam estimate is not a fatigue or retention test. The HC-SR04 transducer pitch, LiPo clearance, connector envelopes, and optional OLED fit all depend on the actual purchased samples. Print and fit a first article, then bench-check the assembled electronics and intended installation before deploying or ordering a batch. This open-aperture HC-SR04 case is indoor-only and has no IP rating. RF use in India also requires the regional frequency, power, duty-cycle, antenna, and equipment-approval review described in the procurement notes.



