# Case: manufacturing notes

The case comes from two sources:
- **Plan view:** the original's drawing **bayleaf-case-MK5_L**. Values from it are marked **[D]**.
- **Top surface:** the shape sent through the [Bayleaf Case Sketchpad](https://claude.ai/artifact/11zAxZXfv3bXQXGKN8ovCU), saved as [`case-sketchpad-shape.json`](case-sketchpad-shape.json). Values from it are marked **[S]**.

There are two CNC parts per half, both 6061-T6, bead-blasted and anodised. The STEP files are in `hardware/case/out/`, and the right half is the mirror image.

| Part | File | Size | Weight (6061) |
|---|---|---|---|
| Top shell (one piece, rim + controller roof) | `bayleaf-shell-{left,right}.step` | 139.4 × 96.8 × 5.0 mm | ≈ 15 g |
| … or the straight-wall variant | `bayleaf-shell-{left,right}-chamfer.step` | 139.4 × 96.8 × 5.0 mm | ≈ 16 g |
| Bottom plate | `bayleaf-plate-{left,right}.step` | 137.3 × 94.7 × 0.8 mm | ≈ 28 g |

A finished half weighs about 92 g with the electronics, so about 185 g for the pair. The original is 180 g.

## Top surface: two flat levels joined by soft S-bends [S]

```
           x = 0                    96.5        137
   y = 0   ┌──────────────────────────┬───────────┐  back (USB-C)
           │                          ╎  HIGH     │
           │   LOW  3.2 mm            ╎  5.0 mm   │
           │   (rim around the keys)  ╎  plateau  │
   y = 76  │                  ╌ ╌ ╌ ╌ ┘           │
           │                                      │
  y = 94.4 └──────────────────────────────────────┘  front (typist)
```

* **LOW = 3.2 mm:** the rim around the key window and the whole front strip, about level with the keycap underside.
* **HIGH = 5.0 mm:** a plateau over the controller, x ≥ 96.5 mm and y ≤ 76 mm. It has square corners (the sketch's rectangle, straightened as the note asked) and is the tallest point, slightly above the ~4.4 mm keycap tops.
* **S-bends:** both inner edges of the plateau blend into the rim over 16.5 mm (10–90 %). The blend is a Gaussian-blurred step, `top_z(x, y)` in `case.py`, so where the two bends meet at the plateau's inner corner the surface stays smooth. On the back face this gives the S-curve beside the USB-C, and the second S runs across the top toward the front.
* The roof over the controller is part of the shell, continuous with the rim. There is **no separate lid**.

## Heights inside

```
5.0 mm  plateau top: the tallest point [S]
4.2 mm  roof underside over the controller (0.8 mm skin)
~4.4 mm keycap tops (PG1316S + stock cap on a 0.8 mm PCB)
~4.0 mm top of the nice!nano (only ~2.4 mm of its 3.2 mm sits above the PCB; the USB-C shell hangs into a PCB notch)
3.8 mm  top of the 3.0 mm LiPo (roof underside above it ≥ 4.0 mm)
3.2 mm  rim [S]; 2.4 mm underside
1.6 mm  PCB top
0.8 mm  bottom plate top
```

## Top shell

* **Top outline:** 137 mm wide **[D]**. The walls are drafted, so the base is 1.19 mm larger per side **[D]**. The depth is assumed to be 86 + 2 × 4.2 = 94.4 mm.
* **Key window:** 103 × 86 mm **[D]**, 4.2 mm from the edge **[D]**, with R2 inside corners **[S]**.
* **Skin:** 0.8 mm, following the top surface (rim and controller roof).
* **Divider:** 2 mm **[D]**. It stops 1.2 mm above the PCB so the SMD parts pass underneath.
* **Controller bay:** 27 mm **[D]**, closed on top by the shell's roof.
* **Bottom plate seat:** a rabbet 1.0 mm wide × 0.8 mm deep, leaving a 1 mm wall at the base **[D]**.
* **USB-C:** a stadium-shaped (obround) opening in the **back** wall, 9.7 × 3.9 mm with full-round ends, concentric with the 8.94 × 3.26 mm receptacle (centre z = 2.1 mm, x = 122.4 mm). Its lower curve dips 0.65 mm into the bottom plate's edge, which carries the same cut, so the outline reads as one clean stadium. There is no power-switch slot: the board has no power switch.
* **Reset:** a Ø1.6 mm pin-hole through the plateau above the KMR2 button (PCB (110.15, 22.0)).

### Posts: M2×0.4 6H, blind from below, Ø2.4 × 90° countersink [D]

| Qty | Position (x, y from the back-left corner of the top outline) | Post | Thread | Note |
|---|---|---|---|---|
| 1 | (2.9, 3.5) | Ø6 | **1.1 mm** | back key-frame corner **[D]**, under the 3.2 mm rim |
| 1 | (2.9, 90.9) | Ø6 | **1.1 mm** | front key-frame corner **[D]**, under the rim |
| 2 | (111.2, 3.5), (133.95, 3.5) | Ø4 | 2 mm | back of the bay, flanking the USB-C. **Moved:** the drawing's pair is 19.039 mm apart, which would sit on the nice!nano's pins. |
| 1 | (109.5, 47.2) | Ø6 | 2 mm | middle of the divider **[D]** |
| 2 | (113.68, 90.9), (131.72, 90.9), 18.037 ±0.1 apart | Ø6 | **1.1 mm** | front of the bay **[D]**, under the rim |

The posts come down onto the PCB. The drawing's 3 mm-deep threads don't fit under a 5 mm keyboard, so `case.py` sizes each thread to leave 0.5 mm of material above it: 2 mm under the plateau, 1.1 mm under the rim. The STEP models them at the Ø1.6 mm tap-drill size; give the shop the thread callout.

## Wall variants

`case.py` writes two shells from the same top surface. They fit the same PCB, bottom plate and screws. [Side by side](img/3d/compare.jpg):

| | Default (`bayleaf-shell-*`) | Chamfer (`bayleaf-shell-*-chamfer`) |
|---|---|---|
| Outer walls | drafted, 1.19 mm per side **[D]** (137 × 94.4 at the top, 139.4 × 96.8 at the base) | vertical, 139.4 × 96.8 all the way up, R4.19 corners |
| Top edge | sharp | 1.0 mm × 45° chamfer following the rim, the S-bends and the plateau (`CHAMFER` in `case.py`) |

The chamfer is cut as a second height field (`chamfer_field()`): the top surface lowered by 1 mm plus the distance in from the outline. So it keeps a constant 45° across the bends and runs around the corners. OCC's own chamfer can't handle the blended top surface.

## Bottom plate

* 0.8 mm thick. It drops into the shell's rabbet and sits flush with the base.
* Seven Ø2.2 mm holes, counterbored Ø4.2 × 0.5 mm from below for thin-head screws.
* A 0.4 mm deep pocket on the top face under the USB-C receptacle, and the lower curve of the USB-C opening in its back edge.

## Fasteners

The screws go up through the bottom plate and the PCB into the posts, so the posts clamp the board.

| Qty per half | Screw | Posts |
|---|---|---|
| 3 | M2 × 3, thin/wafer head (Ø4 × ≤ 0.5 mm head, "laptop screw") | two at the back of the bay, one in the divider |
| 4 | M2 × 2, thin/wafer head | the four under the 3.2 mm rim (1.1 mm threads) |

Put 0.05 mm Kapton film between the bottom plate and the PCB, so the bottom-layer traces never rest directly on aluminium.
