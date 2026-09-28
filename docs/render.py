#!/usr/bin/env python3
"""Line-drawing render of one half (case + keycaps + nice!nano + LiPo) -> docs/img/*.png.

    /opt/cq/bin/python docs/render.py     (needs cadquery and rsvg-convert)
"""
import os
import sys

import subprocess

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hardware", "case"))
import case as C  # noqa: E402


def box(x0, y0, z0, w, h, d):
    # KiCad-style y (down) -> CadQuery y (up)
    return cq.Workplane("XY").box(w, h, d, centered=False).translate((x0, -(y0 + h), z0))


def assembly(side):
    X = (lambda x, w: C.OFF + x) if side == "left" else (lambda x, w: C.OUT_W - C.OFF - x - w)
    pcb_z, pcb_t = C.FLOOR + 0.1, 0.8
    parts = C.build(side)
    parts = parts.union(box(X(0, C.BOARD_W), C.OFF, pcb_z, C.BOARD_W, C.BOARD_H, pcb_t), clean=False) \
        if False else parts  # PCB is hidden under the caps anyway; keep the drawing light
    for r in range(5):
        for k in range(6):
            cx, cy = 11 + 18 * k, (C.BOARD_H - 85) / 2 + 8.5 + 17 * r
            cap = box(X(cx - 8.025, 16.05), C.OFF + cy - 8.125, 3.6, 16.05, 16.25, 1.2).edges("|Z").fillet(1.0)
            parts = parts.add(cap)
    parts = parts.add(box(X(C.NANO_X - 9, 18), C.OFF + C.NANO_TOP, pcb_z + pcb_t, 18, 33.3, 3.2))
    x0, y0, _, _ = C.BAT_CUT
    parts = parts.add(box(X(x0 + 1.1, 20), C.OFF + y0 + 2, C.FLOOR, 20, 40, 3.0))
    return cq.Compound.makeCompound([o for o in parts.vals() if isinstance(o, cq.Shape)])


def render(side, path, direction, spin):
    svg = path[:-4] + ".svg"
    shape = assembly(side).rotate((0, 0, 0), (0, 0, 1), spin)  # the SVG exporter has a fixed "up"
    cq.exporters.export(cq.Workplane().add(shape), svg, opt={
        "width": 1400, "height": 900, "marginLeft": 20, "marginTop": 20,
        "projectionDir": direction, "showAxes": False, "showHidden": False,
        "strokeWidth": 0.35, "strokeColor": (40, 40, 40)})
    subprocess.run(["rsvg-convert", "-b", "white", "-w", "1400", svg, "-o", path], check=True)
    os.remove(svg)
    from PIL import Image, ImageChops, ImageDraw
    im = Image.open(path).convert("RGB")
    ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline="white", width=4)  # svg frame
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    im.crop((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20)).save(path)


SPIN = 90


if __name__ == "__main__":
    out = os.path.join(HERE, "img")
    os.makedirs(out, exist_ok=True)
    render("left", os.path.join(out, "render-left.png"), (-0.35, -1.0, 1.1), SPIN)
    render("right", os.path.join(out, "render-right.png"), (0.35, -1.0, 1.1), SPIN)
