#!/usr/bin/env python3
"""Cross-sections of the three shell variants (CadQuery; run from this folder) -> sections.png."""
import cadquery as cq
from PIL import Image, ImageDraw, ImageFont
Y = 40.0   # shell y of the cut (clear of posts)
def F(n):
    try: return ImageFont.truetype('DejaVuSans.ttf', n)
    except OSError: return ImageFont.load_default()
def tris(style):
    shp = cq.importers.importStep(f'../../hardware/case/out/bayleaf-shell-left{style}.step').val()
    slab = cq.Solid.makeBox(160, 0.02, 10, cq.Vector(-10, -Y - 0.01, -2))
    cut = shp.intersect(slab)
    out = []
    for f in cut.Faces():
        n = f.normalAt()
        if abs(n.y) > 0.99 and f.Center().y > -Y:
            vs, ts = f.tessellate(0.002, 0.05)
            out += [[(vs[i].x, vs[i].z) for i in t] for t in ts]
    return out
def panel(tr, x0, x1, W=1100, H=420, z0=-0.4, z1=5.4):
    s = min(W / (x1 - x0), H / (z1 - z0))
    im = Image.new('RGB', (W, H), '#f4f5f6'); d = ImageDraw.Draw(im)
    X = lambda x: (x - x0) * s; Z = lambda z: H - (z - z0) * s
    for zz in (0, 1, 2, 3, 4, 5):                       # 1 mm grid
        d.line([(0, Z(zz)), (W, Z(zz))], fill='#e2e4e7'); d.text((4, Z(zz) - 16), f'{zz} mm', fill='#9aa0a6', font=F(14))
    for t in tr:
        d.polygon([(X(x), Z(z)) for x, z in t], fill='#8f949b')
    return im
styles = [('', 'drafted walls (MK5)'), ('-chamfer', 'straight + 0.5 mm chamfer'), ('-round', 'straight + rounded edges')]
data = {s: tris(s) for s, _ in styles}
rows = [(-2.0, 9.0, 'section at y = 40: outer wall and key-window edge (left end)'),
        (125.0, 139.0, 'section at y = 40: plateau, divider and outer wall (controller end)')]
W, H, top = 1100, 420, 60
out = Image.new('RGB', (3 * W, len(rows) * (H + top)), 'white'); d = ImageDraw.Draw(out)
for i, (x0, x1, label) in enumerate(rows):
    d.text((16, i * (H + top) + 18), label, fill='#555', font=F(26))
    for j, (s, name) in enumerate(styles):
        out.paste(panel(data[s], x0, x1), (j * W, i * (H + top) + top))
        d.text((j * W + 16, i * (H + top) + top + 8), name, fill='#222', font=F(24))
out.save('sections.png')
print(out.size, {s: len(v) for s, v in data.items()})
