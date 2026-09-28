# Bayleaf schematic

The PCBs are generated straight from `hardware/pcb/generate_pcb.py`, with no separate KiCad schematic, so this page is the schematic. Both halves are electrically identical. The right PCB is a mirrored copy that uses the same controller pins.

## Key matrix (per half: 5 rows × 6 columns, diodes `col2row`)

```
 COLn ──┬──────────────┬─── … (one column wire per physical column)
        │              │
      SWx(1)         SWy(1)        SW = Kailh PG1316S, pad 1 = column side
      SWx(2)         SWy(2)
        │              │
        ▼ D (1N4148WS) ▼            anode = pad 2 (switch side), cathode = pad 1
        │              │
 ROWm ──┴──────────────┴─── … (one row wire per row)
```

| Net | Left half: pin (GPIO, `&pro_micro`) | Right half: pin (GPIO, `&pro_micro`) |
|---|---|---|
| COL0 | D21 (P0.31, 21) | D2 (P0.17, 2) |
| COL1 | D20 (P0.29, 20) | D3 (P0.20, 3) |
| COL2 | D19 (P0.02, 19) | D4 (P0.22, 4) |
| COL3 | D18 (P1.15, 18) | D5 (P0.24, 5) |
| COL4 | D15 (P1.13, 15) | D6 (P1.00, 6) |
| COL5 | D14 (P1.11, 14) | D7 (P0.11, 7) |
| ROW0 (back row) | D9 (P1.06, 9) | D8 (P1.04, 8) |
| ROW1 | D8 (P1.04, 8) | D9 (P1.06, 9) |
| ROW2 | D7 (P0.11, 7) | D18 (P1.15, 18) |
| ROW3 | D6 (P1.00, 6) | D15 (P1.13, 15) |
| ROW4 (front row) | D5 (P0.24, 5) | D14 (P1.11, 14) |

The nice!nano is rotated 180° so its USB-C faces the front. Each half therefore uses the pin column that faces its keys, plus the back end of the other column. The front-corner pins (D0/D1) and the NFC pins (D10/D16) are left unused.

On each half, columns are numbered left → right, so the right half's COL0 is its innermost column. The pins are set per half in `bayleaf_left.overlay` / `bayleaf_right.overlay`, and the right half adds `col-offset = <6>`.

## Power and misc

```
 LiPo + ── BT1.1 (BAT+) ── SW32.1 ┐
                                   ├ MSK12C02 slide switch (common = pin 2)
 nice!nano RAW/B+ ── SW32.2 ───────┘   SW32.3 unused (= off position)
 LiPo − ── BT1.2 ── GND ── nice!nano GND (2 pins wired; the third, B−, is tied internally)

 nice!nano RST ── SW31 (TS-1187A tact switch) ── GND   double-tap → UF2 bootloader
```

The nice!nano handles charging over its own USB-C port, battery protection and 3.3 V regulation. There is no other active circuitry on the board.

## Mechanical notes that affect the circuit

* The nice!nano is soldered flush on the top side. Traces run under it on both layers, protected by soldermask; put a piece of Kapton on the PCB there before soldering it down.
* The nice!nano is rotated so its USB-C faces the front edge. The mid-mount receptacle hangs about 1.1 mm below the nice!nano, into a notch in the PCB's front edge; the bottom plate has a 0.4 mm relief below it.
* The seven aluminium bosses of the case press on the top of the PCB. Keep-out zones keep top copper and vias away from them, and the M2 screws pass through 2.2 mm non-plated holes.
* The PG1316S frame pads (`MP`) are not connected to anything. They are solder anchors only.
