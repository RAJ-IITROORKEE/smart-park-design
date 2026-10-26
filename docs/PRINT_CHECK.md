# Revision D print check

This note summarizes mesh measurements for the PETG enclosure parts at a 0.4 mm nozzle assumption. It guides slicer review and first-article checks; it does not certify a printer/material combination or production readiness.

## Method and limits

The seven remaining STL files were measured with the installed `dfam-check` tool at a 45° overhang limit and `--samples 2000`. Existing `base` and `lid` reports are included for comparison. Reports are in `cad/checks/dfam-<part>.json`; orientation reports are in `cad/checks/dfam-<part>-orientations.json`.

A portable copy of the [FDM/FFF process limits](sources/dfam-process-limits.md) is included. The runtime reference was `C:\Users\rajra\.codex\plugins\cache\openai-curated-remote\text-to-cad\0.7.10\skills\dfam-check\references\process-limits.md`: supported wall ≥1.2 mm, unsupported wall ≥1.6 mm, self-supporting angle 45°, and unsupported bridge ≤10 mm. These are general defaults; the selected printer, PETG, slicer profile, and calibration can change the practical limits.

In the table, wall values are `wall_thickness.min_mm / wall_thickness.p05_mm`; support area is `overhangs.down_facing_area_below_limit_mm2 / overhangs.down_facing_area_below_limit_pct`; volume is `support_volume.support_to_part_ratio_pct`. `wall_thickness.samples_valid` shows how many rays contributed. The minimum is one sampled ray, not an exhaustive wall check; p05 is a stronger signal but still does not identify which samples are bed-supported. A flat, bed-supported mask/retainer flange may use the 1.2 mm supported-wall reference, but the tool does not classify support state per sample.

| STL report | Valid wall samples | `min_mm / p05_mm` (mm) | Down-facing area (mm² / %) | Support-volume upper bound (%) |
|---|---:|---:|---:|---:|
| [base](../cad/checks/dfam-base.json) | 2500 | 0.687 / 1.600 | 1251.28 / 3.5 | 62.2 |
| [lid](../cad/checks/dfam-lid.json) | 1836 | 1.467 / 1.600 | 39.20 / 0.3 | 6.2 |
| [sensor_mask](../cad/checks/dfam-sensor_mask.json) | 2000 | 0.835 / 1.200 | 0.00 / 0.0 | 0.0 |
| [sensor_retainer](../cad/checks/dfam-sensor_retainer.json) | 1364 | 0.452 / 1.600 | 0.00 / 0.0 | 0.0 |
| [front_oled](../cad/checks/dfam-front_oled.json) | 2000 | 1.351 / 1.833 | 0.00 / 0.0 | 0.0 |
| [front_blank](../cad/checks/dfam-front_blank.json) | 804 | 2.400 / 2.400 | 0.00 / 0.0 | 0.0 |
| [oled_retainer](../cad/checks/dfam-oled_retainer.json) | 1660 | 1.224 / 1.600 | 0.00 / 0.0 | 0.0 |
| [light_pipe](../cad/checks/dfam-light_pipe.json) | 1044 | 1.200 / 1.200 | 8.83 / 3.9 | 14.0 |
| [fit_coupon](../cad/checks/dfam-fit_coupon.json) | 888 | 2.400 / 2.400 | 19.68 / 0.5 | 4.0 |

## Print orientation and first-article review

Six-axis orientation reports find the current `+Z` print orientation lowest in support area for the base (1251.28 mm², 3.5%) and lid (39.20 mm², 0.3%). The fit coupon also favors its current `+Z` orientation (19.68 mm²); the light pipe is nearly tied upright versus flipped (8.83 versus 8.84 mm²) and needs much more support laid sideways (46.9 mm²). Keep the coupon flat and the light pipe upright.

Treat isolated low `min_mm` samples as `❓ need more info` until reviewed in the slicer and on a first print: the base sample is at a tapered mounting-ear corner, the lid sample is at a tooth ramp, the mask and sensor-retainer minima are at thin flange edges, and the OLED front/retainer each have a sampled thin edge. Their p05 values meet or equal the relevant 1.2 mm supported or 1.6 mm unsupported reference, but the sampling does not prove every local feature. Check clips, mounting ears, screw pilots, and mask fit on the printed part.

The base's 62.2% `support_to_part_ratio_pct` is a coarse prism upper bound, not a predicted slicer support volume or a failure. Review the slicer preview and add local supports only where needed, including the front-window and USB opening roofs: these spans exceed the 10 mm bridge default, which the DfAM tool does not measure. Hole diameter, positive-feature size, and bridge length also have no measured counterpart in the tool; verify those directly in the slicer and with the fit coupon.

Use the measured reports as geometry evidence only. Physical material behavior, first-layer adhesion, shrinkage, latch force/cycle life, and as-printed clearances still require a prototype. Do not use this document as a production-readiness claim.

