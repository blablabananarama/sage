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

| Net  | nice!nano pin (Pro Micro label) | nRF52840 GPIO | ZMK `&pro_micro` |
|------|------|------|----|
| COL0 (outer-left column of the left half / inner column of the right half) | D1 | P0.06 | 1 |
| COL1 | D0 | P0.08 | 0 |
| COL2 | D2 | P0.17 | 2 |
| COL3 | D3 | P0.20 | 3 |
| COL4 | D4 | P0.22 | 4 |
| COL5 | D5 | P0.24 | 5 |
| ROW0 (top row) | D6 | P1.00 | 6 |
| ROW1 | D7 | P0.11 | 7 |
| ROW2 | D8 | P1.04 | 8 |
| ROW3 | D9 | P1.06 | 9 |
| ROW4 (bottom row) | D14 | P1.11 | 14 |

On each half, columns are numbered left → right, so the right half's COL0 is its innermost column. The firmware adds `col-offset = <6>` for the right half.

## Power and misc

```
 LiPo + ── BT1.1 (BAT+) ── SW32.1 ┐
                                   ├ MSK12C02 slide switch (common = pin 2)
 nice!nano RAW/B+ ── SW32.2 ───────┘   SW32.3 unused (= off position)
 LiPo − ── BT1.2 ── GND ── nice!nano GND (3 pins)

 nice!nano RST ── SW31 (TS-1187A tact switch) ── GND   double-tap → UF2 bootloader
```

The nice!nano handles charging over its own USB-C port, battery protection and 3.3 V regulation. There is no other active circuitry on the board.

## Mechanical notes that affect the circuit

* The nice!nano is soldered flush on the top side. A top-copper keep-out under its footprint means only vias and bottom-layer traces run under it. Put a piece of Kapton on the PCB there anyway.
* The mid-mount USB-C receptacle hangs about 1.1 mm below the nice!nano, into the notch in the PCB's top edge. The case floor has a 0.35 mm relief below it.
* The PG1316S frame pads (`MP`) are not connected to anything. They are solder anchors only.
