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
| Min. hole / via | 0.3 mm drill / 0.6 mm pad, which is standard |
| Min. track / spacing | 0.25 mm / 0.25 mm, which is standard |
| Mark on PCB | "Remove mark" or "specify position". Otherwise the fab may print its order number between the keys |
| Stencil (optional) | Framework or frameless stencil from the `F.Paste` layer. Worth it for pasting 30 switches per side |

### Optional: let JLCPCB place the small parts (PCBA)

Turn on *PCB Assembly → Economic, top side*. Then upload for each half:

* BOM: `hardware/pcb/fab/<side>/bayleaf-<side>-jlc-bom.csv`
* CPL: `hardware/pcb/fab/<side>/bayleaf-<side>-jlc-cpl.csv`

This places D1–D30 (1N4148WT, SOD-523: pick a stocked part in JLC's search), SW31 (TS-1187A, C318884) and SW32 (MSK12C02, C431540). **Check stock and the rotation preview** before paying. JLC's part library sometimes needs a 180° correction for small diodes. On the right PCB the diodes' cathode (pad 1, the band) must sit toward the **row** trace; in the 3D preview, check that the band points to the same side as the silkscreen band.

The switches (PG1316S) and the nice!nano are not placed by JLC. You solder them yourself (see [assembly.md](assembly.md)).

## 2. Keyboard parts

* **60 × Kailh PG1316S** plus a few spares. Pick the force you like; the lighter 25–35 gf versions are quieter. Sold as 5- or 10-packs by beekeeb, keycapsss, holykeebs and modulo.industries.
* **60 × PG1316S 1U keycaps** (16 × 16 mm) from the same shops.
* **2 × nice!nano v2**. Don't buy the "low-profile headers/sockets"; they aren't used.
* **2 × LiPo 402040** (4.0 × 20 × 40 mm, about 250–300 mAh) with a protection PCB and short leads. The controller bay has room for a cell up to 4.2 × 21 × 42 mm.

## 3. Case (top shell + bottom plate)

The case follows the original's MK5 drawing: a machined top shell with the key window and a covered controller bay, plus a flat bottom plate screwed into it. See [case-drawing.md](case-drawing.md) for the dimensions, the thread callouts, and which boss positions I changed.

* Upload `hardware/case/out/bayleaf-shell-{left,right}.step` and `bayleaf-plate-{left,right}.step` to JLCCNC, PCBWay CNC, Xometry or similar. Order qty 1 of each file.
  * Material: 6061-T6. Finish: bead blast + anodise (any colour).
  * Threads: 7 × M2×0.4 blind tapped holes per shell. Four are 2 mm deep and three are 3 mm deep (table in case-drawing.md). Add them in the shop's thread options or as a note; the STEP only contains the Ø1.6 mm tap drill.
  * The shell has a 0.8 mm roof and frame and needs machining from both sides. Expect roughly $80–130 per shell and $15–30 per plate.
* **Printed (budget) option:** the same STEP files can be printed in MJF PA12 or SLS nylon for about $15–25 per half. Use self-tapping M2 screws or heat-set inserts instead of tapped threads.
* **Screws:** 8 × M2×3 and 6 × M2×4 with a thin (≤ 0.5 mm) wafer head, e.g. a laptop-screw assortment.

## 4. Consumables

Thin double-sided tape (for the battery), Kapton tape plus a sheet of 0.05 mm Kapton film, 8 small silicone bumpons, and low-temperature solder paste (Sn42Bi58, 138 °C). The low-temperature paste keeps the switch housings well below the datasheet's 260 °C limit.
