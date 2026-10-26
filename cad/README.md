# SmartPark HC-SR04 / XIAO S3 Rev D — mechanical pilot

This is the parametric snap-fit enclosure for the selected indoor ceiling-mounted pilot. Units are millimetres; +Z points toward the ceiling, sensor faces point down, and the OLED faces the aisle at -Y.

## What to print

Print one base, one lid, one sensor_mask, one sensor_retainer, one light_pipe and either front_blank or front_oled. The OLED version also uses oled_retainer. These variants share the same body and mounting pattern.

STL/ and 3MF/ contain individual parts normalized onto Z=0. The lid is already inverted with its outside face on the bed. STEP/ stores the corresponding print-oriented individual solids; product/exploded STEP files store installed positions. Do not print electronics_stack or product/exploded assemblies.

Use PETG for the indoor pilot, clear PETG or a commercial3mm light rod for the light pipe. Starting slicer settings:0.2mm layer,0.4mm nozzle,4perimeters,5top/bottom layers,30% infill. Review the mounting-ear ramps and local supports in the slicer. Do not use supports inside the latch gap if they would fuse the cantilever. Actual printer shrinkage and PETG flexibility require a first article.

The lid uses1.6mm clip beams and locating lip. Root-to-hook load length is18.8mm, with22mm full tabs and a conservative1.4mm deflection estimate below1% strain. This is an elastic beam estimate, not a fatigue/retention test. Fit0.2–0.3mm soft insulating shims at theOLED rear corner clamp if needed to remove play; never press directly on the glass.

The base, lid and OLED front panel use native OCCT tessellation for manufacturing STL and 3MF at 0.02 mm/0.1 rad, with hashes recorded in checks/manufacturing-manifest.json. This preserves closed seams at the latch windows and panel bosses. The independent edge audit checks the actual manufacturing files. Preview GLBs are visualization files. Run rebuild.py to reproduce both export paths.

The shell is70x66x48mm, closed height50.4mm; mounting ears extend its width to94mm. Four ear bores are4.5mm diameter with82x42mm center spacing. Choose anchors and a secondary retention arrangement for the actual ceiling construction; no printed-anchor load rating is claimed.

## Parts and interfaces

The carrier is 62 × 50 × 1.6 mm, with four M2.5-class mounting positions at X±28.5, Y±22. Its bottom copper seats at Z=21.5 mm; the FR4 datum is Z=21.535 mm because the KiCad export includes 0.035 mm copper below FR4. The kit and socket references move with this correction. Screws use printed pilot bores; verify the actual hardware. Depress the four side clips inward with a thin nonmetal tool while lifting the lid; remove the node from the ceiling before opening.

TwoM2x4 screws retain theHC-SR04 edge clamp from above; twoM2x4 screws retain the replaceable acoustic mask from below. The module is clamped by PCB edges, without assuming a commodity mounting-hole pattern. Nominal module45x20x15, cansØ16 at26mm pitch. Only the two transducer faces appear through the bottom mask. This pitch, can size and right-angle cable/header envelope require the purchased sample check.

The removable front panel uses twoM2x6 screws. OptionalOLED retainer uses fourM2x5 screws into printed pilots; choose screw lengths from the actual fitted stack so they cannot bottom against the front face. OLED drawing envelope27.8x27.5x1.2mm, maximum module3.5mm plus header/cable clearance; header edge up. The viewing window24.4x13.5mm is offset toward that edge to expose the specified active/viewing area. Confirm the supplied panel matchesGME12864-11 before printing a batch.

The front panel is 56 × 40 mm. Its active-area center is Z=27.6 mm; the OLED retainer starts at Z=9.2 mm, leaving 0.8 mm nominal clearance above the modeled battery. These positions are checked against the supplier drawing and the installed reference envelopes.

The protectedLiPo reference is51x34x5mm with1mm foam under it. Retain with an insulating hook-and-loop strap, without compressing the pouch. Nominal lateral clearance to nearby bosses can be as little as0.5mm; supplier confirmation and sample fit are required. The model has generous free height above the cell, but it does not certify a damaged/swollen cell as usable. Replace damaged cells.

## Electrical stack and solar

The XIAO component face points toward the carrier and Wio is above it. Use the XIAO's14 edge pads for the carrier, not the Wio's radio-only outer rows. Use 8.5 mm female headers plus a 2.5 mm male shoulder, with a 0.6 mm air gap between the male plastic and XIAO PCB. A removable soldering shim sets this gap; remove it afterward. Male short legs must be at least 3 mm to leave about 0.8 mm protrusion through the 1.6 mm PCB. Total carrier-top to XIAO facing-PCB separation is 11.6 mm. The air gap clears USB mounting tabs in the vendor model. Pre-solder the two-wire battery pigtail before mating Wio; provide strain relief and keep solder/wires out of theB2B connector.

The XIAOUSB-C port is used for serviceUSB or a regulated5V external solarUSB supply, one source at a time. A raw panel cannot be connected toBAT,3V3 orUSB. The node contains noMPPT controller; panel regulation/storage is external. A slimUSB-C plug must fit the14x7.6mm opening and reach the recessed connector. The pigtail bulkhead hole is6.6mm for a nominal quarter-inchSMA connector; verify actual connector shoulder and nut before purchase.

The bottomRGB pixel faces a removable straight3mm clear light pipe. Fit a suitable865MHz antenna through theSMA/U.FL pigtail before radio transmission; the preview shows the bulkhead envelope, not a tuned antenna or qualified coax bend.

## Model provenance and limits

OfficialSeeedXIAO andWioSTEP geometry is preserved in imported/xiao-s3-wio-sx1262-stack.step. Its alignment follows the documented connector plane and module outline. Carrier/socket geometry and the selected female/male header separation still need a fitted sample. HC-SR04,LiPo,OLED andSMA bodies in product previews are labeled reference envelopes, not vendor metrology.

step.parts was queried before substitutes were made. NoHC-SR04/XIAO match was returned. ItsSSD1306 match was anAdafruit variant and itsLiPo matches were100/150mAh, not the selected products; they were not substituted. Query evidence is imported/step-parts-search.json.

checks/check_fit.py and the saved report check digital topology, interference, clearances and mesh exports. Snap strain is a simple cantilever estimate, notFEA or a fatigue test. Physical module fit, latch force/cycle life, mounting load, ingress,RF performance and battery runtime are not qualified. This open-apertureHC-SR04 enclosure is an indoor pilot, with noIP rating.

