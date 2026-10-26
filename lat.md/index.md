# SmartPark Revision D

Revision D is an indoor ceiling-mounted parking pilot built around a socketed XIAO ESP32-S3/Wio-SX1262 stack, HC-SR04, and an optional OLED.

## Mechanical design

The shared shell carries the board, battery, and sensor, with interchangeable blank and OLED front panels.

[[cad/src/design.py#base_shape]] builds the shell and module seats, [[cad/src/design.py#lid_shape]] builds the four releasable clips, and [[cad/src/design.py#product_shape]] places installed/exploded variants. Print orientation, assembly steps, and sample-fit limits are in [the print package](../docs/BUILD_AND_RELEASE.md#Print%20package) and [assembly guide](../docs/BUILD_AND_RELEASE.md#Assembly).

## Digital geometry checks

Digital checks cover model assumptions, export freshness, component interfaces, and print meshes.

[[cad/src/design.py#self_check]] checks model dimensions and estimates clip strain. [[cad/rebuild.py#main]] regenerates CAD exports; [[cad/checks/check_fit.py#main]] checks saved geometry and print meshes. These checks do not qualify physical fit, latch fatigue, installation strength, or deployed sensor performance.

The fit checker crosses every installed mechanical body with each electronics reference. [[cad/src/design.py#electronics_shape]] requires the native carrier STEP and imports the official Seeed stack with labeled header/reference envelopes. Saved exports are checked for SHA freshness, closed positive-volume solids, Z=0 print placement, and closed millimetre 3MF meshes.

The assembly seats the exported underside copper on the standoffs at Z=21.5 mm, placing the FR4 datum at Z=21.535 mm. The module/header stack follows this offset, avoiding a false 0.035 mm penetration from treating FR4 as the underside contact surface.

A 0.6 mm air gap above the male header shoulder clears USB mounting tabs in the vendor STEP. The carrier-to-XIAO PCB separation is 11.6 mm; a removable soldering shim sets this gap. The fit checker also crosses header housings with the vendor stack and checks the carrier against the sensor/display envelopes.

[[cad/checks/measure_prints.py#measure]] preserves measured wall, overhang and orientation reports for the base and lid. The remaining print-part reports and conservative PETG interpretation are recorded in docs/PRINT_CHECK.md. These measurements guide slicing and first-article review.

[[cad/checks/check_assemblies.py#main]] validates the saved native solids and glTF geometry for all five product/stack views, recording output and input SHA-256 hashes for delivery.

## Electrical and PCB sources

The carrier uses XIAO edge pads, a switched sensor supply, and buffered logic interfaces.

The inverted stack, battery pads, and interfaces are documented in `docs/PINOUT.md` and `docs/POWER_AND_IO.md`; procurement gates are in `docs/BOM.md` and `docs/hardware-review-procurement.md`. [[scripts/build_board.py#main]] regenerates the placement board and router DSN, or imports the saved routing session with `--finish`. Native KiCad verification and fabrication release must match the reviewed board revision.

[[scripts/export_release.py#main]] runs native ERC/DRC/parity, independently checks critical package pins, and exports Gerbers, separate plated/non-plated drills, BOM and placement tables. [[scripts/render_schematics.py#main]] rasterizes native KiCad SVGs for the wiring and assembly PNGs.

## Build and release

Reproduction commands and pilot qualification limits are documented in [build and release](../docs/BUILD_AND_RELEASE.md#Sources%20and%20reproducible%20builds) and [qualification boundary](../docs/BUILD_AND_RELEASE.md#Qualification%20boundary).

## Delivery and preview organization

The root README and illustrated Word and Markdown guide describe the retained RevD release and its numbered preview folders.

[[scripts/build_preview_models.py#main]] exports enclosure only views from final assemblies, preserving installed geometry and checking valid solids. The preview index separates carrier, connected electronics, enclosure and complete product models. Superseded designs are deleted only after retained artifact and archive verification.

The user supplied screen recording is stored unchanged in `media/videos/smartpark-revd-preview.mp4` and linked from the root README. `verification/video-copy.json` records the source filename, saved path, byte count and matching SHA256. Its content has not been reviewed for public sharing.

The public source repository is [RAJ-IITROORKEE/smart-park-design](https://github.com/RAJ-IITROORKEE/smart-park-design). Its repository root is this final design folder; installed runtimes in the parent tools folder and local caches are excluded.

## Battery runtime estimate

Battery lifetime is a scenario calculation using an assumed 1500 mAh pack, 80 percent usable capacity and explicitly stated battery side duty cycle currents.

[[scripts/build_delivery_guide.py#runtime_rows]] computes four polling and wake time scenarios with a small regression assertion. Actual firmware current, radio traffic, protected pack capacity and installation temperature must be measured. Continuous RGB keeps the sensor supply on and invalidates low power estimates.
