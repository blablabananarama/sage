#!/usr/bin/env python3
"""Bayleaf case (CadQuery): top shell + controller lid + bottom plate, per half.

Follows the original's case drawing ("bayleaf-case-MK5_L") for the plan view and the build photos for
the heights ("tallest part of the keyboard is only 5 mm"):

  * top shell   - silver frame around a 103 x 86 key window, 3.8 mm tall over the keys; toward the
                  controller end it curves up to 4.1 mm. The controller bay (27 mm, behind a 2 mm
                  divider) is open on top; 7 M2 posts underneath clamp the PCB to the bottom plate.
  * lid         - separate 0.8 mm plate (anodised in a contrasting colour on the original) that covers
                  the controller bay flush with the outer edges; its top is the tallest point, 5.0 mm.
                  Held by a 0.1 mm double-sided tape on the wall tops and posts; reset pin-hole in it.
  * bottom plate - 0.8 mm, flush in a 1 x 0.8 mm rabbet, screwed into the posts.

    /opt/cq/bin/python case.py        # -> out/bayleaf-{shell,lid,plate}-{left,right}.{step,stl}

Coordinates ("shell coords"): x to the right, y toward the typist (front), origin at the back-left
corner of the 137 x 94.4 top outline. CadQuery Y = -y. Right half = mirror image.
Values from the drawing are marked [D], from the photos [P]; the rest is derived.
"""
import os

import cadquery as cq

# ---------------------------------------------------------------- outline
TOP_W = 137.0                  # [D] top outline width
BORDER = 4.2                   # [D] key-window offset from the edge (assumed the same on all sides)
WIN_W, WIN_H = 103.0, 86.0     # [D] key window
TOP_H = WIN_H + 2 * BORDER     # 94.4
DRAFT = 1.19                   # [D] base outline is 1.19 larger per side (drafted walls)
BASE_W, BASE_H = TOP_W + 2 * DRAFT, TOP_H + 2 * DRAFT   # 139.38 x 96.78
R_TOP = 3.0
DIV_X = BORDER + WIN_W         # 107.2 divider / lid edge [D]
DIV_W = 2.0                    # [D]
BAY_X0, BAY_X1 = DIV_X + DIV_W, DIV_X + DIV_W + 27.0   # 109.2 .. 136.2 [D]
BAY_CX = (BAY_X0 + BAY_X1) / 2                          # 122.7

# ---------------------------------------------------------------- heights
TOTAL_H = 5.0                  # [P] tallest point = top of the lid
LID_T = 0.8
TAPE_T = 0.1                   # double-sided tape under the lid
H_BAY = TOTAL_H - LID_T - TAPE_T   # 4.1 shell wall height around the controller bay
# Two soft bends shape the top ([D] side views + section A, [P] photos):
#  - along y: the frame is H_BAY at the back and curves down to H_FRONT along the front edge
#  - along x: toward the controller end that front dip fades out again, so the front face rises
#    in an S-curve to meet the lid
# Heights are the drawing's 3.8 / 6.2 proportions scaled to the photographed 5 mm total.
H_FRONT = 3.1                  # frame at the front edge of the key area
FRONT_RAMP = 24.0              # [D] depth of the front bend
RAMP_X = (72.0, 101.0)         # [D] section A: x range over which the front dip fades out
EDGE_R = 0.5                   # soft outer top edge (drawing: 0.61 chamfer)
SKIN = 0.8                     # frame thickness over the key area
WALL_IN = 0.8                  # inner cavity inset from the top outline (gives the 27 mm bay [D])
RABBET_W, PLATE_T = 1.0, 0.8   # [D] bottom-plate rabbet: leaves a 1 mm wall at the base

# ---------------------------------------------------------------- stack-up inside
PCB_OFF = WALL_IN + 0.25       # PCB origin in shell coords (0.25 mm clearance to the cavity wall)
PCB_TOP = PLATE_T + 0.8        # 1.6; nice!nano top ~4.0 (only ~2.4 mm of its 3.2 mm sits above the PCB)
RIB_BOTTOM = PCB_TOP + 1.2     # divider stops above the SMD parts

# ---------------------------------------------------------------- posts (x, y, diameter)
# [D] positions: key-frame corners, back pair 18.037 apart, divider middle, front pair. The front pair
# (19.039 apart in the drawing) would sit on the nice!nano's pin rows, so it moves to the bay corners.
# Thread: M2x0.4 blind from below, 2 mm deep where the surface allows (see thread_depth()).
BOSSES = [
    (2.9, 3.5, 6.0),
    (2.9, TOP_H - 3.5, 6.0),
    (BAY_CX - 18.037 / 2, 3.5, 6.0),
    (BAY_CX + 18.037 / 2, 3.5, 6.0),
    (109.5, TOP_H / 2, 6.0),
    (BAY_X0 + 2.25, TOP_H - 3.5, 4.0),
    (BAY_X1 - 2.25, TOP_H - 3.5, 4.0),
]
THREAD_MAX = 2.0
TAP_DRILL = 1.6
MIN_TOP_SKIN = 0.5             # material left above a blind thread

# ---------------------------------------------------------------- openings (from the PCB layout)
USB_X = BAY_CX                 # nice!nano centred in the bay, USB-C facing the front
USB_W = 10.0
PWR_Y = PCB_OFF + 53.9         # slide switch on the inner side wall
PWR_L, PWR_Z1 = 4.4, 3.4
RESET_PIN = (PCB_OFF + 116.5, PCB_OFF + 53.0, 1.6)   # paper-clip hole through the lid


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


def top_z(x, y):
    """Analytic top-surface height (same blend as height_profile)."""
    x0, x1 = RAMP_X
    t = 1 - smooth((x - x0) / (x1 - x0))
    return H_BAY - (H_BAY - H_FRONT) * t * smooth((y - (TOP_H - FRONT_RAMP)) / FRONT_RAMP)


def thread_depth(x, y):
    """Blind M2 thread from the PCB plane, as deep as the surface above allows (max 2 mm)."""
    return round(min(THREAD_MAX, top_z(x, y) - PCB_TOP - MIN_TOP_SKIN), 1)


def height_profile(dz=0.0):
    """Solid whose top is the shell's top surface (optionally lowered by dz): a loft through
    y-z sections whose front dip (H_BAY -> H_FRONT over FRONT_RAMP) fades out along x."""
    def section(x, t):
        t = max(t, 0.002)
        pl = cq.Plane(origin=(x, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
        y_r = TOP_H - FRONT_RAMP
        pts = [(-(y_r + FRONT_RAMP * k / 12), H_BAY - dz - (H_BAY - H_FRONT) * t * smooth(k / 12))
               for k in range(13)]
        wp = (cq.Workplane(pl).moveTo(10, -2).lineTo(10, H_BAY - dz).lineTo(-y_r, H_BAY - dz)
              .spline(pts[1:], includeCurrent=True).lineTo(-(TOP_H + 10), pts[-1][1])
              .lineTo(-(TOP_H + 10), -2).close())
        return wp.wires().val()
    x0, x1 = RAMP_X
    stations = [(-10, 1.0), (x0, 1.0)] + [(x0 + (x1 - x0) * k / 10, 1 - smooth(k / 10)) for k in range(1, 11)] \
        + [(BASE_W + 10, 0.0)]
    return cq.Workplane().add(cq.Solid.makeLoft([section(x, t) for x, t in stations], True))


def outer_body():
    cx, cy = TOP_W / 2, -TOP_H / 2
    return cq.Workplane().add(cq.Solid.makeLoft([
        rrect_wire(BASE_W, BASE_H, R_TOP + DRAFT, cx, cy, 0.0),
        rrect_wire(TOP_W, TOP_H, R_TOP, cx, cy, H_BAY + 0.01)]))


def build_shell(side="left"):
    outer = outer_body()
    body = outer.intersect(height_profile())
    try:                                   # soften the outer top edge
        top_edges = cq.selectors.BoxSelector((-5, -TOP_H - 5, 2.5), (TOP_W + 5, 5, H_BAY + 1))
        body = body.edges(top_edges).fillet(EDGE_R)
    except Exception as e:                 # OCC occasionally refuses on the blended surface
        print("edge fillet skipped:", e)

    cav_w, cav_h = TOP_W - 2 * WALL_IN, TOP_H - 2 * WALL_IN
    # under the key frame: hollow up to 0.8 mm below the top surface
    cavity = prism(WALL_IN, WALL_IN, cav_w, cav_h, -1, H_BAY + 2, R_TOP - WALL_IN).intersect(height_profile(SKIN))
    # controller bay: open to the top (the lid closes it)
    bay = prism(BAY_X0, WALL_IN, BAY_X1 - BAY_X0, cav_h, -1, H_BAY + 5, 1.0)
    rabbet = prism(WALL_IN - RABBET_W, WALL_IN - RABBET_W, cav_w + 2 * RABBET_W, cav_h + 2 * RABBET_W,
                   -1, 1 + PLATE_T, R_TOP - WALL_IN + RABBET_W)
    body = body.cut(cavity).cut(bay).cut(rabbet)

    # divider rib and posts, grown down to the PCB (divider stops above the SMD parts)
    parts = [prism(DIV_X, WALL_IN, DIV_W, cav_h, RIB_BOTTOM, H_BAY)]
    parts += [cyl(x, y, d, PCB_TOP, H_BAY) for x, y, d in BOSSES]
    for p in parts:
        body = body.union(p.intersect(outer).intersect(height_profile()))

    body = body.cut(prism(BORDER, BORDER, WIN_W, WIN_H, -1, H_BAY + 2, 1.0))            # key window
    for x, y, _ in BOSSES:
        body = body.cut(cyl(x, y, TAP_DRILL, PCB_TOP - 0.1, thread_depth(x, y) + 0.1))
        body = body.cut(cq.Workplane("XY").workplane(offset=PCB_TOP).center(x, -y)
                        .circle(1.2).workplane(offset=0.4).circle(TAP_DRILL / 2).loft())  # 2.4 x 90 deg [D]
    body = body.cut(prism(USB_X - USB_W / 2, TOP_H - 3, USB_W, 6, PLATE_T, H_BAY, 1.2))  # USB-C (U-slot)
    body = body.cut(prism(TOP_W - 3, PWR_Y - PWR_L / 2, 6, PWR_L, -1, PWR_Z1 + 1))       # power switch
    if side == "right":
        body = body.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return body


def build_lid(side="left"):
    """Covers x = DIV_X .. TOP_W, flush with the shell's top outline; square edge toward the keys."""
    z0 = H_BAY + TAPE_T
    top = prism(0, 0, TOP_W, TOP_H, z0, LID_T, R_TOP)            # same rounded outline as the shell
    lid = top.intersect(prism(DIV_X, -1, TOP_W, TOP_H + 2, z0 - 1, LID_T + 2))
    lid = lid.edges(">Z").chamfer(0.3)
    lid = lid.cut(cyl(RESET_PIN[0], RESET_PIN[1], RESET_PIN[2], z0 - 1, LID_T + 2))
    if side == "right":
        lid = lid.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return lid


def build_plate(side="left"):
    gap = 0.05
    w = TOP_W - 2 * WALL_IN + 2 * RABBET_W - 2 * gap
    h = TOP_H - 2 * WALL_IN + 2 * RABBET_W - 2 * gap
    x0 = WALL_IN - RABBET_W + gap
    plate = prism(x0, x0, w, h, 0, PLATE_T, R_TOP - WALL_IN + RABBET_W - gap)
    for x, y, _ in BOSSES:
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
    for x, y, d in BOSSES:
        print(f"post ({x:.2f}, {y:.2f}) dia {d:g}: M2 thread {thread_depth(x, y)} mm deep")
    for side in ("left", "right"):
        for name, part in (("shell", build_shell(side)), ("lid", build_lid(side)), ("plate", build_plate(side))):
            base = os.path.join(out, f"bayleaf-{name}-{side}")
            cq.exporters.export(part, base + ".step")
            cq.exporters.export(part, base + ".stl", tolerance=0.02, angularTolerance=0.1)
            bb = part.val().BoundingBox()
            vol = part.val().Volume() / 1000
            print(f"{name}-{side}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm (z {bb.zmin:.2f}..{bb.zmax:.2f}), "
                  f"{vol:.2f} cm3 = {vol * 2.70:.0f} g (6061)")


if __name__ == "__main__":
    main()
