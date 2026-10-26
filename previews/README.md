# SmartPark final 3D previews

Current RevD models are grouped by assembly level. GLB is convenient for orbiting; STEP preserves CAD solids and measurements. These are visualization models, not the files to fabricate a PCB or print an entire product.

## 01 PCB carrier

The carrier includes soldered component envelopes and excludes the plug in XIAO and Wio boards, battery, external sensor and case.

- [Carrier GLB](01-pcb/pcb-carrier.glb) and [STEP](01-pcb/pcb-carrier.step)
- [Front copper SVG](01-pcb/pcb-front.svg) and [back copper SVG](01-pcb/pcb-back.svg)
- [Front assembly SVG](01-pcb/assembly-front.svg) and [back assembly SVG](01-pcb/assembly-back.svg)
- [PCB image](05-images/pcb-only.png)

## 02 Connected electronics

This assembly shows the populated carrier, XIAO ESP32S3 and Wio-SX1262, sockets, ultrasonic module, battery and bulkhead reference without the case.

- [Electronics GLB](02-connected-electronics/electronics-stack.glb) and [STEP](02-connected-electronics/electronics-stack.step)
- [Electronics image](05-images/electronics_stack.png) and [battery location](05-images/battery-location.png)

## 03 Enclosure without electronics

Enclosure only assemblies preserve final installed positions. The parts subfolder holds separate preview meshes.

- [OLED case GLB](03-enclosure/case-oled.glb) and [STEP](03-enclosure/case-oled.step), seven parts
- [No OLED case GLB](03-enclosure/case-no-oled.glb) and [STEP](03-enclosure/case-no-oled.step), six parts
- [Individual preview parts](03-enclosure/parts)
- [Actual STL and 3MF print package](../Case-Print-Files.zip)

## 04 Complete product

Both complete products include the enclosure and component references. Exploded variants expose the interior and removable parts.

| View | GLB | STEP | Image |
|---|---|---|---|
| OLED closed | [GLB](04-complete-product/product_oled.glb) | [STEP](04-complete-product/product_oled.step) | [PNG](05-images/product_oled.png) |
| No OLED closed | [GLB](04-complete-product/product_status.glb) | [STEP](04-complete-product/product_status.step) | [PNG](05-images/product_status.png) |
| OLED exploded | [GLB](04-complete-product/exploded_oled.glb) | [STEP](04-complete-product/exploded_oled.step) | [PNG](05-images/exploded_oled.png) |
| No OLED exploded | [GLB](04-complete-product/exploded_status.glb) | [STEP](04-complete-product/exploded_status.step) | [PNG](05-images/exploded_status.png) |

## 05 Images

Rendered PNGs, a battery annotation and the part overview support the root README and illustrated guide.

![Final preview](05-images/final-preview.png)

Solder fillets, wires and some antenna and fastener details are absent. Physical assembly establishes real fit. `preview-copies.json` maps convenience copies to unchanged originals; the delivery verifier checks their equality.
