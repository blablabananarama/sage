#!/usr/bin/env python3
"""Bayleaf case - one CNC-machined aluminium tray per half (CadQuery).

    /opt/cq/bin/python case.py            # writes STEP + STL for both halves into ./out

Z stack-up (mm, from the table up):
    0.00 - 0.70  aluminium floor
    0.70 - 0.80  double-sided tape (e.g. tesa 4965 cut to size, or 3M 9448A)
    0.80 - 1.60  PCB (0.8 mm FR4)
    1.60 - ~4.8  nice!nano v2 (3.2 mm incl. mid-mount USB-C) / PG1316S switch + keycap
    5.00         top of the case rim  -> 5 mm total, like the original

All XY numbers are derived from hardware/pcb/generate_pcb.py so the case always
matches the board. Origin: outer top-left corner of the left case (y grows toward
the user, like in KiCad), converted to CadQuery's y-up when building solids.
"""
import os

import cadquery as cq

# --- mirrored from generate_pcb.py (kept literal so this runs without KiCad) -----
BOARD_W, BOARD_H = 135.5, 89.5
NANO_X = 123.0
USB_NOTCH_W, USB_NOTCH_D = 10.5, 7.5
BAT_CUT = (111.8, 45.0, 134.0, BOARD_H)
POWER_SW_Y = 39.6
NANO_PIN_DX = 7.62
NANO_TOP, NANO_LEN = 0.6, 33.3

# --- case parameters -------------------------------------------------------------
WALL = 1.5
GAP = 0.25                    # PCB-to-wall clearance
OUT_W = BOARD_W + 2 * (WALL + GAP)   # 139.0
OUT_H = BOARD_H + 2 * (WALL + GAP)   # 93.0
HEIGHT = 5.0
FLOOR = 0.7
OUTER_R = 2.5                 # vertical outer corner radius
INNER_R = 1.25                # >= PCB corner radius (1.0) + GAP
TOP_FILLET = 0.5
BOTTOM_CHAMFER = 0.3
OFF = WALL + GAP              # PCB origin inside the case

USB_SLOT_W = 9.6              # USB-C plug shell is 8.25 x 2.4 mm
USB_POCKET = (11.5, USB_NOTCH_D + 1.0, 0.35)   # floor relief under the mid-mount receptacle
PIN_RELIEF = (2.4, NANO_LEN - 3.0, 0.3)        # floor relief under the flush-cut nano pins
PWR_SLOT = (4.2, 1.1)         # length along the wall, bottom of slot above floor top
BATTERY_POCKET_DEPTH = 0.0    # set to 0.3 for a 3.3 mm cell


def box_xy(w, h, x0, y0, z0, dz, r=0.0):
    """Rounded box given KiCad-style top-left (x0, y0)."""
    s = cq.Workplane("XY").workplane(offset=z0).center(x0 + w / 2, -(y0 + h / 2)).rect(w, h)
    solid = s.extrude(dz)
    if r > 0:
        solid = solid.edges("|Z").fillet(r)
    return solid


def build(side="left"):
    body = box_xy(OUT_W, OUT_H, 0, 0, 0, HEIGHT, OUTER_R)
    body = body.faces(">Z").edges().fillet(TOP_FILLET)
    body = body.faces("<Z").edges().chamfer(BOTTOM_CHAMFER)

    # main pocket for the PCB
    cut = box_xy(BOARD_W + 2 * GAP, BOARD_H + 2 * GAP, WALL, WALL, FLOOR, HEIGHT, INNER_R)

    # USB-C: open-top slot through the top wall + relief in the floor below the receptacle
    ux = OFF + NANO_X
    cut = cut.union(box_xy(USB_SLOT_W, WALL + 0.5, ux - USB_SLOT_W / 2, -0.25, FLOOR, HEIGHT))
    w, d, depth = USB_POCKET
    cut = cut.union(box_xy(w, d, ux - w / 2, WALL - 0.01, FLOOR - depth, depth + 0.02, 0.6))

    # relief under the nano's two pin rows
    w, l, depth = PIN_RELIEF
    for dx in (-NANO_PIN_DX, NANO_PIN_DX):
        cut = cut.union(box_xy(w, l, ux + dx - w / 2, OFF + NANO_TOP + 1.5, FLOOR - depth, depth + 0.02, 0.5))

    # power switch actuator: open-top slot through the inner side wall
    l, z = PWR_SLOT
    cut = cut.union(box_xy(WALL + 0.5, l, OUT_W - WALL - 0.25, OFF + POWER_SW_Y - l / 2, FLOOR + z, HEIGHT))

    if BATTERY_POCKET_DEPTH > 0:
        x0, y0, x1, y1 = BAT_CUT
        cut = cut.union(box_xy(x1 - x0 - 1, y1 - y0 - 1, OFF + x0 + 0.5, OFF + y0 + 0.5,
                               FLOOR - BATTERY_POCKET_DEPTH, BATTERY_POCKET_DEPTH + 0.02, 1.0))

    case = body.cut(cut)
    if side == "right":
        case = case.mirror("YZ", basePointVector=(OUT_W / 2, 0, 0))
    return case


def main():
    global FLOOR, HEIGHT
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true",
                    help="3D-print (MJF/SLS) variant: 1.0 mm floor, 5.3 mm tall, files suffixed -mjf")
    args = ap.parse_args()
    suffix = ""
    if args.print:
        FLOOR, HEIGHT, suffix = 1.0, 5.3, "-mjf"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for side in ("left", "right"):
        c = build(side)
        cq.exporters.export(c, os.path.join(out, f"bayleaf-case-{side}{suffix}.step"))
        cq.exporters.export(c, os.path.join(out, f"bayleaf-case-{side}{suffix}.stl"),
                            tolerance=0.02, angularTolerance=0.1)
        bb = c.val().BoundingBox()
        print(f"{side}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm, volume {c.val().Volume() / 1000:.2f} cm3, "
              f"~{c.val().Volume() / 1000 * 2.70:.0f} g in 6061")


if __name__ == "__main__":
    main()
