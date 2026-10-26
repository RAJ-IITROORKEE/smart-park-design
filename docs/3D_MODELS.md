# STEP component models

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
