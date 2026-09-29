# Assembly

Do these steps once per half. They're written for the left half; the right half is the mirror image. Plan on 2–3 hours per half if you place the diodes by hand.

**Tools:** a soldering iron with a fine tip and a small chisel tip; optionally a small hotplate for the switch anchors. No reflow oven needed. Also: thin solder wire, tweezers, flux, low-temp paste (Sn42Bi58), Kapton tape, flush cutters, multimeter.

## Stack-up

```
5.0 mm ┬ plateau over the controller: the tallest point (roof underside 4.2 mm)
~4.4   │ keycap tops
~4.0   │ top of the nice!nano; 3.0 mm LiPo on the bottom plate in front of it
3.2 mm ┼ rim around the keys and along the front; S-bends join it to the plateau
1.6 mm ┼ PCB top: the shell's posts press down here
0.8 mm ┼ PCB (0.8 mm FR4, castellated half-holes under each switch; reset button on its underside)
0.0 mm ┴ bottom plate (0.8 mm FR4, no copper), flush in the shell's rabbet; 7 thin-head M2 screws come up through it
-1.1   │ reset button, standing in a window of the plate (the 1.5 mm feet keep it off the desk)
```

## 1. Diodes (skip if JLC assembled them)

1. Put a tiny dot of paste on each SOD-523 pad pair. They sit in the narrow gap on the left of every key; on the right half, on the right.
2. Place the 1N4148WT diodes with the **cathode band on the pad marked by the silkscreen bar**. That side goes to the row trace.
3. Reflow on the hotplate section by section, or use the iron.

## 2. Switches

The whole switch can be soldered from below with an iron:

* The two **contacts** sit over plated half-holes on the edge of a window in the board. This is the hand-solder trick from Mike Holscher's [mikecinq](https://github.com/mikeholscher/zmk-config-mikecinq).
* The four **frame anchors** each have a 0.7 mm plated hole through their 2 × 2 mm pad, with a 1.4 mm pad on the bottom. Heat from below travels up the hole into the anchor. This part is new and not proven yet, so try one switch first and check it holds before doing the rest.

A hotplate still works for the anchors if you have one (step 1b).

1. **Frames, iron only (1a):**
   1. Put a small blob of low-temp paste (Sn42Bi58) on each of the four square frame pads. Put no paste on the round contact pads.
   2. Drop the PG1316S in, keycaps **off**, with the two locating pins in the two small holes.
   3. Hold the switch flat with a strip of Kapton tape across it, or a small weight.
   4. Turn the board over. On each anchor's bottom pad, hold a clean, fluxed chisel tip (about 280 °C) until the paste on top melts, 2–3 s. The joint is right when a little solder shows in the hole. If it doesn't, feed a touch of solder wire into the hole.
   5. Do the diagonal corners first so the switch can't rock.
2. **Frames, hotplate (1b):** same paste. Set that spot of the board on the hotplate, about 170 °C for Sn42Bi58, and press the switch gently while the paste is molten. The anchor holes wick a little paste down; that's fine.
3. **Contacts (iron):** turn the board over. In each window you see the switch's two contact legs next to the half-holes. Add flux and flow a little solder wire from the half-hole onto the leg: one short touch (≤ 3 s, the datasheet's iron limit) per contact. Keep the joints small; the bottom plate has a window under each one.
4. With a multimeter in continuity mode, check each key: probe the column pin at the nice!nano footprint and the diode's row side, then press the key. A dead key is almost always a contact joint, and that one you can just reheat from below. To remove a switch, heat its anchors from below one at a time while levering gently.

## 3. Reset button (bottom side)

SW31, the KMR2 tact switch, goes on the **underside** of the PCB (silkscreen "RST", beside the controller). Tin one pad, place it with tweezers, solder the other three. It's pressed from below through a window in the bottom plate, so there's no pin-hole in the top of the case.

## 4. Flash and test the nice!nano *before* soldering it

1. Download the firmware from the GitHub Actions run ("Build ZMK firmware" → artifact `bayleaf-firmware`), or build it locally (see `firmware/README.md`).
2. Plug the nice!nano in. It shows up as a USB drive (`NICENANO`); if not, short RST to GND twice.
3. Copy the `settings_reset-…uf2` file, wait for the reboot, then copy the `bayleaf_left-…uf2` file (or `bayleaf_right-…` for the right half).

## 5. Solder the nice!nano flush

1. Cover the PCB area under the controller with a layer of Kapton tape, leaving the 24 holes open (poke through with a needle).
2. Lay the nice!nano on the board, components up, USB-C over the notch in the back edge of the board.
3. Push a short piece of 0.5–0.6 mm tinned wire (cut component legs work well) through each nice!nano hole into the PCB hole below. Solder it on the top, then on the bottom.
4. Cut every pin short on the bottom side. The bottom plate has a slot under each pin row, so the joints can stand up to ~0.7 mm.

## 6. Battery

1. There is no power switch: the nice!nano is live as soon as the cell is soldered, so do this step last, after flashing and testing over USB.
2. The 3.0 mm 302030 cell drops into the window in the PCB in front of the controller. It rests on the bottom plate.
3. Solder the cell's red lead to **+** and black to **−** on the BT1 pads. Keep the leads short.
4. Put Kapton on the cell. It's held by a small piece of thin double-sided tape once the plate is on.

## 7. Close the case

1. Lay the shell upside down on a soft cloth.
2. Drop the PCB in, keys down, so the switches go into the key window, and the USB-C into the opening in the back wall. The 7 holes in the PCB line up with the shell's posts.
3. Stick the battery to the bottom plate where it will meet the cell, then drop the plate into the rabbet, silkscreen out. The reset button drops into its window; the FR4 plate is an insulator, so no film is needed between it and the PCB.
4. Screw in the thin-head screws: M2×2 in the four posts under the rim (both key-frame corners and the front pair at the bay; their threads are only 1.1 mm deep), M2×3 in the other three (back of the bay, divider). Snug, not tight: the posts clamp the PCB.
5. Snap on the 30 keycaps and stick 4 bumpons under each half.

## 8. Pair

1. Both halves start as soon as their cells are connected. They pair with each other automatically; the left half is the BLE "central".
2. On the computer, pair with **Bayleaf**. The reset button is on the underside, in the window of the bottom plate. Lower+Raise gives the Adjust layer, which has the BT profile keys, `BT_CLR`, and `&bootloader` for later firmware updates over USB.

## Troubleshooting

* **A key doesn't register:** usually a switch contact pad that didn't wet. Reflow that switch, or touch up its pads from the side with the iron.
* **A whole row or column is dead:** check the flush joints on the nice!nano pins.
* **The halves don't connect:** flash `settings_reset` to both halves, then the real firmware again.
* **Short range in the aluminium case:** the controller sits under the aluminium roof, so the radio gets out downward through the FR4 bottom plate (keep it copper-free) and through the key window. The firmware already sets TX power to +8 dBm. Don't put the keyboard on a metal desk or laptop palm rest. If range is still poor, a printed (MJF/SLS) shell avoids the problem.
