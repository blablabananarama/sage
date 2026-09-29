# Ordering the parts

Prices are estimates from September 2026 for a single build. See [`BOM.csv`](BOM.csv) for the per-line breakdown.

## 1. PCBs (JLCPCB, or any other fab)

Upload `hardware/pcb/fab/left/bayleaf-left-gerbers.zip` and `hardware/pcb/fab/right/bayleaf-right-gerbers.zip` as **two separate orders or two items in one cart**. The halves are mirror images, not the same board.

| Setting | Value |
|---|---|
| Layers | 2 |
| Dimensions | 134.9 × 92.3 mm (auto-detected) |
| PCB thickness | **0.8 mm** (1.0 mm also works; the case then sits 0.2 mm higher) |
| Surface finish | **ENIG** recommended (flat pads for the SMD switches); lead-free HASL works |
| **Castellated holes** | **Yes** (≈ $8 extra per design). The two switch contacts sit on plated half-holes at the edge of a window under each switch, so you can solder them from below with an iron. The fab may flag the 30 internal windows; they're intended |
| Min. hole / via | 0.3 mm drill / 0.6 mm pad, which is standard |
| Min. track / spacing | 0.25 mm / 0.25 mm, which is standard |
| Mark on PCB | "Remove mark" or "specify position". Otherwise the fab may print its order number between the keys |
| Stencil (optional) | Framework or frameless stencil from the `F.Paste` layer (frame anchors and diodes only) |

### Bottom plates (same order)

Upload `hardware/pcb/fab/plate-left/bayleaf-plate-left-gerbers.zip` and `…/plate-right/bayleaf-plate-right-gerbers.zip` as two more designs: 2 layers, **0.8 mm**, **black** solder mask, white silkscreen, any finish (there's no copper). They're the case floor: FR4 lets the Bluetooth signal out, where the old aluminium plate shielded the controller. Keep them copper-free; don't let the fab add a copper pour or "thieving".

### Optional: let JLCPCB place the small parts (PCBA)

Turn on *PCB Assembly → Economic, top side*. Then upload for each half:

* BOM: `hardware/pcb/fab/<side>/bayleaf-<side>-jlc-bom.csv`
* CPL: `hardware/pcb/fab/<side>/bayleaf-<side>-jlc-cpl.csv`

This places D1–D30 (1N4148WT, SOD-523: pick a stocked part in JLC's search) (the reset button SW31 is on the bottom side, which economic assembly doesn't cover; solder it by hand). **Check stock and the rotation preview** before paying. JLC's part library sometimes needs a 180° correction for small diodes. On the right PCB the diodes' cathode (pad 1, the band) must sit toward the **row** trace; in the 3D preview, check that the band points to the same side as the silkscreen band.

The switches (PG1316S) and the nice!nano are not placed by JLC. You solder them yourself (see [assembly.md](assembly.md)).

## 2. Keyboard parts

* **60 × Kailh PG1316S** plus a few spares. Pick the force you like; the lighter 25–35 gf versions are quieter. Sold as 5- or 10-packs by beekeeb, keycapsss, holykeebs and modulo.industries.
* **60 × PG1316S 1U keycaps** (16 × 16 mm) from the same shops.
* **2 × nice!nano v2**. Don't buy the "low-profile headers/sockets"; they aren't used.
* **2 × LiPo 302030** (3.0 × 20 × 30 mm, about 120–150 mAh) with a protection PCB and short leads. The PCB window under the controller roof takes a cell up to 3.0 × 21 × 31 mm; a thicker or longer cell reaches the S-bend where the roof drops.

## 3. Case (one-piece top shell)

The case follows the original's MK5 drawing for the plan view and the shape sent through the case sketchpad for the top surface: a 3.2 mm rim around the keys and a 5.0 mm plateau over the controller, joined by soft S-bends, all one piece. See [case-drawing.md](case-drawing.md) for all dimensions and what I changed.

* Upload `hardware/case/out/bayleaf-shell-{left,right}.step` (drafted walls) **or** `bayleaf-shell-{left,right}-chamfer.step` (straight walls, 0.5 mm chamfer on the top edge) **or** `bayleaf-shell-{left,right}-round.step` (straight walls, rounded top edges); see [the comparison](img/3d/compare.jpg) to JLCCNC, PCBWay CNC, Xometry or similar. Order qty 1 of each. (The bottom plates are PCBs now, see above.)
  * Material: 6061-T6. Finish: bead blast + anodise. Silver/clear for the original's look.
  * Threads: 7 × M2×0.4, blind, cut up from the bottom into the posts: three 2 mm deep (back of the bay, divider) and four 1.1 mm deep (the posts under the rim). Add them in the shop's thread options or as a note; the STEP only contains the Ø1.6 mm tap drill.
  * Rough cost: $70–110 per half.
* **SendCutSend (CNC machining):** upload the shell STEP as is. Each file is one solid in mm, the threads aren't modelled, and the M2 holes are at the Ø1.6 mm tap-drill size. The inside corners are ≥ R1.65, which meets their R1/16" minimum.
  * Material 6061-T6; add anodising if you want it.
  * In their tapping options, pick M2×0.4 for the seven Ø1.6 holes on the underside. Four are only 1.1 mm deep (the posts under the rim), three are 2 mm deep.
  * Their page lists 1 × 1 × 1 in as the smallest part size, and the shell is 5 mm (0.2 in) thick. If the quote refuses it, send the same file to JLCCNC, PCBWay or Xometry.
* **Printed (budget) option:** the same STEP files (with their curved surfaces, so they print well) come out in MJF PA12 or SLS nylon for about $15–25 per half. Use self-tapping M2 screws.
* **Screws:** 6 × M2×3 and 8 × M2×2 with a thin (≤ 0.5 mm) wafer head, e.g. a laptop-screw assortment.

## 4. Consumables

Thin foam tape for the battery, Kapton tape (under the nice!nano), 8 small silicone bumpons, and low-temperature solder paste (Sn42Bi58, 138 °C). The low-temperature paste keeps the switch housings well below the datasheet's 260 °C limit.
