# Ordering the parts

Prices are estimates from September 2026 for a single build. See [`BOM.csv`](BOM.csv) for the per-line breakdown.

## 1. PCBs (JLCPCB, or any other fab)

Upload `hardware/pcb/fab/left/bayleaf-left-gerbers.zip` and `hardware/pcb/fab/right/bayleaf-right-gerbers.zip` as **two separate orders or two items in one cart**. The halves are mirror images, not the same board.

| Setting | Value |
|---|---|
| Layers | 2 |
| Dimensions | 135.5 × 89.5 mm (auto-detected) |
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

This places D1–D30 (1N4148WS, C2128), SW31 (TS-1187A, C318884) and SW32 (MSK12C02, C431540). **Check stock and the rotation preview** before paying. JLC's part library sometimes needs a 180° correction for SOD-323 diodes. On the right PCB the diodes' cathode (pad 1, the band) must sit toward the **row** trace; in the 3D preview, check that the band points to the same side as the silkscreen band.

The switches (PG1316S) and the nice!nano are not placed by JLC. You solder them yourself (see [assembly.md](assembly.md)).

## 2. Keyboard parts

* **60 × Kailh PG1316S** plus a few spares. Pick the force you like; the lighter 25–35 gf versions are quieter. Sold as 5- or 10-packs by beekeeb, keycapsss, holykeebs and modulo.industries.
* **60 × PG1316S 1U keycaps** (16 × 16 mm) from the same shops.
* **2 × nice!nano v2**. Don't buy the "low-profile headers/sockets"; they aren't used.
* **2 × LiPo 302040** (3.0 × 20 × 40 mm) with a protection PCB and short leads. A 301230 or 401230 also fits but has roughly half the capacity.

## 3. Case

* **CNC aluminium, as in the original:** upload `hardware/case/out/bayleaf-case-left.step` and `…-right.step` to JLCCNC, PCBWay CNC, Xometry or similar.
  * Material: 6061-T6. Finish: bead blast + anodise (any colour). Qty 1 each.
  * Mention that the **floor is 0.7 mm thick** and should be machined with the part fixtured by its outer walls. Some shops ask for a 0.8 mm minimum; you can change `FLOOR` in `case.py`, which costs 0.1 mm of total height.
  * Expected: roughly $60–125 per half, depending on shop and finish.
* **Printed (budget) option:** run `python case.py --print` and upload the `…-mjf.stl` files for MJF PA12 or SLS nylon. This variant has a 1.0 mm floor and is 5.3 mm tall, for about $10–15 per half.

## 4. Consumables

Double-sided tape ≤ 0.1 mm (tesa 4965 / 3M 9448A), Kapton tape, 8 small silicone bumpons, and low-temperature solder paste (Sn42Bi58, 138 °C). The low-temperature paste keeps the switch housings well below the datasheet's 260 °C limit.
