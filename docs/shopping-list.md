# Shopping list

Everything to buy for one Bayleaf (both halves), with links. Quantities include a few spares. Prices are the estimates from [`BOM.csv`](BOM.csv) (Sept 2026). Links were checked when this list was written, but shops change; any equivalent part works unless the note says otherwise.

## Made to order from the repo files

| ✓ | What | Qty | Where | Files / settings |
|---|---|---|---|---|
| ☐ | Key PCB, left | 5 (min.) | [JLCPCB](https://jlcpcb.com/) | `hardware/pcb/fab/left/bayleaf-left-gerbers.zip` · 2 layers, **0.8 mm**, ENIG, **castellated holes: Yes**, remove mark |
| ☐ | Key PCB, right | 5 (min.) | [JLCPCB](https://jlcpcb.com/) | `hardware/pcb/fab/right/bayleaf-right-gerbers.zip` · same settings |
| ☐ | Bottom plate, left (FR4) | 5 (min.) | [JLCPCB](https://jlcpcb.com/) | `hardware/pcb/fab/plate-left/bayleaf-plate-left-gerbers.zip` · 2 layers, **0.8 mm**, black mask, no copper fill |
| ☐ | Bottom plate, right (FR4) | 5 (min.) | [JLCPCB](https://jlcpcb.com/) | `hardware/pcb/fab/plate-right/bayleaf-plate-right-gerbers.zip` · same settings |
| ☐ | Top shell, left + right | 1 + 1 | [JLCCNC instant quote](https://jlccnc.com/cnc-machining-quote) or [SendCutSend CNC](https://sendcutsend.com/services/cnc-machining/) | `hardware/case/out/bayleaf-shell-{left,right}.step` (drafted walls), `…-chamfer.step` (straight walls, chamfer), `…-round.step` (straight walls, rounded edges) **or** `…-corner.step` (straight walls, cut corners). 6061-T6, bead blast + anodise, 7 × M2×0.4 threads (see [ordering.md](ordering.md)) |

Optional: a stencil for each key PCB in the same JLCPCB order (frame pads and diodes only).

## Electronics

| ✓ | What | Qty | Buy | Notes |
|---|---|---|---|---|
| ☐ | Kailh PG1316S switches | 64 (60 + 4 spare) | [beekeeb 40 gf](https://shop.beekeeb.com/products/pg1316s-40gf) / [25 gf](https://shop.beekeeb.com/products/pg1316s-25gf) (5-packs) · [holykeebs](https://holykeebs.com/products/kailh-pg1316s-butterfly-switch-10-pack) (10-packs) · [keycapsss 35 gf](https://keycapsss.com/Kailh-PG1316S-Ultra-Thin-Notebook-Switch/KC10231-35) · [modulo.industries](https://modulo.industries/product/pg1316s-switch/) | The mikecinq builder recommends 35 gf; 60 gf is heavy |
| ☐ | PG1316S keycaps, 1U | 60 | [keycapsss (black, 10×)](https://keycapsss.com/Kailh-PG1316S-Keycaps/KC10237-1U-BK) · [holykeebs](https://holykeebs.com/products/kailh-pg1316s-keycaps) · [modulo.industries](https://modulo.industries/product/pg1316s-keycap/) | 16 × 16 mm, stock Kailh caps |
| ☐ | nice!nano v2 | 2 | [Typeractive](https://typeractive.xyz/products/nice-nano) · [beekeeb](https://shop.beekeeb.com/products/nicenano) · [Little Keyboards](https://www.littlekeyboards.com/products/nice-nano) · [official store list](https://nicekeyboards.com/nice-nano/) | **Without** sockets/headers; it's soldered flush |
| ☐ | LiPo 302030, 3.7 V, with protection circuit | 2 | [KBT 302030 150 mAh (2-pack)](https://www.kbt18650battery.com/products/kbt-302030pl-3-7v-150mah-li-polymer-rechargeable-battery-2pack) · [LP302030 130 mAh](https://www.lipolbattery.com/Lithium-Ion-Polymer-Battery-LP302030.html) · [Amazon (JST lead)](https://www.amazon.com/Battery-Rechargeable-Lithium-Polymer-Connector/dp/B09F9V199L) | Max 3.0 × 21 × 31 mm. Must have the protection PCB. Cut off any connector; the leads are soldered to the pads |
| ☐ | Diode 1N4148WT, SOD-523 | 70 | [LCSC C511874](https://www.lcsc.com/product-detail/Switching-Diode_BORN-1N4148WT_C511874.html) · [LCSC C2961218](https://www.lcsc.com/product-detail/C2961218.html) | Skip if JLCPCB assembles the diodes |
| ☐ | Reset button C&K KMR211NGLFS (KMR2) | 2 (+ spares) | [DigiKey](https://www.digikey.com/en/products/detail/c-k/KMR211NG-LFS/2176482) | Any KMR2-footprint tact switch works; mounts on the PCB's underside |

## Mechanical and consumables

| ✓ | What | Qty | Buy | Notes |
|---|---|---|---|---|
| ☐ | M2 × 2 mm wafer-head screws | 8 | [Amazon (HH Fasteners, 50 pcs)](https://www.amazon.com/Machine-Screws-Laptop-Dia-5mm-Metric/dp/B01ILW3TS8) · [metricscrews.us](https://www.metricscrews.us/index.php?main_page=index&cPath=13_122_129_123) | The 4 posts under the rim per half (1.1 mm threads) |
| ☐ | M2 × 3 mm wafer-head screws | 6 | [Amazon (HH Fasteners, 50 pcs)](https://www.amazon.com/Machine-Screws-Laptop-Dia-5mm-Metric/dp/B01ILW3UV4) · [metricscrews.us](https://www.metricscrews.us/index.php?main_page=index&cPath=13_122_129_125) | The other 3 posts per half. These heads are Ø5 × 0.65 mm and sit on the outside of the plate, inside the feet |
| ☐ | Clear silicone bumpons | 8 | [Amazon (tiny bumpons)](https://www.amazon.com/Self-adhesive-Clear-Rubber-Feet-Bumpons/dp/B001JAW454) | 1.5–2.5 mm tall: taller than the reset button (1.1 mm below the plate) |
| ☐ | Kapton (polyimide) tape | 1 roll | [Amazon search](https://www.amazon.com/s?k=kapton+tape+10mm) | Under the nice!nano |
| ☐ | Thin double-sided foam tape | 1 roll | [Amazon search](https://www.amazon.com/s?k=thin+double+sided+foam+tape+1mm) | Holds the battery to the plate |
| ☐ | Low-temp solder paste Sn42Bi58 (Chip Quik TS391LT) | 1 syringe | [DigiKey](https://www.digikey.com/en/products/detail/chip-quik-inc/TS391LT/7802220) · [Amazon](https://www.amazon.com/Chip-Quik-TS391LT-Thermally-No-Clean/dp/B096BLQQNY) | Under the switch frame anchors (melted from below with the iron) and the diodes; no fridge needed |
| ☐ | Flux pen (e.g. Chip Quik CQ4LF) | 1 | [DigiKey search](https://www.digikey.com/en/products/result?keywords=CQ4LF) | For the contacts from below |
| ☐ | Thin solder wire (0.5 mm) | 1 | any | Contacts and nice!nano pins |

## Tools, if you don't have them

| ✓ | What | Buy | Notes |
|---|---|---|---|
| ☐ | Mini hotplate (optional) | [Miniware MHP30 (DFRobot)](https://www.dfrobot.com/product-2530.html) · [welectron (EU)](https://www.welectron.com/Miniware-MHP30-Hot-Plate-Preheater) · [SparkFun](https://www.sparkfun.com/mini-hot-plate-preheater-mhp30.html) | Only needed if the iron-only frame-anchor joints don't hold. 30 × 30 mm does one switch at a time |
| ☐ | Soldering iron with a fine and a small chisel tip (temperature-controlled), tweezers, flush cutters, multimeter, Phillips #00 driver | any | |

The nice!nano and its firmware: see [firmware/README.md](../firmware/README.md). Assembly: [assembly.md](assembly.md).
