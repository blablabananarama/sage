# Case: manufacturing notes

The case comes from two sources:
- **Plan view:** the original's drawing **bayleaf-case-MK5_L**. Values from it are marked **[D]**.
- **Heights and look:** the build photos. "Tallest part of the keyboard is only 5 mm": a silver frame, the keycaps standing slightly proud of it, and a separate lid over the controller that's anodised in a contrasting colour. Values from the photos are marked **[P]**.

There are three CNC parts per half, all 6061-T6, bead-blasted and anodised. The STEP files are in `hardware/case/out/`, and the right half is the mirror image.

| Part | File | Size | Weight (6061) | Finish on the original |
|---|---|---|---|---|
| Top shell | `bayleaf-shell-{left,right}.step` | 139.4 × 96.8 × 4.1 mm | ≈ 9 g | silver |
| Lid | `bayleaf-lid-{left,right}.step` | 29.8 × 94.4 × 0.8 mm | ≈ 6 g | blue (contrast) |
| Bottom plate | `bayleaf-plate-{left,right}.step` | 137.3 × 94.7 × 0.8 mm | ≈ 28 g | silver |

A finished half weighs about 93 g with the electronics, so about 186 g for the pair. The original is 180 g.

## Heights

```
5.0 mm  top of the lid: the tallest point [P]
4.2 mm  underside of the lid (0.1 mm tape on the shell's wall tops)
4.1 mm  shell walls around the controller bay
~4.4 mm keycap tops (PG1316S + stock cap on a 0.8 mm PCB)
4.1 mm  frame at the back of the key area
3.1 mm  frame at the front edge of the key area (the drawing's 3.8 / 6.2 proportion, scaled to the 5 mm total)
~4.0 mm top of the nice!nano (only ~2.4 mm of its 3.2 mm sits above the PCB; the USB-C shell hangs into a PCB notch)
1.6 mm  PCB top
0.8 mm  bottom plate top
```

## Top shell

* **Top outline:** 137 mm wide **[D]**. The walls are drafted, so the base is 1.19 mm larger per side **[D]**. The depth is assumed to be 86 + 2 × 4.2 = 94.4 mm.
* **Key window:** 103 × 86 mm **[D]**, 4.2 mm from the edge **[D]**.
* **Two soft bends [D]/[P]:**
  * Front to back: the frame is 4.1 mm tall at the back and curves down to 3.1 mm along the front edge, over the front 24 mm (the drawing's side views).
  * Toward the controller: between x ≈ 72 and 101 mm that front dip fades out in a second S-curve (section A), so the front face rises to meet the lid, as in the photos.
  * Both curves are smoothstep blends. The outer top edge has a 0.5 mm round (the drawing shows a 0.61 mm chamfer).
* **Frame skin:** 0.8 mm.
* **Divider:** 2 mm **[D]**. It stops 1.2 mm above the PCB so the SMD parts pass underneath.
* **Controller bay:** 27 mm **[D]**, open on top and closed by the lid.
* **Bottom plate seat:** a rabbet 1.0 mm wide × 0.8 mm deep, leaving a 1 mm wall at the base **[D]**.
* **USB-C:** an open-top 10 mm slot in the front wall of the bay (the lid closes it).
* **Power switch:** a 4.4 mm slot in the inner side wall.

### Posts: M2×0.4 6H, blind from below, Ø2.4 × 90° countersink [D]

| Qty | Position (x, y from the back-left corner of the top outline) | Post | Thread | Note |
|---|---|---|---|---|
| 1 | (2.9, 3.5) | Ø6 | 2 mm | back key-frame corner **[D]** |
| 1 | (2.9, 90.9) | Ø6 | **1.1 mm** | front key-frame corner **[D]**, under the 3.1 mm front edge |
| 2 | (113.68, 3.5), (131.72, 3.5), 18.037 ±0.1 apart | Ø6 | 2 mm | back of the bay **[D]** |
| 1 | (109.5, 47.2) | Ø6 | 2 mm | middle of the divider **[D]** |
| 2 | (111.45, 90.9), (133.95, 90.9) | Ø4 | 2 mm | front of the bay, flanking the USB-C. **Moved:** the drawing's pair is 19.039 mm apart, which would sit on the nice!nano's pins. |

The posts come down onto the PCB, and the bay posts also carry the lid. The drawing's 3 mm-deep threads don't fit under a 5 mm-tall keyboard. `case.py` sizes each thread to leave 0.5 mm of material above it. The STEP models them at the Ø1.6 mm tap-drill size; give the shop the thread callout.

## Lid

* 0.8 mm plate covering x = 107.2 … 137 mm, flush with the shell's outer edges. It has a 0.3 mm chamfer on top and a Ø1.6 mm pin-hole above the reset button.
* It's held by 0.1 mm double-sided tape (e.g. 3M 467MP / Nitto 5000NS) on the wall tops, the divider and the four bay posts, so it can be peeled off for service.
* Anodise it in a contrasting colour to get the original's look, or match the shell.

## Bottom plate

* 0.8 mm thick. It drops into the shell's rabbet and sits flush with the base.
* Seven Ø2.2 mm holes, counterbored Ø4.2 × 0.5 mm from below for thin-head screws.
* A 0.4 mm deep pocket on the top face under the USB-C receptacle.

## Fasteners

The screws go up through the bottom plate and the PCB into the posts, so the posts clamp the board.

| Qty per half | Screw |
|---|---|
| 6 | M2 × 3, thin/wafer head (Ø4 × ≤ 0.5 mm head, "laptop screw") |
| 1 | M2 × 2, thin/wafer head, for the front key-frame corner |

Put 0.05 mm Kapton film between the bottom plate and the PCB, so the bottom-layer traces never rest directly on aluminium.
