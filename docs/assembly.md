# Assembly

Do these steps once per half. They're written for the left half; the right half is the mirror image. Plan on 2–3 hours per half if you place the diodes by hand.

**Tools:** small hotplate (a 50 × 50 mm plate is fine; you reflow a few switches at a time), fine-tip iron, tweezers, flux, low-temp paste (Sn42Bi58), Kapton tape, flush cutters, multimeter.

## Stack-up

```
5.0 mm ┬ plateau over the controller: the tallest point (roof underside 4.2 mm)
~4.4   │ keycap tops
~4.0   │ top of the nice!nano; 3.0 mm LiPo on the bottom plate in front of it
3.2 mm ┼ rim around the keys and along the front; S-bends join it to the plateau
1.6 mm ┼ PCB top: the shell's posts press down here
0.8 mm ┼ PCB (0.8 mm FR4) on 0.05 mm Kapton film
0.0 mm ┴ bottom plate (0.8 mm aluminium), flush in the shell's rabbet; 7 thin-head M2 screws come up through it
```

## 1. Diodes (skip if JLC assembled them)

1. Put a tiny dot of paste on each SOD-523 pad pair. They sit in the narrow gap on the left of every key; on the right half, on the right.
2. Place the 1N4148WT diodes with the **cathode band on the pad marked by the silkscreen bar**. That side goes to the row trace.
3. Reflow on the hotplate section by section, or use the iron.

## 2. Switches

1. Apply paste to the two contact pads **and** the four square frame pads of each footprint. A stencil makes this trivial; a syringe works too.
2. Drop each PG1316S in, with the two locating pins in the two small holes. The contacts face the pads near the bottom of the footprint.
3. Reflow 4–6 switches at a time on the hotplate. With Sn42Bi58, about 170 °C is enough; don't cook the switches. Press each switch gently while the paste is molten so it seats flat.
4. With a multimeter in continuity mode, check each key: probe the column pin at the nice!nano footprint and the diode's row side, then press the key.

## 3. Reset button and power switch

Solder SW31 (KMR2 tact switch, beside the controller) and SW32 (slide switch on the inner edge, lever pointing out of the board). Skip this if JLC placed them.

## 4. Flash and test the nice!nano *before* soldering it

1. Download the firmware from the GitHub Actions run ("Build ZMK firmware" → artifact `bayleaf-firmware`), or build it locally (see `firmware/README.md`).
2. Plug the nice!nano in. It shows up as a USB drive (`NICENANO`); if not, short RST to GND twice.
3. Copy the `settings_reset-…uf2` file, wait for the reboot, then copy the `bayleaf_left-…uf2` file (or `bayleaf_right-…` for the right half).

## 5. Solder the nice!nano flush

1. Cover the PCB area under the controller with a layer of Kapton tape, leaving the 24 holes open (poke through with a needle).
2. Lay the nice!nano on the board, components up, USB-C over the notch in the back edge of the board.
3. Push a short piece of 0.5–0.6 mm tinned wire (cut component legs work well) through each nice!nano hole into the PCB hole below. Solder it on the top, then on the bottom.
4. Cut every pin **flush** on the bottom side. The case floor only has a 0.3 mm relief under the pin rows.

## 6. Battery

1. Slide the power switch to OFF.
2. The 3.0 mm 302030 cell drops into the window in the PCB in front of the controller. It rests on the bottom plate.
3. Solder the cell's red lead to **+** and black to **−** on the BT1 pads. Keep the leads short.
4. Put Kapton on the cell. It's held by a small piece of thin double-sided tape once the plate is on.

## 7. Close the case

1. Lay the shell upside down on a soft cloth.
2. Drop the PCB in, keys down, so the switches go into the key window, USB-C into the window in the back wall, and the power-switch lever into the side slot. The 7 holes in the PCB line up with the shell's posts.
3. Put the 0.05 mm Kapton film on the back of the PCB. Stick the battery to the bottom plate where it will meet the cell, then drop the plate into the rabbet.
4. Screw in the thin-head screws: M2×2 in the four posts under the rim (both key-frame corners and the front pair at the bay; their threads are only 1.1 mm deep), M2×3 in the other three (back of the bay, divider). Snug, not tight: the posts clamp the PCB.
5. Snap on the 30 keycaps and stick 4 bumpons under each half.

## 8. Pair

1. Switch both halves ON. They pair with each other automatically; the left half is the BLE "central".
2. On the computer, pair with **Bayleaf**. The reset button is reachable with a paper clip through the pin-hole in the plateau. Lower+Raise gives the Adjust layer, which has the BT profile keys, `BT_CLR`, and `&bootloader` for later firmware updates over USB.

## Troubleshooting

* **A key doesn't register:** usually a switch contact pad that didn't wet. Reflow that switch, or touch up its pads from the side with the iron.
* **A whole row or column is dead:** check the flush joints on the nice!nano pins.
* **The halves don't connect:** flash `settings_reset` to both halves, then the real firmware again.
* **Short range in the aluminium case:** the controller sits under the aluminium roof, so the radio mostly escapes through the key window and the USB window. The firmware already sets TX power to +8 dBm. If range is still poor, a printed (MJF/SLS) shell avoids the problem.
