#!/usr/bin/env python3
"""Composite realistic PCB top textures (black mask, ENIG pads, white silk) from the KiCad boards.

Needs kicad-cli, rsvg-convert, numpy and Pillow. Writes pcb-<side>-top.png next to this file.
"""
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, "..", "..", "hardware", "pcb")
LAYERS = ("F.Cu", "F.Mask", "F.SilkS", "Edge.Cuts")

for side in ("left", "right"):
    tmp = tempfile.mkdtemp()
    L = {}
    for layer in LAYERS:
        svg, png = os.path.join(tmp, f"{layer}.svg"), os.path.join(tmp, f"{layer}.png")
        subprocess.run(["kicad-cli", "pcb", "export", "svg", "--layers", f"{layer},Edge.Cuts", "--black-and-white",
                        "--page-size-mode", "2", "--exclude-drawing-sheet", "-o", svg,
                        os.path.join(PCB, f"bayleaf-{side}.kicad_pcb")], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["rsvg-convert", "-z", "7.5591", "-b", "white", svg, "-o", png], check=True)  # ~28.6 px/mm
        L[layer] = np.array(Image.open(png).convert("L")) < 128
    ys, xs = np.nonzero(L["Edge.Cuts"])  # crop to the board outline
    crop = lambda a: a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cu, mask, silk, edge = (crop(L[k]) for k in LAYERS)
    fill = Image.fromarray(np.pad(edge * 255, 2).astype(np.uint8))
    ImageDraw.floodfill(fill, (0, 0), 128)  # everything reachable from outside is not board
    inside = np.array(fill)[2:-2, 2:-2] != 128
    rgb = np.zeros(cu.shape + (3,), np.uint8)
    rgb[:] = (18, 20, 22)                     # black soldermask
    rgb[cu & ~edge] = (46, 50, 54)            # copper under mask
    pads = mask & ~edge
    rgb[pads] = (214, 178, 96)                # ENIG
    rgb[silk & ~pads & ~edge] = (235, 235, 230)
    Image.fromarray(np.dstack([rgb, (inside * 255).astype(np.uint8)]), "RGBA").save(
        os.path.join(HERE, f"pcb-{side}-top.png"))
    print("wrote", side)
