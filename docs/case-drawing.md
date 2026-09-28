# Case: manufacturing notes

This is modelled on the original's drawing **bayleaf-case-MK5_L**. There are two parts per half, both CNC-machined 6061-T6, bead-blasted and anodised. The STEP files are in `hardware/case/out/`, and the right half is the mirror image.

| Part | File | Size | Weight (6061) |
|---|---|---|---|
| Top shell | `bayleaf-shell-{left,right}.step` | 139.4 × 96.8 × 6.2 mm | ≈ 19 g |
| Bottom plate | `bayleaf-plate-{left,right}.step` | 137.3 × 94.7 × 0.8 mm | ≈ 28 g |

## Top shell

Values marked **[D]** are dimensions from the MK5 drawing. Everything else is my reading of that drawing, or was changed to fit this PCB.

* **Top outline:** 137 mm wide **[D]**. The walls are drafted, so the base is 1.19 mm larger per side **[D]** (about 99° walls plus the top chamfer). I modelled this as one straight draft.
* **Depth:** assumed to be 86 + 2 × 4.2 = 94.4 mm at the top. The drawing gives the 4.2 mm border **[D]** only on the left side.
* **Key window:** 103 × 86 mm **[D]**, 4.2 mm from the left edge **[D]**.
* **Divider:** 2 mm wall **[D]**. Next to it is the 27 mm controller bay **[D]**, closed by a 0.8 mm roof **[D]**.
* **Height profile:** 6.2 mm at the back and over the controller bay **[D]**. Along the front edge of the key area it curves down to 3.8 mm **[D]**, over roughly the first 24 mm (read off the side view). Toward the controller bay the curve fades out between x ≈ 72 and 101 mm (read off section A).
* **Bottom plate seat:** a rabbet 1.0 mm wide × 0.8 mm deep, leaving a 1 mm wall at the base **[D]**.
* **Divider rib:** stops 1.2 mm above the PCB, so the SMD parts pass underneath.
* **USB-C:** a 10 × 3.5 mm slot in the front wall, centred on the bay.
* **Power switch:** a 4.4 mm slot in the inner side wall, open to the bottom.
* **Reset:** a Ø1.6 mm pin-hole through the roof, above the reset button. Press it with a paper clip.

### Tapped holes: all in bosses on the underside, drilled up from the PCB plane

| Qty | Position (x, y from the back-left corner of the top outline) | Boss | Thread | Note |
|---|---|---|---|---|
| 2 | (2.9, 3.5), (2.9, 90.9) | Ø6 | M2×0.4 6H × 2, Ø2.4 × 90° countersink | key-frame corners **[D]** |
| 2 | (113.68, 3.5), (131.72, 3.5), 18.037 ±0.1 apart | Ø6 | M2×0.4 6H × 2, Ø2.4 × 90° | back of the controller bay **[D]** |
| 1 | (109.5, 47.2) | Ø6 | M2×0.4 6H × 3, Ø2.4 × 90° | middle of the divider **[D]** |
| 2 | (111.45, 90.9), (133.95, 90.9) | Ø4 | M2×0.4 6H × 3, Ø2.4 × 90° | front of the bay, flanking the USB-C port. **Moved:** the drawing has them 19.039 mm apart (Ø5), which would put them on the nice!nano's pin rows. Here they sit in the bay corners, 22.5 mm apart. |

The STEP files model the tapped holes at the Ø1.6 mm tap-drill size. Tell the shop the threads are **M2×0.4, blind, 2 and 3 mm deep** as in this table.

## Bottom plate

* 0.8 mm thick. It drops into the shell's rabbet and sits flush with the base.
* Seven Ø2.2 mm holes, counterbored Ø4.2 × 0.5 mm from below for thin-head M2 screws.
* A 0.4 mm deep pocket on the top face under the USB-C receptacle.

## Fasteners

The screws go up through the bottom plate and the PCB into the bosses, so each boss clamps the PCB.

| Qty per half | Screw | Where |
|---|---|---|
| 4 | M2 × 3, thin/wafer head (Ø4 × ≤0.5 mm head, "laptop screw") | 2 mm-deep holes |
| 3 | M2 × 4, thin/wafer head | 3 mm-deep holes |

Put a piece of 0.05 mm Kapton film between the bottom plate and the PCB, so the bottom-layer traces never rest directly on aluminium.
