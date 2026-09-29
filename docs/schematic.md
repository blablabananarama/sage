# Bayleaf schematic

The PCBs are generated straight from `hardware/pcb/generate_pcb.py`, with no separate KiCad schematic, so this page is the schematic. Both halves have the same circuit. The right PCB is a mirrored layout; its matrix uses different controller pins (table below).

## Key matrix (per half: 5 rows × 6 columns, diodes `col2row`)

```
 COLn ──┬──────────────┬─── … (one column wire per physical column)
        │              │
      SWx(1)         SWy(1)        SW = Kailh PG1316S, pad 1 = column side
      SWx(2)         SWy(2)
        │              │
        ▼ D (1N4148WT) ▼            anode = pad 2 (switch side), cathode = pad 1
        │              │
 ROWm ──┴──────────────┴─── … (one row wire per row)
```

| Net | Left half: pin (GPIO, `&pro_micro`) | Right half: pin (GPIO, `&pro_micro`) |
|---|---|---|
| COL0 | D2 (P0.17, 2) | D21 (P0.31, 21) |
| COL1 | D3 (P0.20, 3) | D20 (P0.29, 20) |
| COL2 | D4 (P0.22, 4) | D19 (P0.02, 19) |
| COL3 | D5 (P0.24, 5) | D18 (P1.15, 18) |
| COL4 | D6 (P1.00, 6) | D15 (P1.13, 15) |
| COL5 | D7 (P0.11, 7) | D14 (P1.11, 14) |
| ROW0 (back row) | D8 (P1.04, 8) | D9 (P1.06, 9) |
| ROW1 | D9 (P1.06, 9) | D8 (P1.04, 8) |
| ROW2 | D18 (P1.15, 18) | D7 (P0.11, 7) |
| ROW3 | D15 (P1.13, 15) | D6 (P1.00, 6) |
| ROW4 (front row) | D14 (P1.11, 14) | D5 (P0.24, 5) |

The nice!nano sits with its USB-C facing the back edge (the case's USB-C opening is in the back wall). Each half uses the pin column that faces its keys for the columns, and continues the rows on the nearer pins. The NFC pins (D10/D16) and the serial pins (D0/D1) are left unused.

On each half, columns are numbered left → right, so the right half's COL0 is its innermost column. The pins are set per half in `bayleaf_left.overlay` / `bayleaf_right.overlay`, and the right half adds `col-offset = <6>`.

## Power and misc

```
 LiPo + ── BT1.1 ── nice!nano RAW/B+   (no power switch; ZMK deep sleep after 15 min idle)
 LiPo − ── BT1.2 ── GND ── nice!nano GND (2 pins wired; the third, B−, is tied internally)

 nice!nano RST ── SW31 (KMR2 tact switch, bottom side) ── GND   double-tap → UF2 bootloader
```

The nice!nano handles charging over its own USB-C port, battery protection and 3.3 V regulation. There is no other active circuitry on the board.

## Mechanical notes that affect the circuit

* The nice!nano is soldered flush on the top side. Traces run under it on both layers, protected by soldermask; put a piece of Kapton on the PCB there before soldering it down.
* The nice!nano's USB-C faces the back edge. The mid-mount receptacle hangs about 1.1 mm below the nice!nano, into a notch in the PCB's back edge; the bottom plate has a notch below it.
* The 302030 cell sits in a window in the PCB in front of the controller, on the bottom plate.
* The seven aluminium bosses of the case press on the top of the PCB. Keep-out zones keep top copper and vias away from them, and the M2 screws pass through 2.2 mm non-plated holes.
* The PG1316S frame pads (`MP`) are not connected to anything. They are solder anchors only.
* The PG1316S contacts (pads 1/2) are **castellated half-holes** on the front edge of a window under each switch, so they're soldered from below with an iron; the autorouter treats the windows as keep-outs.
* The reset button SW31 is the only part on the bottom side. It sits in a window of the FR4 bottom plate.
