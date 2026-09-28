# Bayleaf: ultra-low-profile wireless split keyboard (reproduction)

This is an open, buildable re-creation of Sebastian Graz's [Bayleaf](https://www.graz.io/articles/bayleaf-wireless-keyboard/): a 60-key (2 × 5×6) ortholinear split keyboard. It uses Kailh PG1316S laptop-style switches, runs ZMK on nice!nano controllers, and sits in a CNC-machined aluminium case 5 mm thick.

> **Provenance.** The original Bayleaf is a one-off prototype and is **not open source**. None of its files are used here. This repository is an independent design built to the published specs (139 × 93 mm per half, 5 mm thick, ~180 g, PG1316S, nice!nano/ZMK, CNC aluminium enclosure, MJF keycaps). Everything else was designed from scratch: board layout, pin mapping, case geometry, keymap and part choices. The PG1316S land pattern comes from Kailh's datasheet (CPG1316S01D02).

![Bayleaf reproduction, both halves](docs/img/3d/hero.jpg)

| | |
|---|---|
| ![top view](docs/img/3d/top.jpg) | ![controller close-up](docs/img/3d/closeup.jpg) |
| ![exploded view: shell, keycaps, switches, PCB, bottom plate, screws](docs/img/3d/exploded.jpg) | ![inside: PCB with the nice!nano, battery and switches, shell removed](docs/img/3d/inside.jpg) |

*Renders are generated from the actual case STEP files and the routed PCB artwork (`docs/render3d/render.sh`). The keycap legends show the default keymap. The case follows the original's MK5 case drawing: top shell with a covered controller bay, plus a screwed-on bottom plate.*

| | Original Bayleaf (published) | This reproduction |
|---|---|---|
| Layout | 60 % ortholinear split | 2 × 5 rows × 6 columns, 17 × 17 mm pitch |
| Size per half | 139 × 93 mm; the MK5 case drawing gives 3.8–6.2 mm | 139.4 × 96.8 mm base, 3.8 mm at the front edge → 6.2 mm at the back and over the controller |
| Weight | 180 g | ~210 g estimated (shell 19 g + plate 28 g per half in 6061) |
| Switches | Kailh PG1316S | Kailh PG1316S, reflow-soldered |
| Keycaps | custom MJF prints | stock Kailh PG1316S 1U caps (16 × 16 mm) |
| Controller | nice!nano, ZMK | nice!nano v2 soldered flush, ZMK (BLE split) |
| Battery | "over a month" | 402040 LiPo (~250–300 mAh) per half, deep sleep after 15 min |
| Case | CNC aluminium, MK5 drawing | CNC 6061 top shell (key window, covered controller bay, 7 tapped M2 bosses) + 0.8 mm bottom plate, modelled on the MK5 drawing ([notes](docs/case-drawing.md)) |

## What's in here

```
hardware/pcb/generate_pcb.py      the whole PCB as code: placement, nets, outline -> Freerouting -> DRC -> fab files
hardware/pcb/bayleaf-{left,right}.kicad_pcb   routed KiCad 7 boards (open in KiCad to inspect or edit)
hardware/pcb/lib/bayleaf.pretty/  footprints: PG1316S, nice!nano (flush), battery pads
hardware/pcb/fab/{left,right}/    gerbers+drill zip, JLCPCB BOM/CPL, 3D STEP of the board, DRC report
hardware/case/case.py             parametric shell + bottom plate (CadQuery); out/ has STEP + STL
firmware/                         ZMK shield "bayleaf" + keymap; built by .github/workflows/firmware.yml
docs/BOM.csv                      full bill of materials with prices
docs/ordering.md                  exact fab settings (PCB, PCBA, CNC, parts)
docs/assembly.md                  step-by-step build guide
docs/schematic.md                 circuit / pin map
docs/case-drawing.md              case dimensions, tapped holes, screws
```

| Left PCB | Right PCB |
|---|---|
| ![left pcb](docs/img/pcb-left.png) | ![right pcb](docs/img/pcb-right.png) |

## How much does one cost?

These are estimates from September 2026 for a single keyboard, including spares and shipping. The details are in [`docs/BOM.csv`](docs/BOM.csv).

| | USD |
|---|---:|
| PCBs (2 designs × 5 pcs, 0.8 mm, ENIG) | 40 |
| 64 × Kailh PG1316S switches | 64 |
| 60 × PG1316S keycaps | 27 |
| 2 × nice!nano v2 | 50 |
| 2 × LiPo 402040 | 10 |
| Diodes, slide switches, reset buttons | 2 |
| Tape, Kapton, bumpons, M2 screws | 22 |
| Shipping (rough) | 35 |
| 2 × CNC aluminium top shell + bottom plate (6061, anodised) | 230 |
| **Electronics only** (PCBs, switches, diodes, controllers, batteries, slide and reset switches) | **≈ $167** |
| **Total with aluminium case** | **≈ $480** |
| **Total with printed nylon case instead** | **≈ $290** |

Optional extras: JLCPCB assembly of the 64 small SMD parts (≈ $40), SMT stencils (≈ $14), and a hotplate plus low-temp paste if you don't own them (≈ $60–120).

Most of the extra units are leftovers you can't avoid: 3 spare PCBs per side at the 5-piece minimum, spare switches, and so on.

## Build it

1. **Order**: follow [docs/ordering.md](docs/ordering.md). Upload the gerber zips, optionally the JLC BOM/CPL, and the case STEP files. Buy switches, caps, 2 nice!nanos and 2 cells.
2. **Firmware**: GitHub Actions builds `bayleaf_left`, `bayleaf_right` and `settings_reset` UF2s on every push. See [firmware/README.md](firmware/README.md).
3. **Assemble**: follow [docs/assembly.md](docs/assembly.md). The rough order is diodes → switches (hotplate) → reset/power → nice!nano flush → battery → PCB into the shell → bottom plate + 7 screws.

## Regenerating the design

The committed outputs are all you need to order. To change something (pitch, board size, pin map, case wall), edit the constants at the top of `generate_pcb.py` or `case.py` and run:

```sh
make pcb      # KiCad 7 python (pcbnew) + Freerouting 2.x jar (FREEROUTING_JAR=...)
make case     # CadQuery (shell + bottom plate)
make render   # README renders (docs/render3d)
```

The PCB script autoroutes with Freerouting and re-runs until nothing is unrouted. It writes a DRC report next to the gerbers. The committed boards have **0 unconnected pads and 0 electrical DRC errors**; the report only lists cosmetic silkscreen warnings. Freerouting isn't deterministic, so each regeneration produces different (equally valid) traces.

## Status and caveats

* **Not yet built.** The design passes DRC and the case was checked against the board in CAD, but no physical prototype exists yet. Order one set of PCBs before ordering in quantity.
* The PG1316S footprint follows the Kailh datasheet land pattern. Its contact-pad coordinates were cross-checked against the dimensions Mike Holscher published for his working [mikefive](https://github.com/mikeholscher/zmk-config-mikefive) build. Still, print the board 1:1 and check a real switch against it before ordering.
* The nice!nano is soldered flush, without sockets, to reach 5 mm. Flash and test it **before** soldering it down.
* The LCSC part numbers in the BOM are well-known parts, but check stock before ordering.
* **Case vs. the MK5 drawing.** The drawing gives no overall depth, and there's no section through the key area, so some values are my reading. The depth assumes a 4.2 mm border all round, and the curve lengths and keycap heights are estimates. [docs/case-drawing.md](docs/case-drawing.md) marks which numbers come from the drawing.
  * The two tapped bosses beside the USB port are moved 1.6 mm outward, so they don't land on the nice!nano's pins.
  * With a 0.8 mm PCB on the 0.8 mm bottom plate, the keycap tops sit roughly flush with the 3.8 mm front edge but about 1.8 mm below the 6.2 mm back frame. If that's wrong for the real PG1316S stack, raise the PCB with a thicker bottom plate (`PLATE_T` in `case.py`).
* **Radio.** The nice!nano now sits under an aluminium roof. BLE range may suffer, which is a known trade-off of full-metal cases. The firmware already uses +8 dBm TX power, and a printed shell avoids the problem entirely.
