#!/usr/bin/env python3
"""Generate the Bayleaf PCBs (left + right half) with the KiCad 7 pcbnew API.

    /usr/bin/python3 generate_pcb.py            # place + autoroute + DRC + fab outputs
    /usr/bin/python3 generate_pcb.py --no-route # placement only

Every dimension of the board lives in this file, so the design is fully
reproducible from source. Routing is done with Freerouting (set FREEROUTING_JAR).

Coordinate system: KiCad (x right, y down), origin at the top-left corner of the
left-half PCB. The right half is the mirror image (x -> BOARD_W - x); footprints
are *not* flipped because every part sits on the top side.
"""
import argparse
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
BOARD_W, BOARD_H = 135.5, 89.5   # fits a 139 x 93 mm case with 1.5 mm walls + 0.25 mm gap
CORNER_R = 1.0
ROWS, COLS = 5, 6
PITCH_X, PITCH_Y = 18.0, 17.0    # PG1316S caps are 16.05 x 16.25 mm
KEY_X0 = 2.0 + PITCH_X / 2       # first key centre
KEY_Y0 = (BOARD_H - ROWS * PITCH_Y) / 2 + PITCH_Y / 2
DIODE_DX, DIODE_DY = PITCH_X / 2, -1.0  # diode sits in the gap right of each switch

NANO_X, NANO_Y = 123.0, 0.6 + 33.3 / 2  # nice!nano centre (USB-C at the top edge)
USB_NOTCH_W, USB_NOTCH_D = 10.5, 7.5    # room for the mid-mount receptacle
BAT_CUT = (111.8, 45.0, 134.0, BOARD_H)  # x0, y0, x1, y1 - LiPo bay, open to bottom edge
BAT_PADS = (126.3, 42.0)
RESET = (118.6, 37.6)
POWER_SW = (BOARD_W - 2.3, 39.6)         # actuator pokes through the inner side wall

# Pro Micro pin label -> footprint pad number (see nice_nano_v2_flush.kicad_mod)
NANO_PADS = {n: i + 1 for i, n in enumerate(
    ["D1", "D0", "GND", "GND2", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9",
     "RAW", "GND3", "RST", "3V3", "D21", "D20", "D19", "D18", "D15", "D14", "D16", "D10"])}
# Matrix wiring - must match firmware/boards/shields/bayleaf/bayleaf.dtsi
COL_PINS = ["D1", "D0", "D2", "D3", "D4", "D5"]   # physical columns, left -> right
ROW_PINS = ["D6", "D7", "D8", "D9", "D14"]        # rows, top -> bottom


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

    def place(self, lib, name, ref, x, y, rot=0, value=None):
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
        bx0, by0, bx1, _ = BAT_CUT
        r = CORNER_R
        W, H = BOARD_W, BOARD_H
        poly = [  # straight edges; rounded outer corners are added as arcs
            (r, 0), (ux0, 0), (ux0, USB_NOTCH_D), (ux1, USB_NOTCH_D), (ux1, 0), (W - r, 0),
            None,  # corner top-right
            (W, r), (W, H - r),
            None,  # corner bottom-right
            (W - r, H), (bx1, H), (bx1, by0), (bx0, by0), (bx0, H), (r, H),
            None,  # corner bottom-left
            (0, H - r), (0, r),
            None,  # corner top-left
        ]
        corners = {6: ((W - r, r), (W - r, 0)), 9: ((W - r, H - r), (W, H - r)),
                   16: ((r, H - r), (r, H)), 19: ((r, r), (0, r))}
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

    # ------------------------------------------------------------ parts
    def parts(self):
        idx = 1
        for r in range(ROWS):
            for c in range(COLS):
                x = KEY_X0 + c * PITCH_X
                y = KEY_Y0 + r * PITCH_Y
                sw = self.place(LIB, "Kailh_PG1316S", f"SW{idx}", x, y, value="PG1316S")
                d = self.place(f"{KICAD_FP}/Diode_SMD.pretty", "D_SOD-323", f"D{idx}",
                               x + DIODE_DX, y + DIODE_DY, rot=90, value="1N4148WS")
                # right half: physical column index counted left -> right on that half
                pc = c if self.side == "left" else COLS - 1 - c
                col_net = f"COL{pc}"
                row_net = f"ROW{r}"
                self.connect(sw, "1", col_net)
                self.connect(sw, "2", f"N_SW{idx}")
                self.connect(d, "2", f"N_SW{idx}")   # anode
                self.connect(d, "1", row_net)        # cathode -> row (col2row)
                idx += 1

        u = self.place(LIB, "nice_nano_v2_flush", "U1", NANO_X, NANO_Y, value="nice!nano v2")
        for c, p in enumerate(COL_PINS):
            self.connect(u, NANO_PADS[p], f"COL{c}")
        for r, p in enumerate(ROW_PINS):
            self.connect(u, NANO_PADS[p], f"ROW{r}")
        for g in ("GND", "GND2", "GND3"):
            self.connect(u, NANO_PADS[g], "GND")
        self.connect(u, NANO_PADS["RAW"], "RAW")
        self.connect(u, NANO_PADS["RST"], "RST")

        bt = self.place(LIB, "Battery_Pads", "BT1", *BAT_PADS, value="LiPo 3.7V")
        self.connect(bt, "1", "BAT+")
        self.connect(bt, "2", "GND")

        rst = self.place(f"{KICAD_FP}/Button_Switch_SMD.pretty", "SW_Push_1P1T_XKB_TS-1187A",
                         "SW31", *RESET, value="TS-1187A-B-A-B")
        self.connect(rst, "1", "RST")
        self.connect(rst, "2", "GND")

        # PCM12 actuator points +Y at 0 deg; 90 deg turns it toward +X (inner edge of the left half)
        pwr = self.place(f"{KICAD_FP}/Button_Switch_SMD.pretty", "SW_SPDT_PCM12",
                         "SW32", *POWER_SW, rot=90, value="MSK12C02")
        self.connect(pwr, "1", "BAT+")
        self.connect(pwr, "2", "RAW")

        self.text("BAYLEAF", 56, 40, 4.0, pcbnew.B_SilkS)
        self.text(f"{self.side} half - rev 1", 56, 47, 1.5, pcbnew.B_SilkS)
        self.text("RST", RESET[0] - 4.6, RESET[1] + 3.6, 0.8)
        self.text("LiPo 3.0x20x40", 123.0, 66.0, 0.9, pcbnew.Cmts_User)

    def keepouts(self):
        # No top-layer copper under the nice!nano (its underside is not insulated).
        za = pcbnew.ZONE(self.board)
        za.SetIsRuleArea(True)
        za.SetDoNotAllowTracks(True)
        za.SetDoNotAllowVias(False)
        za.SetDoNotAllowPads(False)
        za.SetDoNotAllowCopperPour(True)
        za.SetDoNotAllowFootprints(False)
        za.SetLayer(pcbnew.F_Cu)
        ol = za.Outline()
        ol.NewOutline()
        x0, x1 = NANO_X - 9.0, NANO_X + 9.0
        y0, y1 = 0.0, NANO_Y + 33.3 / 2
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(mm(self.X(x)), mm(y))
        self.board.Add(za)

    def save(self, path):
        self.board.BuildConnectivity()
        pcbnew.SaveBoard(path, self.board)


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
    netinfo = board.GetNetInfo()
    count = 0
    for net in net_out[1:]:
        ni = netinfo.GetNetItem(net[1])
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


def route(pcb_path, attempts=6):
    base = pcb_path[:-10]
    dsn, ses = base + ".dsn", base + ".ses"
    board = pcbnew.LoadBoard(pcb_path)
    assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
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
    "D_SOD-323": ("1N4148WS", "C2128"),
    "SW_Push_1P1T_XKB_TS-1187A": ("TS-1187A-B-A-B", "C318884"),
    "SW_SPDT_PCM12": ("MSK12C02", "C431540"),
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
    args = ap.parse_args()
    sides = ["left", "right"] if args.side == "both" else [args.side]
    for side in sides:
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
