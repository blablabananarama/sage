#!/usr/bin/env python3
"""Bayleaf case (CadQuery), modelled on the original's drawing "bayleaf-case-MK5_L".

Two CNC parts per half:
  * top shell   - key window 103 x 86, 2 mm divider, 27 mm controller bay closed by a 0.8 mm roof,
                  6.2 mm tall at the back / over the controller, curving down to 3.8 mm at the
                  front edge of the key area, ~9 deg drafted side walls, 7 tapped M2 bosses underneath
  * bottom plate - 0.8 mm, sits flush in a 1 x 0.8 mm rabbet, screwed into the bosses; clamps the PCB

    /opt/cq/bin/python case.py        # -> out/bayleaf-{shell,plate}-{left,right}.{step,stl}

Coordinates ("shell coords"): x to the right, y toward the typist (front), origin at the back-left
corner of the 137 x 94.4 top outline. CadQuery Y = -y. Right half = mirror image.
Dimensions quoted in the MK5 drawing are marked [D]; everything else is derived or assumed.
"""
import math
import os

import cadquery as cq

# ---------------------------------------------------------------- outline / heights
TOP_W = 137.0                  # [D] top outline width
BORDER = 4.2                   # [D] key-window offset from the left edge (assumed same at back/front)
WIN_W, WIN_H = 103.0, 86.0     # [D] key window
TOP_H = WIN_H + 2 * BORDER     # 94.4 (drawing gives no overall depth; assumed symmetric border)
DRAFT = 1.19                   # [D] base outline is 1.19 larger per side (99 deg walls + chamfer)
BASE_W, BASE_H = TOP_W + 2 * DRAFT, TOP_H + 2 * DRAFT   # 139.38 x 96.78
R_TOP = 3.0
H_MAX, H_MIN = 6.2, 3.8        # [D]
FRONT_RAMP = 24.0              # front strip that curves down to H_MIN (read off the side view)
RAMP_X = (72.0, 101.0)         # along x the front ramp fades out toward the controller bay (section A)
SKIN = 0.8                     # [D] roof / frame thickness
WALL_IN = 0.8                  # inner cavity inset from the top outline (gives the 27 mm bay [D])
RABBET_W, PLATE_T = 1.0, 0.8   # [D] bottom plate rabbet: leaves a 1 mm wall at the base
DIV_X = BORDER + WIN_W         # 107.2 divider start [D]
DIV_W = 2.0                    # [D]
BAY_X0, BAY_X1 = DIV_X + DIV_W, DIV_X + DIV_W + 27.0   # 109.2 .. 136.2 [D]
BAY_CX = (BAY_X0 + BAY_X1) / 2                          # 122.7

# ---------------------------------------------------------------- stack-up inside
PCB_OFF = WALL_IN + 0.25       # PCB origin in shell coords (0.25 mm clearance to the cavity wall)
PCB_Z0 = PLATE_T               # PCB bottom
PCB_TOP = PLATE_T + 0.8        # 1.6
RIB_BOTTOM = PCB_TOP + 1.2     # divider rib stops above the SMD parts

# ---------------------------------------------------------------- bosses (x, y, diameter, thread depth)
# [D] 4x M2x0.4 6H x 2 (TL, BL, back pair 18.037 apart) and 3x M2 x 3 (divider middle, front pair).
# The front pair is 19.039 [D] apart in the drawing, which would sit on a nice!nano's pin rows, so here
# it is moved out to the bay corners (22.5 apart, dia 4) - the one deliberate deviation.
BOSSES = [
    (2.9, 3.5, 6.0, 2.0),
    (2.9, TOP_H - 3.5, 6.0, 2.0),
    (BAY_CX - 18.037 / 2, 3.5, 6.0, 2.0),
    (BAY_CX + 18.037 / 2, 3.5, 6.0, 2.0),
    (109.5, TOP_H / 2, 6.0, 3.0),
    (BAY_X0 + 2.25, TOP_H - 3.5, 4.0, 3.0),
    (BAY_X1 - 2.25, TOP_H - 3.5, 4.0, 3.0),
]
TAP_DRILL = 1.6                # M2 tap drill; threads are called out in docs/case-drawing.md

# ---------------------------------------------------------------- openings (from the PCB layout)
USB_X = BAY_CX                 # nice!nano centred in the bay, USB-C facing the front
USB_W, USB_Z0, USB_Z1 = 10.0, PLATE_T, 4.3
PWR_Y = PCB_OFF + 53.9         # slide switch on the inner side wall
PWR_L, PWR_Z1 = 4.4, 3.4
RESET_PIN = (PCB_OFF + 116.5, PCB_OFF + 53.0, 1.6)   # paper-clip hole through the roof


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def rrect_wire(w, h, r, cx, cy, z):
    s = cq.Sketch().rect(w, h).vertices().fillet(r)
    return s._faces.Faces()[0].outerWire().translate(cq.Vector(cx, cy, z))


def prism(x0, y0, w, h, z0, dz, r=0.0):
    """Box from shell coords (top-left x0, y0)."""
    wp = cq.Workplane("XY").workplane(offset=z0).center(x0 + w / 2, -(y0 + h / 2))
    if r > 0:
        return wp.sketch().rect(w, h).vertices().fillet(r).finalize().extrude(dz)
    return wp.rect(w, h).extrude(dz)


def cyl(x, y, d, z0, dz):
    return cq.Workplane("XY").workplane(offset=z0).center(x, -y).circle(d / 2).extrude(dz)


def height_profile(dz=0.0):
    """Solid whose top surface is the case's top surface (optionally lowered by dz)."""
    def section(x, t):
        t = max(t, 0.002)
        pl = cq.Plane(origin=(x, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
        y_r = TOP_H - FRONT_RAMP
        pts = [(-(y_r + FRONT_RAMP * k / 12), H_MAX - dz - (H_MAX - H_MIN) * t * smooth(k / 12)) for k in range(13)]
        wp = (cq.Workplane(pl).moveTo(10, -2).lineTo(10, H_MAX - dz).lineTo(-y_r, H_MAX - dz)
              .spline(pts[1:], includeCurrent=True).lineTo(-(TOP_H + 10), pts[-1][1])
              .lineTo(-(TOP_H + 10), -2).close())
        return wp.wires().val()
    x0, x1 = RAMP_X
    stations = [(-10, 1.0), (x0, 1.0)] + [(x0 + (x1 - x0) * k / 8, 1 - smooth(k / 8)) for k in range(1, 9)] \
        + [(BASE_W + 10, 0.0)]
    wires = [section(x, t) for x, t in stations]
    return cq.Workplane().add(cq.Solid.makeLoft(wires, True))


def build_shell(side="left"):
    cx, cy = TOP_W / 2, -TOP_H / 2
    outer = cq.Workplane().add(cq.Solid.makeLoft([
        rrect_wire(BASE_W, BASE_H, R_TOP + DRAFT, cx, cy, 0.0),
        rrect_wire(TOP_W, TOP_H, R_TOP, cx, cy, H_MAX + 0.01)]))
    body = outer.intersect(height_profile())

    # hollow from below: cavity follows the top surface 0.8 mm below it
    cav_w, cav_h = TOP_W - 2 * WALL_IN, TOP_H - 2 * WALL_IN
    cavity = prism(WALL_IN, WALL_IN, cav_w, cav_h, -1, H_MAX + 2, R_TOP - WALL_IN).intersect(height_profile(SKIN))
    rabbet = prism(-RABBET_W + WALL_IN, -RABBET_W + WALL_IN, cav_w + 2 * RABBET_W, cav_h + 2 * RABBET_W,
                   -1, 1 + PLATE_T, R_TOP - WALL_IN + RABBET_W)
    body = body.cut(cavity).cut(rabbet)

    # divider rib and bosses (grown down from the skin, trimmed to the outer body)
    inner = []
    inner.append(prism(DIV_X, WALL_IN, DIV_W, cav_h, RIB_BOTTOM, H_MAX))
    for x, y, d, _ in BOSSES:
        inner.append(cyl(x, y, d, PCB_TOP, H_MAX))
    for s in inner:
        body = body.union(s.intersect(outer).intersect(height_profile()))

    # key window, tapped holes, USB-C, power switch slot, reset pin-hole
    body = body.cut(prism(BORDER, BORDER, WIN_W, WIN_H, -1, H_MAX + 2, 1.0))
    for x, y, d, depth in BOSSES:
        body = body.cut(cyl(x, y, TAP_DRILL, PCB_TOP - 0.1, depth + 0.1))
        body = body.cut(cq.Workplane("XY").workplane(offset=PCB_TOP).center(x, -y)
                        .circle(1.2).workplane(offset=0.4).circle(TAP_DRILL / 2).loft())  # 2.4 x 90 deg [D]
    body = body.cut(prism(USB_X - USB_W / 2, TOP_H - 3, USB_W, 6, USB_Z0, USB_Z1 - USB_Z0, 1.2))
    body = body.cut(prism(TOP_W - 3, PWR_Y - PWR_L / 2, 6, PWR_L, -1, PWR_Z1 + 1))
    body = body.cut(cyl(RESET_PIN[0], RESET_PIN[1], RESET_PIN[2], 0, H_MAX + 1))
    if side == "right":
        body = body.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return body


def build_plate(side="left"):
    gap = 0.05
    w = TOP_W - 2 * WALL_IN + 2 * RABBET_W - 2 * gap
    h = TOP_H - 2 * WALL_IN + 2 * RABBET_W - 2 * gap
    x0 = WALL_IN - RABBET_W + gap
    plate = prism(x0, x0, w, h, 0, PLATE_T, R_TOP - WALL_IN + RABBET_W - gap)
    for x, y, _, _ in BOSSES:
        plate = plate.cut(cyl(x, y, 2.2, -1, 3))
        plate = plate.cut(cyl(x, y, 4.2, -1, 1.5))        # counterbore 0.5 deep for thin-head M2 screws
    # relief under the mid-mount USB-C receptacle (it hangs ~1.1 mm below the nice!nano)
    plate = plate.cut(prism(USB_X - 5.75, TOP_H - 9.5, 11.5, 9, PLATE_T - 0.4, 1, 0.6))
    if side == "right":
        plate = plate.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return plate


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for side in ("left", "right"):
        for name, part in (("shell", build_shell(side)), ("plate", build_plate(side))):
            base = os.path.join(out, f"bayleaf-{name}-{side}")
            cq.exporters.export(part, base + ".step")
            cq.exporters.export(part, base + ".stl", tolerance=0.02, angularTolerance=0.1)
            bb = part.val().BoundingBox()
            vol = part.val().Volume() / 1000
            print(f"{name}-{side}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm, "
                  f"{vol:.2f} cm3 = {vol * 2.70:.0f} g (6061)")


if __name__ == "__main__":
    main()
