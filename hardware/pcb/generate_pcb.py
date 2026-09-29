#!/usr/bin/env python3
"""Generate the Bayleaf PCBs (left + right half) with the KiCad 7 pcbnew API.

    /usr/bin/python3 generate_pcb.py            # place + autoroute + DRC + fab outputs
    /usr/bin/python3 generate_pcb.py --no-route # placement only

Every dimension of the board lives in this file, so the design is fully
reproducible from source. Routing is done with Freerouting (set FREEROUTING_JAR).

Coordinate system: KiCad (x right, y down), origin at the top-left corner of the
left-half PCB. The right half is the mirror image (x -> BOARD_W - x); footprints
are *not* flipped: everything but the reset button sits on the top side.

Also generates the FR4 bottom plates (bayleaf-plate-{left,right}.kicad_pcb): copper-free 0.8 mm
boards that close the case from below and let the radio out.
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "lib", "bayleaf.pretty")
KICAD_FP = "/usr/share/kicad/footprints"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/opt/tools/freerouting2.jar")  # v2.1.0

# ---------------------------------------------------------------- geometry (mm)
# The board drops into the MK5-style top shell (hardware/case/case.py): shell coords = PCB coords + 1.05.
# y grows toward the typist, so the "top" edge (y = 0) is the back of the keyboard.
BOARD_W, BOARD_H = 134.9, 92.3   # shell cavity 135.4 x 92.8 minus 0.25 mm clearance per side
CORNER_R = 2.0
ROWS, COLS = 5, 6
PITCH_X, PITCH_Y = 17.0, 17.0    # 103 x 86 mm key window = 5 x 17 + 16 mm cap + ~1 mm clearance
KEY_X0, KEY_Y0 = 12.15, 12.15    # first key centre (centred in the window)
DIODE_DX, DIODE_DY = -PITCH_X / 2, -1.0  # SOD-523 in the 0.95 mm gap left of each keycap

# Controller end: everything sits under the case's 5 mm plateau, which covers the back ~70 mm.
NANO_X, NANO_Y = 121.35, 0.4 + 33.3 / 2   # nice!nano centre, USB-C facing the back edge
NANO_ROT = 0
USB_NOTCH_W, USB_NOTCH_D = 10.5, 7.5    # room for the mid-mount receptacle (back edge)
BAT_CUT = (111.15, 34.9, 132.15, 65.9)   # x0, y0, x1, y1 - closed LiPo window (3.0 x 20 x 30 cell)
BAT_PADS = (132.75, 28.25)               # beside the nice!nano, "+" toward the back
RESET = (109.0, 22.0)                    # KMR2 on the *bottom*, pressed through a window in the plate
# Shell bosses (PCB coords): x, y, boss diameter. Each gets a 2.2 mm hole; M2 screws come up through
# the bottom plate and the PCB, so the bosses clamp the board. Must match BOSSES in case.py.
BOSSES = [(1.85, 2.45, 6.0), (1.85, 89.85, 6.0), (110.15, 2.45, 4.0), (132.90, 2.45, 4.0),
          (108.45, 46.15, 6.0), (112.63, 89.85, 6.0), (130.67, 89.85, 6.0)]

# Pro Micro pin label -> footprint pad number (see nice_nano_v2_flush.kicad_mod)
NANO_PADS = {n: i + 1 for i, n in enumerate(
    ["D1", "D0", "GND", "GND2", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9",
     "RAW", "GND3", "RST", "3V3", "D21", "D20", "D19", "D18", "D15", "D14", "D16", "D10"])}
# Matrix wiring - must match firmware/boards/shields/bayleaf/bayleaf_{left,right}.overlay.
# Each half uses the nice!nano pin column that faces its keys plus the far (front) end of the other
# column; the back-corner pins next to the USB-C (D0/D1, RAW side) and the NFC pins (D10/D16) stay
# unused.
MATRIX_PINS = {
    #          columns, physical left -> right                rows, back -> front
    "left":  (["D2", "D3", "D4", "D5", "D6", "D7"], ["D8", "D9", "D18", "D15", "D14"]),
    "right": (["D21", "D20", "D19", "D18", "D15", "D14"], ["D9", "D8", "D7", "D6", "D5"]),
}


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


class Builder:
    def __init__(self, side):
        self.side = side
        self.board = pcbnew.BOARD()
        self.nets = {}
        self._setup()

    # ------------------------------------------------------------ helpers
    def X(self, x):
        return BOARD_W - x if self.side == "right" else x

    def net(self, name):
        if name not in self.nets:
            n = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(n)
            self.nets[name] = n
        return self.nets[name]

    def place(self, lib, name, ref, x, y, rot=0, value=None, bottom=False):
        fp = pcbnew.FootprintLoad(lib, name)
        if fp is None:
            sys.exit(f"footprint {lib}:{name} not found")
        fp.SetReference(ref)
        fp.SetFPID(pcbnew.LIB_ID("bayleaf" if lib == LIB else os.path.basename(lib)[:-7], name))
        if name != "nice_nano_v2_flush":  # per-part refs would crowd the tiny gaps
            fp.Reference().SetVisible(False)
        if value:
            fp.SetValue(value)
        self.board.Add(fp)
        fp.SetPosition(pt(self.X(x), y))
        if self.side == "right" and rot in (90, -90):
            rot = -rot
        fp.SetOrientationDegrees(rot)
        if bottom:
            fp.Flip(fp.GetPosition(), False)
        return fp

    def connect(self, fp, pad_name, net_name):
        found = False
        for pad in fp.Pads():
            if pad.GetName() == str(pad_name):
                pad.SetNet(self.net(net_name))
                found = True
        assert found, (fp.GetReference(), pad_name)

    def seg(self, layer, a, b, width=0.1):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(*a))
        s.SetEnd(pt(*b))
        s.SetLayer(layer)
        s.SetWidth(mm(width))
        self.board.Add(s)

    def arc(self, center, start, angle_deg):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(pt(*center))
        s.SetStart(pt(*start))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(angle_deg, pcbnew.DEGREES_T), True)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        self.board.Add(s)

    def text(self, s, x, y, size=1.2, layer=pcbnew.F_SilkS):
        t = pcbnew.PCB_TEXT(self.board)
        t.SetText(s)
        t.SetPosition(pt(self.X(x), y))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(size * 0.15))
        if layer == pcbnew.B_SilkS:
            t.SetMirrored(True)
        self.board.Add(t)

    # ------------------------------------------------------------ board setup
    def _setup(self):
        b = self.board
        b.SetCopperLayerCount(2)
        ds = b.GetDesignSettings()
        ds.SetBoardThickness(mm(0.8))
        ds.m_TrackMinWidth = mm(0.15)
        ds.m_ViasMinSize = mm(0.5)
        ds.m_MinThroughDrill = mm(0.3)
        ds.m_MinClearance = mm(0.15)
        ds.m_CopperEdgeClearance = mm(0.25)
        ds.m_HoleClearance = mm(0.25)
        ds.m_HoleToHoleMin = mm(0.25)
        nc = ds.m_NetSettings.m_DefaultNetClass
        nc.SetClearance(mm(0.25))
        nc.SetTrackWidth(mm(0.25))
        nc.SetViaDiameter(mm(0.6))
        nc.SetViaDrill(mm(0.3))

    # ------------------------------------------------------------ outline
    def outline(self):
        # Outline traced clockwise in *left-half* coordinates, mirrored for the right half.
        ux0 = NANO_X - USB_NOTCH_W / 2
        ux1 = NANO_X + USB_NOTCH_W / 2
        r = CORNER_R
        W, H = BOARD_W, BOARD_H
        poly = [  # straight edges; rounded outer corners are added as arcs
            (r, 0), (ux0, 0), (ux0, USB_NOTCH_D), (ux1, USB_NOTCH_D), (ux1, 0), (W - r, 0),
            None,  # corner top-right
            (W, r), (W, H - r),
            None,  # corner bottom-right
            (W - r, H), (r, H),
            None,  # corner bottom-left
            (0, H - r), (0, r),
            None,  # corner top-left
        ]
        corners = {6: ((W - r, r), (W - r, 0)), 9: ((W - r, H - r), (W, H - r)),
                   12: ((r, H - r), (r, H)), 15: ((r, r), (0, r))}
        prev = None
        for i, p in enumerate(poly + [poly[0]]):
            if p is None:
                c, st = corners[i]
                self.arc((self.X(c[0]), c[1]), (self.X(st[0]), st[1]), 90 if self.side == "left" else -90)
                prev = None
                continue
            if prev is not None:
                self.seg(pcbnew.Edge_Cuts, (self.X(prev[0]), prev[1]), (self.X(p[0]), p[1]))
            prev = p
        bx0, by0, bx1, by1 = BAT_CUT
        for a, b in (((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)),
                     ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))):
            self.seg(pcbnew.Edge_Cuts, (self.X(a[0]), a[1]), (self.X(b[0]), b[1]))

    # ------------------------------------------------------------ parts
    def parts(self):
        idx = 1
        for r in range(ROWS):
            for c in range(COLS):
                x = KEY_X0 + c * PITCH_X
                y = KEY_Y0 + r * PITCH_Y
                sw = self.place(LIB, "Kailh_PG1316S_castellated", f"SW{idx}", x, y, value="PG1316S")
                d = self.place(f"{KICAD_FP}/Diode_SMD.pretty", "D_SOD-523", f"D{idx}",
                               x + DIODE_DX, y + DIODE_DY, rot=90, value="1N4148WT")
                # right half: physical column index counted left -> right on that half
                pc = c if self.side == "left" else COLS - 1 - c
                col_net = f"COL{pc}"
                row_net = f"ROW{r}"
                self.connect(sw, "1", col_net)
                self.connect(sw, "2", f"N_SW{idx}")
                self.connect(d, "2", f"N_SW{idx}")   # anode
                self.connect(d, "1", row_net)        # cathode -> row (col2row)
                idx += 1

        u = self.place(LIB, "nice_nano_v2_flush", "U1", NANO_X, NANO_Y, rot=NANO_ROT, value="nice!nano v2")
        col_pins, row_pins = MATRIX_PINS[self.side]
        for c, p in enumerate(col_pins):
            self.connect(u, NANO_PADS[p], f"COL{c}")
        for r, p in enumerate(row_pins):
            self.connect(u, NANO_PADS[p], f"ROW{r}")
        # The nice!nano ties its GND pins together internally; the third one (B-, next to RAW) sits in
        # the boxed-in front corner, so only the two on the other column are wired.
        for g in ("GND", "GND2"):
            self.connect(u, NANO_PADS[g], "GND")
        self.connect(u, NANO_PADS["RAW"], "RAW")
        self.connect(u, NANO_PADS["RST"], "RST")

        bt = self.place(LIB, "Battery_Pads_Small", "BT1", *BAT_PADS, value="LiPo 3.7V")
        self.connect(bt, "1", "RAW")         # no power switch: the cell feeds the nice!nano directly
        self.connect(bt, "2", "GND")

        rst = self.place(f"{KICAD_FP}/Button_Switch_SMD.pretty", "SW_Push_1P1T_NO_CK_KMR2",
                         "SW31", *RESET, rot=90, value="KMR211NGLFS", bottom=True)
        self.connect(rst, "1", "RST")
        self.connect(rst, "2", "GND")


        self.text("BAYLEAF", 56, 40, 4.0, pcbnew.B_SilkS)
        self.text(f"{self.side} half - rev 1", 56, 47, 1.5, pcbnew.B_SilkS)
        self.text("RST", RESET[0], RESET[1] - 4.2, 0.8, pcbnew.B_SilkS)
        self.text("LiPo 3.0x20x30", 121.65, 50.0, 0.9, pcbnew.Cmts_User)
        for i, (x, y, d) in enumerate(BOSSES):
            h = self.place(f"{KICAD_FP}/MountingHole.pretty", "MountingHole_2.2mm_M2", f"H{i + 1}", x, y,
                           value=f"boss {d:g}")
            for g in list(h.GraphicalItems()):  # stock courtyard is wider than the 4 mm bosses
                if g.GetLayer() == pcbnew.F_CrtYd:
                    h.Remove(g)

    def keepouts(self):
        # The aluminium bosses sit on the board: no top copper or vias under them.
        for x, y, d in BOSSES:
            zb = pcbnew.ZONE(self.board)
            zb.SetIsRuleArea(True)
            zb.SetDoNotAllowTracks(True)
            zb.SetDoNotAllowVias(True)
            zb.SetDoNotAllowPads(False)
            zb.SetDoNotAllowCopperPour(True)
            zb.SetDoNotAllowFootprints(False)
            zb.SetLayer(pcbnew.F_Cu)
            o = zb.Outline()
            o.NewOutline()
            r = d / 2 + 0.4
            for k in range(24):
                a = 2 * math.pi * k / 24
                o.Append(mm(self.X(x + r * math.cos(a))), mm(y + r * math.sin(a)))
            self.board.Add(zb)

    def save(self, path):
        self.board.BuildConnectivity()
        pcbnew.SaveBoard(path, self.board)


# ---------------------------------------------------------------- FR4 bottom plate
# Shell coords = PCB coords + 1.05; the plate fills the shell's rabbet (case.py build_plate()).
PLATE = (-1.2, -1.2, 136.1, 93.5, 3.15)       # x0, y0, x1, y1, corner radius (PCB coords)
PLATE_USB_W, PLATE_USB_D = 9.7, 7.5          # notch under the USB-C receptacle (it hangs 0.3 mm into the plate)
SWITCH_RELIEF = (-4.3, -1.0, 4.3, 4.2)       # window under each switch's contact half-holes (solder bulges)
NANO_PIN_SLOT = (2.2, 1.8, 32.4)             # width, y0, y1 of the windows under the two nice!nano pin rows
RESET_WINDOW = (3.9, 6.1)                    # KMR2 (on the PCB's bottom) stands in this window


class PlateBuilder(Builder):
    def rrect(self, x0, y0, x1, y1, r):
        """Rounded-rectangle cutout (left-half coords, mirrored for the right half)."""
        x0, x1 = sorted((self.X(x0), self.X(x1)))
        pts = [((x0 + r, y0), (x1 - r, y0)), ((x1, y0 + r), (x1, y1 - r)),
               ((x1 - r, y1), (x0 + r, y1)), ((x0, y1 - r), (x0, y0 + r))]
        corners = [((x1 - r, y0 + r), (x1 - r, y0)), ((x1 - r, y1 - r), (x1, y1 - r)),
                   ((x0 + r, y1 - r), (x0 + r, y1)), ((x0 + r, y0 + r), (x0, y0 + r))]
        for (a, b), (c, st) in zip(pts, corners):
            self.seg(pcbnew.Edge_Cuts, a, b)
            self.arc(c, st, 90)

    def plate(self):
        x0, y0, x1, y1, r = PLATE
        ux0, ux1 = NANO_X - PLATE_USB_W / 2, NANO_X + PLATE_USB_W / 2
        uy = PLATE_USB_D
        poly = [(x0 + r, y0), (ux0, y0), (ux0, uy), (ux1, uy), (ux1, y0), (x1 - r, y0), None,
                (x1, y0 + r), (x1, y1 - r), None, (x1 - r, y1), (x0 + r, y1), None,
                (x0, y1 - r), (x0, y0 + r), None]
        corners = {6: ((x1 - r, y0 + r), (x1 - r, y0)), 9: ((x1 - r, y1 - r), (x1, y1 - r)),
                   12: ((x0 + r, y1 - r), (x0 + r, y1)), 15: ((x0 + r, y0 + r), (x0, y0 + r))}
        prev = None
        for i, p in enumerate(poly + [poly[0]]):
            if p is None:
                c, st = corners[i]
                self.arc((self.X(c[0]), c[1]), (self.X(st[0]), st[1]), 90 if self.side == "left" else -90)
                prev = None
                continue
            if prev is not None:
                self.seg(pcbnew.Edge_Cuts, (self.X(prev[0]), prev[1]), (self.X(p[0]), p[1]))
            prev = p
        sx0, sy0, sx1, sy1 = SWITCH_RELIEF
        for row in range(ROWS):
            for col in range(COLS):
                x, y = KEY_X0 + col * PITCH_X, KEY_Y0 + row * PITCH_Y
                self.rrect(x + sx0, y + sy0, x + sx1, y + sy1, 1.0)
        w, ya, yb = NANO_PIN_SLOT
        for dx in (-7.62, 7.62):
            self.rrect(NANO_X + dx - w / 2, ya, NANO_X + dx + w / 2, yb, w / 2 - 0.01)
        rw, rh = RESET_WINDOW
        self.rrect(RESET[0] - rw / 2, RESET[1] - rh / 2, RESET[0] + rw / 2, RESET[1] + rh / 2, 0.8)
        for i, (x, y, _) in enumerate(BOSSES):
            h = self.place(f"{KICAD_FP}/MountingHole.pretty", "MountingHole_2.2mm_M2", f"H{i + 1}", x, y)
            for g in list(h.GraphicalItems()):
                if g.GetLayer() in (pcbnew.F_CrtYd, pcbnew.F_SilkS, pcbnew.F_Fab):
                    h.Remove(g)
        # no copper at all: the plate must stay transparent to the 2.4 GHz radio
        self.text("bayleaf", 56, 22.2, 5.0, pcbnew.B_SilkS)
        self.text(f"{self.side} - FR4 bottom plate, no copper", 56, 39.2, 1.2, pcbnew.B_SilkS)


def build_plate(side):
    b = PlateBuilder(side)
    b.plate()
    path = os.path.join(HERE, f"bayleaf-plate-{side}.kicad_pcb")
    b.save(path)
    out = os.path.join(HERE, "fab", f"plate-{side}")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    g = tempfile.mkdtemp()
    run(["kicad-cli", "pcb", "export", "gerbers", "--layers", "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
         "--subtract-soldermask", "--no-x2", "--use-drill-file-origin", "-o", g + "/", path])
    run(["kicad-cli", "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
         "-o", g + "/", path])
    shutil.make_archive(os.path.join(out, f"bayleaf-plate-{side}-gerbers"), "zip", g)
    shutil.rmtree(g)
    run(["kicad-cli", "pcb", "export", "step", "--force", "--user-origin", "0x0mm", "--board-only",
         "-o", os.path.join(out, f"bayleaf-plate-{side}.step"), path], stdout=subprocess.DEVNULL)
    rpt = os.path.join(out, f"bayleaf-plate-{side}-drc.rpt")
    pcbnew.WriteDRCReport(pcbnew.LoadBoard(path), rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return rpt


def run(cmd, **kw):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def parse_sexpr(text):
    tokens, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in "()":
            tokens.append(ch)
            i += 1
        elif ch.isspace():
            i += 1
        elif ch == '"':
            j = text.index('"', i + 1)
            tokens.append(text[i + 1:j])
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            tokens.append(text[i:j])
            i = j
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(t)
    return stack[0][0]


def import_ses(board, ses_path):
    """Minimal Specctra session importer (pcbnew.ImportSpecctraSES needs the GUI in KiCad 7)."""
    tree = parse_sexpr(open(ses_path).read())
    routes = next(x for x in tree if isinstance(x, list) and x[0] == "routes")
    res = next(x for x in routes if isinstance(x, list) and x[0] == "resolution")
    scale = {"um": 1e-3, "mm": 1.0, "mil": 0.0254}[res[1]] / float(res[2])  # -> mm
    layers = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    vias = {}
    lib = next((x for x in routes if isinstance(x, list) and x[0] == "library_out"), [])
    for ps in lib[1:]:
        if ps[0] == "padstack":
            dia = float(ps[2][1][2]) * scale
            vias[ps[1]] = dia
    net_out = next(x for x in routes if isinstance(x, list) and x[0] == "network_out")
    count = 0
    for net in net_out[1:]:
        ni = board.FindNet(net[1])
        for item in net[2:]:
            if item[0] == "wire":
                path = item[1]
                layer, width = layers[path[1]], float(path[2]) * scale
                coords = [float(v) * scale for v in path[3:] if not isinstance(v, list)]
                pts_ = [(coords[k], -coords[k + 1]) for k in range(0, len(coords), 2)]
                for a, b in zip(pts_, pts_[1:]):
                    if a == b:
                        continue
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(pt(*a))
                    t.SetEnd(pt(*b))
                    t.SetWidth(mm(width))
                    t.SetLayer(layer)
                    t.SetNet(ni)
                    board.Add(t)
                    count += 1
            elif item[0] == "via":
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pt(float(item[2]) * scale, -float(item[3]) * scale))
                dia = vias.get(item[1], 0.6)
                v.SetWidth(mm(dia))
                v.SetDrill(mm(0.3 if dia <= 0.6 else 0.35))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                v.SetNet(ni)
                board.Add(v)
    return count


def prune_dangling(board):
    """Drop autorouter stubs (track ends that touch nothing), repeat until stable."""
    removed = 0
    while True:
        board.BuildConnectivity()
        conn = board.GetConnectivity()
        stubs = [t for t in board.GetTracks()
                 if t.GetClass() == "PCB_TRACK" and conn.TestTrackEndpointDangling(t, False)]
        if not stubs:
            return removed
        for t in stubs:
            board.Remove(t)
        removed += len(stubs)


def notch_switch_windows(dsn):
    """The switch contacts are castellated half-holes whose centres lie on the edge of the window under each
    switch. Freerouting can't start a route inside a keepout, so for routing only, each window's keepout gets
    a notch around the two contact pads (the notches only open onto the pads, so no trace can cross the
    window; the real board keeps the plain window)."""
    import re
    text = open(dsn).read()
    pat = re.compile(r'\(keepout "" \(polygon signal 0 ([-\d.\s]+)\)\)')

    def repl(m):
        v = [float(t) for t in m.group(1).split()]
        xs, ys = [x / 1000 for x in v[0::2]], [-y / 1000 for y in v[1::2]]   # um -> mm, board y
        if not (abs(max(xs) - min(xs) - 8.0) < 0.05 and abs(max(ys) - min(ys) - 3.4) < 0.05):
            return m.group(0)                                                 # not a switch window
        cx, y0, y1 = (max(xs) + min(xs)) / 2, min(ys), max(ys)
        # the front edge is pushed 0.3 mm out, so no trace can run along the real window edge
        rn, dy = 1.35, 0.3
        a0 = math.asin(dy / rn)
        pts = [(cx - 4, y0), (cx + 4, y0), (cx + 4, y1 + dy)]
        for px in (cx + 1.55, cx - 1.55):                                     # walk the front edge right -> left
            for k in range(15):
                a = -a0 + (math.pi + 2 * a0) * k / 14
                pts.append((px + rn * math.cos(a), y1 - rn * math.sin(a)))
        pts.append((cx - 4, y1 + dy))
        coords = " ".join(f"{x * 1000:.1f} {-y * 1000:.1f}" for x, y in pts)
        return f'(keepout "" (polygon signal 0 {coords}))'

    text, n = pat.subn(repl, text)
    open(dsn, "w").write(text)


def route(pcb_path, attempts=10):
    base = pcb_path[:-10]
    dsn, ses = base + ".dsn", base + ".ses"
    board = pcbnew.LoadBoard(pcb_path)
    assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
    notch_switch_windows(dsn)
    for attempt in range(1, attempts + 1):
        workdir = tempfile.mkdtemp()  # freerouting drops a logs/ folder in its cwd
        run(["java", "-jar", FREEROUTING_JAR, "--gui.enabled=false",
             "-de", dsn, "-do", ses, "-mp", "60"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800, cwd=workdir)
        shutil.rmtree(workdir, ignore_errors=True)
        board = pcbnew.LoadBoard(pcb_path)
        n = import_ses(board, ses)
        stubs = prune_dangling(board)
        board.BuildConnectivity()
        unrouted = board.GetConnectivity().GetUnconnectedCount(False)
        print(f"attempt {attempt}: {n} segments, {stubs} stubs pruned, {unrouted} unrouted")
        if unrouted == 0:
            break
    else:
        sys.exit(f"{pcb_path}: autorouter left {unrouted} connections unrouted")
    pcbnew.SaveBoard(pcb_path, board)
    os.remove(dsn)
    os.remove(ses)


# Parts JLCPCB can place (everything else is hand-soldered, see docs/assembly.md).
# LCSC numbers: check stock before ordering.
JLC_PARTS = {
    "D_SOD-523": ("1N4148WT", ""),  # pick any 1N4148WT/SOD-523 in JLC's parts search
}


def jlc_assembly_files(pcb_path, out, side):
    import csv
    board = pcbnew.LoadBoard(pcb_path)
    groups, cpl = {}, []
    for fp in board.GetFootprints():
        name = fp.GetFPID().GetLibItemName().wx_str()
        if name not in JLC_PARTS:
            continue
        groups.setdefault(name, []).append(fp.GetReference())
        pos = fp.GetPosition()
        cpl.append((fp.GetReference(), f"{pcbnew.ToMM(pos.x):.3f}mm", f"{-pcbnew.ToMM(pos.y):.3f}mm",
                    "Top", f"{fp.GetOrientationDegrees() % 360:.1f}"))
    with open(os.path.join(out, f"bayleaf-{side}-jlc-bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for name, refs in sorted(groups.items()):
            value, lcsc = JLC_PARTS[name]
            refs.sort(key=lambda r: (r.rstrip("0123456789"), int(r.lstrip("DSW"))))
            w.writerow([value, ",".join(refs), name, lcsc])
    with open(os.path.join(out, f"bayleaf-{side}-jlc-cpl.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(sorted(cpl, key=lambda r: (r[0].rstrip("0123456789"), int(r[0].lstrip("DSW")))))


def fab(pcb_path, side):
    out = os.path.join(HERE, "fab", side)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    g = tempfile.mkdtemp()
    layers = "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
    run(["kicad-cli", "pcb", "export", "gerbers", "--layers", layers,
         "--subtract-soldermask", "--no-x2", "--use-drill-file-origin", "-o", g + "/", pcb_path])
    run(["kicad-cli", "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
         "--generate-map", "--map-format", "pdf", "-o", g + "/", pcb_path])
    shutil.make_archive(os.path.join(out, f"bayleaf-{side}-gerbers"), "zip", g)
    shutil.rmtree(g)
    run(["kicad-cli", "pcb", "export", "pos", "--side", "front", "--format", "csv", "--units", "mm",
         "--smd-only", "-o", os.path.join(out, f"bayleaf-{side}-pos.csv"), pcb_path])
    svg = os.path.join(out, f"bayleaf-{side}.svg")
    run(["kicad-cli", "pcb", "export", "svg", "--layers", "F.Cu,B.Cu,F.SilkS,Edge.Cuts",
         "--page-size-mode", "2", "--exclude-drawing-sheet", "-o", svg, pcb_path])
    if shutil.which("rsvg-convert"):
        img = os.path.join(HERE, "..", "..", "docs", "img", f"pcb-{side}.png")
        run(["rsvg-convert", "-w", "1800", "-b", "white", svg, "-o", img])
    run(["kicad-cli", "pcb", "export", "step", "--subst-models", "--force",
         "-o", os.path.join(out, f"bayleaf-{side}-pcb.step"), pcb_path],
        stdout=subprocess.DEVNULL)
    jlc_assembly_files(pcb_path, out, side)
    rpt = os.path.join(out, f"bayleaf-{side}-drc.rpt")
    board = pcbnew.LoadBoard(pcb_path)  # kicad-cli 7 has no DRC command; use the API
    pcbnew.WriteDRCReport(board, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return rpt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-route", action="store_true")
    ap.add_argument("--side", choices=["left", "right", "both"], default="both")
    ap.add_argument("--plates-only", action="store_true", help="only (re)build the FR4 bottom plates")
    args = ap.parse_args()
    sides = ["left", "right"] if args.side == "both" else [args.side]
    for side in sides:
        rpt = build_plate(side)
        print(open(rpt).read().split("** Found")[1:])
        if args.plates_only:
            continue
        b = Builder(side)
        b.outline()
        b.parts()
        b.keepouts()
        path = os.path.join(HERE, f"bayleaf-{side}.kicad_pcb")
        b.save(path)
        if not args.no_route:
            route(path)
            rpt = fab(path, side)
            print(open(rpt).read())


if __name__ == "__main__":
    main()
