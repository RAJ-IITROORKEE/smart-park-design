# Rev D fabrication notes

These files describe a digitally checked indoor pilot. Build and qualify a first article before ordering a production batch.

Use outputs/SmartPark-RevD-PCB-Fabrication.zip for the PCB fabrication upload. It contains nine Gerber layers, separate PTH/NPTH Excellon drills, drill maps/report and the Gerber job file. The board is 62 × 50 mm, two copper layers, 1.6 mm FR4, with 35 µm nominal copper and solder mask on both sides. Confirm the surface finish and assembly process with the assembler for the 2 × 2 mm WSON package.

Configured minimum track width is 0.18 mm; the exported board's smallest track is 0.1874 mm. Nominal routing classes are 0.25 mm signal and 0.30 mm power, with router neck-downs. Minimum copper clearance is 0.20 mm, via diameter/drill is 0.60/0.30 mm, and mounting holes are 2.7 mm NPTH. Confirm the chosen fabricator supports these limits. Do not rescale or mirror individual Gerbers or drills.

outputs/BOM.csv and placements-smd.csv support assembly planning; confirm MPNs, generic passives and rotations with the assembler. D1 and C7 are on the bottom. Test pads are bare copper and excluded from the filtered SMD placement file. placements-all.csv retains native coordinates for reference. U1 is a socket interface: fit two 1×7 female sockets and hand-assemble the XIAO/Wio stack as described in BUILD_AND_RELEASE.md. The Seeed module is not an SMT placement at U1. The battery, its pigtail and XIAO BAT contacts remain off-board.

Both product variants use the same Gerbers. BOM.csv / placements-smd.csv describe the OLED population; BOM-no-OLED.csv / placements-smd-no-OLED.csv omit J2, R8 and R9 for the status-only version. Fit the blank front panel and omit the OLED module, cable and retainer for that version.

Native checks and 42 independent critical-pin checks are recorded in verification/release-electrical.json with SHA-256 hashes. The native report preserves KiCad's default ignored rule categories; zero reported violations is not a statement that every possible manufacturing check was enabled. Package/model envelopes and physical qualification limits are documented in 3D_MODELS.md and BUILD_AND_RELEASE.md.
