#!/usr/bin/env python3
"""Bayleaf case (CadQuery): one-piece top shell + bottom plate, per half.

Plan view from the original's case drawing ("bayleaf-case-MK5_L"); the top surface from the shape
sent through the Bayleaf Case Sketchpad (docs/case-sketchpad-shape.json):

  * two flat levels - LOW (3.2 mm, the rim around the keys, about at the keycap underside) and
    HIGH (5.0 mm, the tallest point: a plateau over the controller at the back of the inner end)
  * the plateau is a rectangle (x >= 96.5, y <= 76 mm) whose two inner edges blend into the rim
    through soft S-bends 16.5 mm wide (10-90 %), i.e. a separable Gaussian-blurred step
  * the controller bay is closed by the shell itself (0.8 mm roof); USB-C exits the back wall
  * the bottom plate (0.8 mm FR4, made as a copper-free PCB) screws into 7 posts and clamps the PCB
  * two wall styles: drafted walls [D] (default) or straight walls with a 45 deg chamfer on the top edge

    /opt/cq/bin/python case.py        # -> out/bayleaf-{shell,shell-*-chamfer,shell-*-round,shell-*-corner,shell-*-corner2,plate}-{left,right}.{step,stl}

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
MILL_R = 1.65                  # smallest inside corner radius (SendCutSend: >= 1/16" = 1.59 mm)
CHAMFER = 0.5                  # "chamfer" variant: straight walls + 45 deg chamfer on the outer top edge
ROUND_OUT, ROUND_WIN = 1.5, 0.8  # "round" variant: straight walls, outer top edge / key-window edge rounded over
CORNER_CUT, CORNER_RT, CORNER_RB = 2.5, 1.0, 0.5   # "corner" variant: 45 deg corner cut (legs), and rounds on
                                                   # the top / bottom edge of each corner face only

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
    if style in ("corner", "corner2"):   # straight walls, sharp plan corners (cut or rounded later)
        return prism(-DRAFT, -DRAFT, BASE_W, BASE_H, 0, H_HIGH + 0.01)
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


def _grow(w, d):
    """Faces bounded by wire w offset outward by d (inward if d < 0); [] if it vanishes."""
    area = cq.Face.makeFromWires(w).Area()
    for sign in (1, -1):
        try:
            fs = [cq.Face.makeFromWires(x) for x in w.offset2D(sign * d, "arc")]
        except Exception:
            fs = []
        a = sum(f.Area() for f in fs)
        if (d > 0 and a > area) or (d < 0 and fs and a < area):
            return fs
    return []


def _minus(faces, holes):
    out = []
    for f in faces:
        for h in holes:
            f = f.cut(h)
        out += [x for x in f.Faces() if x.Area() > 1e-6]
    return out


def opening(faces, r):
    """Morphological opening (erode, then dilate by r): the part of a planar region a cutter of radius r
    can reach. Inside corners come out rounded to r, and gaps narrower than 2r are left as material."""
    eroded = []
    for f in faces:
        eroded += _minus(_grow(f.outerWire(), -r), [g for h in f.innerWires() for g in _grow(h, r)])
    out = []
    for f in eroded:
        out += _minus(_grow(f.outerWire(), r), [g for h in f.innerWires() for g in _grow(h, -r)])
    u = out[0]
    for f in out[1:]:
        u = u.fuse(f)
    return u.clean().Faces()


def pocket_outline(with_divider):
    """Plan-view outline of the underside pocket at one level: the cavity minus the posts (and the divider
    above its underside), opened for the cutter."""
    cav_w, cav_h = TOP_W - 2 * WALL_IN, TOP_H - 2 * WALL_IN
    s = prism(WALL_IN, WALL_IN, cav_w, cav_h, 0, 1, R_TOP - WALL_IN)
    for x, y, d in BOSSES:
        s = s.cut(cyl(x, y, d, -1, 3))
    if with_divider:
        s = s.cut(prism(DIV_X, -1, DIV_W, TOP_H + 2, -1, 3))
    return opening(s.faces("<Z").vals(), MILL_R)


def window_dist(x, y):
    """Signed distance to the key window (rounded rectangle): positive outside it (on the frame)."""
    x0, y0, x1, y1, r = BORDER, BORDER, BORDER + WIN_W, BORDER + WIN_H, WIN_R
    dx, dy = max(x0 + r - x, x - (x1 - r)), max(y0 + r - y, y - (y1 - r))
    return math.hypot(max(dx, 0), max(dy, 0)) + min(max(dx, dy), 0) - r


def _roundover(d, r):
    """Height offset of a quarter-round of radius r on an edge, d = distance in from the edge."""
    if d <= 0:
        return -r + d
    if d < r:
        return -r + math.sqrt(r * r - (r - d) ** 2)
    return min((d - r) ** 2 / r, 3.0)


def round_field():
    """Solid under the top surface with both top edges rounded over: the outer edge (ROUND_OUT) and the
    key-window edge (ROUND_WIN). Like chamfer_field(), a height field that follows the blended surface;
    sections are dense (0.15 mm) where the rounds are."""
    def near(lo, hi, step=0.15):
        return [lo + step * k for k in range(int(round((hi - lo) / step)) + 1)]

    def coarse(lo, hi, bend):
        return [v for v in [lo + 5 * k for k in range(int((hi - lo) / 5) + 1)] + bend if lo < v < hi]
    xb = [PLATEAU_X0 - 4 * SIGMA + k * SIGMA / 2 for k in range(17)]
    yb = [PLATEAU_Y1 - 4 * SIGMA + k * SIGMA / 2 for k in range(17)]
    ro, rw = ROUND_OUT + 0.4, ROUND_WIN + 0.4
    xw0, xw1, yw0, yw1 = BORDER, BORDER + WIN_W, BORDER, BORDER + WIN_H
    rc = R_TOP + DRAFT + ro          # the outline's plan-view corners curve in this far: sample them densely
    xs = (near(-DRAFT - 1.5, -DRAFT + rc) + near(xw0 - rw, xw0 + 0.3) + coarse(xw0 + 1, xw1 - 1, xb)
          + near(xw1 - 0.3, xw1 + rw) + coarse(xw1 + rw + 1, TOP_W + DRAFT - rc - 1, xb)
          + near(TOP_W + DRAFT - rc, TOP_W + DRAFT + 1.5))
    ys = (near(-DRAFT - 1.5, -DRAFT + rc) + near(yw0 - rw, yw0 + 0.3) + coarse(yw0 + 1, yw1 - 1, yb)
          + near(yw1 - 0.3, yw1 + rw) + near(TOP_H + DRAFT - rc, TOP_H + DRAFT + 1.5))
    def spaced(vals, gap=0.1):                     # near-coincident sections break the booleans
        out = []
        for v in sorted(vals):
            if not out or v - out[-1] >= gap:
                out.append(v)
        return out
    xs, ys = spaced(xs), spaced(ys)

    def fn(x, y):
        t = top_z(x, y)
        # clamp: inside the key window (cut away anyway) the field must stay above the section's floor
        return max(t + min(_roundover(inward_dist(x, y), ROUND_OUT), _roundover(window_dist(x, y), ROUND_WIN)),
                   -0.5)
    return height_field(fn, xs, ys)


def corner_cutter(x, y, sx, sy):
    """Material to remove at one outer corner (shell coords x, y; sx, sy = outward direction, +-1): the
    corner is cut at 45 deg (CORNER_CUT legs), then only the new face's top and bottom edges are rounded.
    Built on a local block at the corner's (flat) height and subtracted from a box around the corner."""
    L, n = CORNER_CUT, 5.0          # n: working box, small enough to stay clear of the plateau slope
    h = top_z(x - sx * L / 2, y - sy * L / 2)
    keep = cq.Workplane().box(n, n, h, centered=False).edges("|Z").edges(">X and >Y").chamfer(L)
    face = keep.faces(cq.selectors.DirectionMinMaxSelector(cq.Vector(1, 1, 0), True)).val()
    keep = keep.newObject([e for e in face.Edges() if abs(e.Center().z - h) < 1e-6]).fillet(CORNER_RT)
    bottom = [e for e in keep.val().Edges()
              if abs(e.Center().z) < 1e-6 and abs(e.Center().x + e.Center().y - (2 * n - L)) < 0.5]
    keep = keep.newObject(bottom).fillet(CORNER_RB)
    region = cq.Workplane().box(n, n, h + 4, centered=False).translate((0, 0, -2))
    cut = region.cut(keep).val()
    # local corner (n, n) points to +x/+y; mirror into the corner's direction (CadQuery Y = -y)
    if sx < 0:
        cut = cut.mirror("YZ")
    if -sy < 0:
        cut = cut.mirror("XZ")
    return cq.Workplane().add(cut.translate(cq.Vector(x - sx * n, -y + sy * n, 0)))


def build_shell(side="left", style="draft"):
    outer = outer_body(style)
    body = outer.intersect(height_profile())
    if style == "chamfer":
        body = body.intersect(chamfer_field())
    elif style == "round":
        body = body.intersect(round_field())
    elif style in ("corner", "corner2"):
        # "corner": all four corners cut; "corner2": only the back corner by the USB-C and the opposite
        # front corner, the other two get the usual R4.19 plan radius
        for x, sx in ((-DRAFT, -1), (TOP_W + DRAFT, 1)):
            for y, sy in ((-DRAFT, -1), (TOP_H + DRAFT, 1)):
                if style == "corner" or (sx, sy) in ((1, -1), (-1, 1)):
                    body = body.cut(corner_cutter(x, y, sx, sy))
                else:
                    r = R_TOP + DRAFT
                    sq = prism(x - (r if sx > 0 else 0) - (1 if sx < 0 else 0), y - (r if sy > 0 else 0) - (1 if sy < 0 else 0),
                               r + 1, r + 1, -1, H_HIGH + 2)
                    body = body.cut(sq.cut(cyl(x - sx * r, y - sy * r, 2 * r, -2, H_HIGH + 4)))

    cav_w, cav_h = TOP_W - 2 * WALL_IN, TOP_H - 2 * WALL_IN
    rabbet = prism(WALL_IN - RABBET_W, WALL_IN - RABBET_W, cav_w + 2 * RABBET_W, cav_h + 2 * RABBET_W,
                   -1, 1 + PLATE_T, R_TOP - WALL_IN + RABBET_W)
    body = body.cut(rabbet)
    # Hollow from below, following the top surface 0.8 mm under it (rim and controller roof), in three
    # layers: the full cavity under the PCB plane; around the posts up to the divider's underside; around
    # the posts and the divider above it. The posts and the divider are what the pockets leave standing.
    # Each layer's outline is rounded for a MILL_R cutter, so no inside corner is sharper than the tool.
    ceiling = height_profile(SKIN)
    for z0, z1, with_div in ((-1, PCB_TOP, None), (PCB_TOP, RIB_BOTTOM, False), (RIB_BOTTOM, H_HIGH + 1, True)):
        if with_div is None:
            layer = prism(WALL_IN, WALL_IN, cav_w, cav_h, z0, z1 - z0, R_TOP - WALL_IN)
        else:
            layer = cq.Workplane().add([cq.Solid.extrudeLinear(f.translate(cq.Vector(0, 0, z0)),
                                                                 cq.Vector(0, 0, z1 - z0))
                                        for f in pocket_outline(with_div)]).combine()
        body = body.cut(layer.intersect(ceiling))

    body = body.cut(prism(BORDER, BORDER, WIN_W, WIN_H, -1, H_HIGH + 2, WIN_R))         # key window
    for x, y, _ in BOSSES:
        body = body.cut(cyl(x, y, TAP_DRILL, PCB_TOP - 0.1, thread_depth(x, y) + 0.1))
        body = body.cut(cq.Workplane("XY").workplane(offset=PCB_TOP).center(x, -y)
                        .circle(1.2).workplane(offset=0.4).circle(TAP_DRILL / 2).loft())  # 2.4 x 90 deg [D]
    body = body.cut(usb_opening(-4, 4 + WALL_IN))                                        # USB-C, back wall
    if side == "right":
        body = body.mirror("YZ", basePointVector=(TOP_W / 2, 0, 0))
    return body


def build_plate(side="left"):
    """The bottom plate is a copper-free 0.8 mm FR4 board (radio-transparent), generated with the PCBs by
    hardware/pcb/generate_pcb.py. Its outline fills the rabbet (0.05 mm gap); here it is only brought into
    shell coords for the STEP/STL and the renders. KiCad's STEP export ignores the 0.8 mm thickness, so the
    plate is re-extruded from its bottom face."""
    step = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb", "fab", f"plate-{side}",
                        f"bayleaf-plate-{side}.step")
    face = cq.importers.importStep(step).faces("<Z").val()
    plate = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, PLATE_T))
    return cq.Workplane().add(plate.translate(cq.Vector(PCB_OFF, -PCB_OFF, -face.Center().z)))


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for x, y, d in BOSSES:
        print(f"post ({x:.2f}, {y:.2f}) dia {d:g}: M2 thread {thread_depth(x, y)} mm deep")
    for side in ("left", "right"):
        for name, part in ((f"shell-{side}", build_shell(side)),
                           (f"shell-{side}-chamfer", build_shell(side, "chamfer")),
                           (f"shell-{side}-round", build_shell(side, "round")),
                           (f"shell-{side}-corner", build_shell(side, "corner")),
                           (f"shell-{side}-corner2", build_shell(side, "corner2")),
                           (f"plate-{side}", build_plate(side))):
            base = os.path.join(out, f"bayleaf-{name}")
            cq.exporters.export(part, base + ".step")
            cq.exporters.export(part, base + ".stl", tolerance=0.02, angularTolerance=0.1)
            bb = part.val().BoundingBox()
            zmax = max(p.z for p in part.val().tessellate(0.01)[0])   # OCC's box is padded
            vol = part.val().Volume() / 1000
            print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} mm footprint, {zmax:.2f} mm tall, "
                  f"{vol:.2f} cm3 = " + (f"{vol * 1.85:.0f} g (FR4)" if name.startswith("plate") else
                                         f"{vol * 2.70:.0f} g (6061)"))


if __name__ == "__main__":
    main()
