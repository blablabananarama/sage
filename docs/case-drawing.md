# Case: manufacturing notes

The case comes from two sources:
- **Plan view:** the original's drawing **bayleaf-case-MK5_L**. Values from it are marked **[D]**.
- **Top surface:** the shape sent through the [Bayleaf Case Sketchpad](https://claude.ai/artifact/11zAxZXfv3bXQXGKN8ovCU), saved as [`case-sketchpad-shape.json`](case-sketchpad-shape.json). Values from it are marked **[S]**.

Per half there is one CNC part, the 6061-T6 top shell (bead-blasted and anodised), and a bottom plate made as a copper-free 0.8 mm FR4 PCB. The STEP files are in `hardware/case/out/`, the plate gerbers in `hardware/pcb/fab/plate-{left,right}/`, and the right half is the mirror image.

| Part | File | Size | Weight |
|---|---|---|---|
| Top shell (one piece, rim + controller roof) | `bayleaf-shell-{left,right}.step` | 139.4 × 96.8 × 5.0 mm | ≈ 15 g |
| … or the straight-wall variant | `bayleaf-shell-{left,right}-chamfer.step` | 139.4 × 96.8 × 5.0 mm | ≈ 17 g |
| Bottom plate (FR4) | gerbers in `hardware/pcb/fab/plate-{left,right}/`; `bayleaf-plate-*.step` for reference | 137.3 × 94.7 × 0.8 mm | ≈ 17 g |

A finished half weighs about 82 g with the electronics, so about 165 g for the pair. The original is 180 g.

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
* **Inside corners:** every vertical inside corner of the underside pocket (where the posts and the divider meet the walls and each other) is rounded to R1.65 mm, and gaps narrower than 3.3 mm (e.g. behind the two back posts) are left solid. So the pocket can be cut with a Ø3.3 mm end mill; SendCutSend's minimum is R1/16" = 1.59 mm. `MILL_R` in `case.py`.
* **Controller bay:** 27 mm **[D]**, closed on top by the shell's roof.
* **Bottom plate seat:** a rabbet 1.0 mm wide × 0.8 mm deep, leaving a 1 mm wall at the base **[D]**.
* **USB-C:** a stadium-shaped (obround) opening in the **back** wall, 9.7 × 3.9 mm with full-round ends, concentric with the 8.94 × 3.26 mm receptacle (centre z = 2.1 mm, x = 122.4 mm). Its lower curve dips 0.65 mm into the bottom plate's edge, which carries the same cut, so the outline reads as one clean stadium. There is no power-switch slot: the board has no power switch.

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

`case.py` writes four shells from the same top surface. They fit the same PCB, bottom plate and screws. See the [side-by-side comparison, with cross-sections](img/3d/compare.jpg).

| | Default (`bayleaf-shell-*`) | Chamfer (`…-chamfer`) | Round (`…-round`) | Cut corners (`…-corner`) |
|---|---|---|---|---|
| Outer walls | drafted, 1.19 mm per side **[D]** (137 × 94.4 at the top, 139.4 × 96.8 at the base) | vertical, 139.4 × 96.8 all the way up, R4.19 plan corners | same as chamfer | vertical, 139.4 × 96.8, plan corners cut at 45° with 2.5 mm legs (3.5 mm face) (`CORNER_CUT`) |
| Outer top edge | sharp | 0.5 mm × 45° chamfer (`CHAMFER`) | quarter-round R1.5 (`ROUND_OUT`) | sharp, except R1.0 along the corner faces (`CORNER_RT`) |
| Outer bottom edge | sharp | sharp | sharp | sharp, except R0.5 along the corner faces (`CORNER_RB`) |
| Key-window edge | sharp, R2 plan corners | sharp, R2 plan corners | quarter-round R0.8 (`ROUND_WIN`) | sharp, R2 plan corners |
| Weight | ≈ 15 g | ≈ 17 g | ≈ 16 g | ≈ 17 g |

The cut-corners version is modelled the way you'd machine it. Each corner is cut at 45°, then only the new face's top and bottom edges are filleted; the vertical edges beside it stay sharp (`corner_cutter()`). At 2.5 mm the cut stays clear of the corner screw posts, the PCB and the bottom plate. A larger cut, up to about 6 mm (the nice!nano limits it), would need the corner posts moved and the PCB re-routed.

The chamfer and the rounds are cut as a second height field (`chamfer_field()` / `round_field()`): the top surface, lowered by the edge profile as a function of the distance in from the outline or the key window. So the edge keeps its profile across the S-bends and runs around the plan-view corners. OCC's own chamfer and fillet can't handle the blended top surface. For the round variant, the height field is sampled every 0.15 mm near the edges, which leaves facets of well under 0.1 mm.

## Bottom plate

* 0.8 mm FR4, made as a 2-layer PCB with **no copper**, black mask and silkscreen (generated by `generate_pcb.py`, `PlateBuilder`). Aluminium would close the Faraday cage around the nice!nano; FR4 lets the 2.4 GHz signal out downward. It also insulates, so no Kapton film is needed.
* It drops into the shell's rabbet and sits flush with the base. Seven Ø2.2 mm holes; the thin screw heads sit on its outside (0.5 mm, inside the 1.5 mm feet).
* Windows: one under each switch (8.0 × 5.2 mm, for the solder on the castellated contacts), four 2.6 × 2.6 mm ones per switch under the plated frame-anchor holes, two slots under the nice!nano pin rows, one for the reset button (3.9 × 6.1 mm; the KMR2 on the PCB's underside stands in it), and a 9.7 × 7.5 mm notch in the back edge under the USB-C receptacle, below the shell's stadium opening.

## Fasteners

The screws go up through the bottom plate and the PCB into the posts, so the posts clamp the board.

| Qty per half | Screw | Posts |
|---|---|---|
| 3 | M2 × 3, thin/wafer head (Ø4 × ≤ 0.5 mm head, "laptop screw") | two at the back of the bay, one in the divider |
| 4 | M2 × 2, thin/wafer head | the four under the 3.2 mm rim (1.1 mm threads) |

