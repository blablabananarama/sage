#!/usr/bin/env python3
"""Bayleaf case (CadQuery): one-piece top shell + bottom plate, per half.

Plan view from the original's case drawing ("bayleaf-case-MK5_L"); the top surface from the shape
sent through the Bayleaf Case Sketchpad (docs/case-sketchpad-shape.json):

  * two flat levels - LOW (3.2 mm, the rim around the keys, about at the keycap underside) and
    HIGH (5.0 mm, the tallest point: a plateau over the controller at the back of the inner end)
  * the plateau is a rectangle (x >= 96.5, y <= 76 mm) whose two inner edges blend into the rim
    through soft S-bends 16.5 mm wide (10-90 %), i.e. a separable Gaussian-blurred step
  * the controller bay is closed by the shell itself (0.8 mm roof); USB-C exits the back wall
  * the bottom plate (0.8 mm) screws into 7 posts and clamps the PCB
  * two wall styles: drafted walls [D] (default) or straight walls with a 45 deg chamfer on the top edge

    /opt/cq/bin/python case.py        # -> out/bayleaf-{shell,shell-*-chamfer,plate}-{left,right}.{step,stl}

Coordinates ("shell coords"): x to the right, y toward the typist (front), origin at the back-left
corner of the 137 x 94.4 top outline. CadQuery Y = -y. Right half = mirror image.
Values from the drawing are marked [D], from the sketchpad [S]; the rest is derived.
"""
import math
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
DIV_X = BORDER + WIN_W         # 107.2 divider [D]
DIV_W = 2.0                    # [D]
BAY_X0, BAY_X1 = DIV_X + DIV_W, DIV_X + DIV_W + 27.0   # 109.2 .. 136.2 [D]
BAY_CX = (BAY_X0 + BAY_X1) / 2                          # 122.7

# ---------------------------------------------------------------- heights
H_LOW, H_HIGH = 3.2, 5.0       # [S] rim level / plateau level (tallest point)
PLATEAU_X0, PLATEAU_Y1 = 96.5, 76.0   # [S] plateau = x >= X0 and y <= Y1 (square corners)
BEND = 16.5                    # [S] 10-90 % width of each S-bend
SIGMA = BEND / 2.563           # Gaussian sigma giving that width
SKIN = 0.8                     # top skin (rim and roof over the controller)
WALL_IN = 0.8                  # inner cavity inset from the top outline (gives the 27 mm bay [D])
RABBET_W, PLATE_T = 1.0, 0.8   # [D] bottom-plate rabbet: leaves a 1 mm wall at the base
WIN_R = 2.0                    # [S] rounded inside corners of the key window
CHAMFER = 1.0                  # "chamfer" variant: straight walls + 45 deg chamfer on the outer top edge

# ---------------------------------------------------------------- stack-up inside
PCB_OFF = WALL_IN + 0.25       # PCB origin in shell coords (0.25 mm clearance to the cavity wall)
PCB_TOP = PLATE_T + 0.8        # 1.6; nice!nano top ~4.0 (only ~2.4 mm of its 3.2 mm sits above the PCB)
RIB_BOTTOM = PCB_TOP + 1.2     # divider stops above the SMD parts

# ---------------------------------------------------------------- posts (x, y, diameter)
# [D] positions: key-frame corners, the pair flanking the USB-C at the back (19.039 apart in the
# drawing - moved out to the bay corners here, or they would sit on the nice!nano's pins), the
# divider middle, and the pair at the front of the bay (18.037 apart).
BOSSES = [
    (2.9, 3.5, 6.0),
    (2.9, TOP_H - 3.5, 6.0),
    (BAY_X0 + 2.0, 3.5, 4.0),
    (BAY_X1 - 2.25, 3.5, 4.0),
    (109.5, TOP_H / 2, 6.0),
    (BAY_CX - 18.037 / 2, TOP_H - 3.5, 6.0),
    (BAY_CX + 18.037 / 2, TOP_H - 3.5, 6.0),
]
THREAD_MAX = 2.0
TAP_DRILL = 1.6
MIN_TOP_SKIN = 0.5             # material left above a blind thread

# ---------------------------------------------------------------- openings (from the PCB layout)
USB_X = BAY_CX - 0.3           # nice!nano (0.3 mm toward the divider), USB-C facing the back
USB_ZC = PCB_TOP + 0.5         # mid-mount receptacle: centred on the nice!nano's 1 mm board
USB_W, USB_H = 9.7, 3.9        # obround opening = 8.94 x 3.26 receptacle + ~0.35 all round (z 0.15..4.05)
RESET_PIN = (PCB_OFF + 110.15, PCB_OFF + 22.0, 1.6)   # paper-clip hole through the roof


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


def usb_opening(y0, depth):
    """Obround (stadium) USB-C opening around the receptacle, through the back wall from y0 toward the front."""
    return (cq.Workplane("XZ", origin=(0, -y0, 0)).center(USB_X, USB_ZC)
            .slot2D(USB_W, USB_H).extrude(depth))


def _phi(t):
    return 0.5 * (1 + math.erf(t / math.sqrt(2)))


def top_z(x, y):
    """Top-surface height: LOW + (HIGH - LOW) * blurred plateau mask (separable, square corners)."""
    return H_LOW + (H_HIGH - H_LOW) * _phi((x - PLATEAU_X0) / SIGMA) * _phi((PLATEAU_Y1 - y) / SIGMA)


def thread_depth(x, y):
    """Blind M2 thread from the PCB plane, as deep as the surface above allows (max 2 mm)."""
    return round(min(THREAD_MAX, top_z(x, y) - PCB_TOP - MIN_TOP_SKIN), 1)


def height_field(fn, xs, ys):
    """Solid under z = fn(x, y): a ruled loft (along x) through y-z spline sections."""
    def section(x):
        pl = cq.Plane(origin=(x, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
        pts = [(-y, fn(x, y) + 1e-5 * i) for i, y in enumerate(ys)]   # tiny tilt: never collinear
        wp = cq.Workplane(pl).moveTo(-ys[0], -2).lineTo(*pts[0]).spline(pts[1:], includeCurrent=True) \
            .lineTo(-ys[-1], -2).close()
        return wp.wires().val()
    return cq.Workplane().add(cq.Solid.makeLoft([section(x) for x in xs], True))


def height_profile(dz=0.0):
    """Solid whose top is the shell's top surface (lowered by dz)."""
    y_bend = [PLATEAU_Y1 - 4 * SIGMA + k * SIGMA / 2 for k in range(17)]
    ys = [-10.0 + 5 * k for k in range(int((y_bend[0] + 10) // 5))] + y_bend + [TOP_H + 5, TOP_H + 10]
    xs = [-10.0] + [PLATEAU_X0 - 4 * SIGMA + k * SIGMA / 2 for k in range(17)] + [BASE_W + 10]
    return height_field(lambda x, y: top_z(x, y) - dz, xs, ys)


def outer_body(style="draft"):
    """Outer walls: "draft" = drafted walls (base 1.19 mm larger per side [D]); "chamfer" = straight walls
    on the base outline."""
    cx, cy = TOP_W / 2, -TOP_H / 2
    top_w, top_h, top_r = (TOP_W, TOP_H, R_TOP) if style == "draft" else (BASE_W, BASE_H, R_TOP + DRAFT)
    return cq.Workplane().add(cq.Solid.makeLoft([
        rrect_wire(BASE_W, BASE_H, R_TOP + DRAFT, cx, cy, 0.0),
        rrect_wire(top_w, top_h, top_r, cx, cy, H_HIGH + 0.01)]))


def inward_dist(x, y):
    """Distance inside the base outline (rounded rectangle), negative outside; shell coords."""
    x0, y0, x1, y1, r = -DRAFT, -DRAFT, TOP_W + DRAFT, TOP_H + DRAFT, R_TOP + DRAFT
    cx, cy = min(max(x, x0 + r), x1 - r), min(max(y, y0 + r), y1 - r)
    if (cx, cy) != (x, y) and not (x0 + r <= x <= x1 - r or y0 + r <= y <= y1 - r):
        return r - math.hypot(x - cx, y - cy)          # corner quadrant
    return min(x - x0, x1 - x, y - y0, y1 - y)


def chamfer_field():
    """Solid below z = top_z - CHAMFER + inward distance: intersecting with it cuts a 45 deg chamfer of
    size CHAMFER along the outer top edge that follows the blended surface (OCC can't chamfer that edge
    directly). Sections are dense within reach of the walls and in the bends."""
    def near(lo, hi, step=0.5):
        return [lo + step * k for k in range(int(round((hi - lo) / step)) + 1)]
    xb = [PLATEAU_X0 - 4 * SIGMA + k * SIGMA / 2 for k in range(17)]
    xs = near(-3.0, R_TOP + 3.0) + [x for x in xb if R_TOP + 3.5 < x < TOP_W - R_TOP - 3.5] + \
        near(TOP_W - R_TOP - 3.0, TOP_W + 3.0)
    yb = [PLATEAU_Y1 - 4 * SIGMA + k * SIGMA / 2 for k in range(17)]
    ys = near(-3.0, R_TOP + 3.0) + [y for y in [10.0 + 5 * k for k in range(12)] + yb
                                     if R_TOP + 3.5 < y < TOP_H - R_TOP - 3.5] + near(TOP_H - R_TOP - 3.0, TOP_H + 3.0)
    return height_field(lambda x, y: top_z(x, y) - CHAMFER + min(inward_dist(x, y), 3.0), xs, sorted(set(ys)))


def build_shell(side="left", style="draft"):
    outer = outer_body(style)
    body = outer.intersect(height_profile())
    if style == "chamfer":
        body = body.intersect(chamfer_field())

    cav_w, cav_h = TOP_W - 2 * WALL_IN, TOP_H - 2 * WALL_IN
    # hollow from below, following the top surface 0.8 mm under it (rim and controller roof)
    cavity = prism(WALL_IN, WALL_IN, cav_w, cav_h, -1, H_HIGH + 2, R_TOP - WALL_IN).intersect(height_profile(SKIN))
    rabbet = prism(WALL_IN - RABBET_W, WALL_IN - RABBET_W, cav_w + 2 * RABBET_W, cav_h + 2 * RABBET_W,
                   -1, 1 + PLATE_T, R_TOP - WALL_IN + RABBET_W)
    body = body.cut(cavity).cut(rabbet)

    # divider rib and posts, grown down to the PCB (divider stops above the SMD parts)
    parts = [prism(DIV_X, WALL_IN, DIV_W, cav_h, RIB_BOTTOM, H_HIGH)]
    parts += [cyl(x, y, d, PCB_TOP, H_HIGH) for x, y, d in BOSSES]
    for p in parts:
        body = body.union(p.intersect(outer).intersect(height_profile()))

    body = body.cut(prism(BORDER, BORDER, WIN_W, WIN_H, -1, H_HIGH + 2, WIN_R))         # key window
    for x, y, _ in BOSSES:
        body = body.cut(cyl(x, y, TAP_DRILL, PCB_TOP - 0.1, thread_depth(x, y) + 0.1))
        body = body.cut(cq.Workplane("XY").workplane(offset=PCB_TOP).center(x, -y)
                        .circle(1.2).workplane(offset=0.4).circle(TAP_DRILL / 2).loft())  # 2.4 x 90 deg [D]
    body = body.cut(usb_opening(-4, 4 + WALL_IN))                                        # USB-C, back wall
    body = body.cut(cyl(RESET_PIN[0], RESET_PIN[1], RESET_PIN[2], 0, H_HIGH + 1))        # reset pin-hole
    if side == "right":
        body = body.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return body


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
    plate = plate.cut(prism(USB_X - 5.75, 0.5, 11.5, 9, PLATE_T - 0.4, 1, 0.6))
    plate = plate.cut(usb_opening(-4, 5))    # the opening's lower curve continues into the plate edge
    if side == "right":
        plate = plate.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return plate


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for x, y, d in BOSSES:
        print(f"post ({x:.2f}, {y:.2f}) dia {d:g}: M2 thread {thread_depth(x, y)} mm deep")
    for side in ("left", "right"):
        for name, part in ((f"shell-{side}", build_shell(side)),
                           (f"shell-{side}-chamfer", build_shell(side, "chamfer")),
                           (f"plate-{side}", build_plate(side))):
            base = os.path.join(out, f"bayleaf-{name}")
            cq.exporters.export(part, base + ".step")
            cq.exporters.export(part, base + ".stl", tolerance=0.02, angularTolerance=0.1)
            bb = part.val().BoundingBox()
            zmax = max(p.z for p in part.val().tessellate(0.01)[0])   # OCC's box is padded
            vol = part.val().Volume() / 1000
            print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} mm footprint, {zmax:.2f} mm tall, "
                  f"{vol:.2f} cm3 = {vol * 2.70:.0f} g (6061)")


if __name__ == "__main__":
    main()
