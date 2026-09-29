#!/bin/sh
# Photoreal-ish renders -> docs/img/3d/*.jpg  (three.js in headless Chromium via Playwright)
#   needs: node, kicad-cli, rsvg-convert, python with numpy+Pillow, a Chromium (CHROME=/path/to/chrome)
set -e
cd "$(dirname "$0")"
python3 make_textures.py   # needs numpy + Pillow
cp ../../hardware/case/out/bayleaf-*.stl .
[ -d node_modules ] || npm install --no-save playwright three
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 & SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1
node shoot.mjs '{
"hero":"w=2400&h=1250&cam=174,-400,250&tx=174&ty=-44&tz=0&fov=30",
"desk":"w=2400&h=1300&bg=%23232427&cam=-40,-330,95&tx=175&ty=-40&tz=0&fov=27",
"back":"halves=left&w=2200&h=1300&cam=190,120,45&tx=78&ty=-45&tz=2&fov=31",
"front":"halves=left&w=2200&h=1300&cam=200,-200,42&tx=78&ty=-50&tz=2&fov=31",
"closeup":"halves=left&w=2000&h=1300&cam=175,70,55&tx=112&ty=-25&tz=2&fov=30",
"exploded":"halves=left&explode=11&w=2000&h=1500&cam=225,-235,200&tx=70&ty=-47&tz=26&fov=40",
"inside":"halves=left&noshell=1&w=2000&h=1300&cam=180,-190,150&tx=90&ty=-50&tz=0&fov=34",
"top":"w=2400&h=950&cam=174,-48.2,1500&tx=174&ty=-47.2&tz=0&fov=5.9&bg=%23f4f5f6",
"legends":"legends=1&w=2400&h=1250&cam=174,-400,250&tx=174&ty=-44&tz=0&fov=30",
"bottom":"halves=left&w=2200&h=1300&cam=150,-210,-170&tx=70&ty=-47&tz=0&fov=34&exp=1.1",
"v_backq_draft":"halves=left&styles=&w=1100&h=700&cam=190,120,45&tx=85&ty=-45&tz=2&fov=33",
"v_backq_chamfer":"halves=left&styles=-chamfer&w=1100&h=700&cam=190,120,45&tx=85&ty=-45&tz=2&fov=33",
"v_backq_round":"halves=left&styles=-round&w=1100&h=700&cam=190,120,45&tx=85&ty=-45&tz=2&fov=33",
"v_frontq_draft":"halves=left&styles=&w=1100&h=700&cam=200,-200,42&tx=78&ty=-50&tz=2&fov=31",
"v_frontq_chamfer":"halves=left&styles=-chamfer&w=1100&h=700&cam=200,-200,42&tx=78&ty=-50&tz=2&fov=31",
"v_frontq_round":"halves=left&styles=-round&w=1100&h=700&cam=200,-200,42&tx=78&ty=-50&tz=2&fov=31",
"v_corner_draft":"halves=left&styles=&w=1100&h=700&cam=175,40,22&tx=128&ty=-10&tz=2&fov=22",
"v_corner_chamfer":"halves=left&styles=-chamfer&w=1100&h=700&cam=175,40,22&tx=128&ty=-10&tz=2&fov=22",
"v_corner_round":"halves=left&styles=-round&w=1100&h=700&cam=175,40,22&tx=128&ty=-10&tz=2&fov=22",
"v_frontcorner_draft":"halves=left&styles=&w=1100&h=700&cam=-45,-150,22&tx=6&ty=-88&tz=2&fov=22",
"v_frontcorner_chamfer":"halves=left&styles=-chamfer&w=1100&h=700&cam=-45,-150,22&tx=6&ty=-88&tz=2&fov=22",
"v_frontcorner_round":"halves=left&styles=-round&w=1100&h=700&cam=-45,-150,22&tx=6&ty=-88&tz=2&fov=22"
}'
${CQ_PYTHON:-python3} sections.py   # needs cadquery
python3 -c "
from PIL import Image, ImageDraw, ImageFont
for n in ['hero','desk','back','front','closeup','exploded','inside','top','legends','bottom']:
    Image.open(n + '.png').convert('RGB').save('../img/3d/' + n + '.jpg', quality=88, optimize=True)
# case variants side by side: 4 views each, plus the CAD cross-sections from sections.py
def F(n):
    try: return ImageFont.truetype('DejaVuSans.ttf', n)
    except OSError: return ImageFont.load_default()
views = [('backq', 'back'), ('frontq', 'front'), ('corner', 'back corner, USB-C'), ('frontcorner', 'front corner')]
styles = [('draft', 'drafted walls (MK5)'), ('chamfer', 'straight + 0.5 mm chamfer'), ('round', 'straight + rounded edges')]
sec = Image.open('sections.png').convert('RGB')
out = Image.new('RGB', (3300, 90 + 4 * 700 + sec.size[1]), 'white'); d = ImageDraw.Draw(out)
for j, (st, label) in enumerate(styles):
    d.text((j * 1100 + 40, 28), label, fill='#222', font=F(40))
for i, (v, label) in enumerate(views):
    for j, (st, _) in enumerate(styles):
        out.paste(Image.open(f'v_{v}_{st}.png').convert('RGB'), (j * 1100, 90 + i * 700))
    d.text((20, 90 + i * 700 + 14), label, fill='#555', font=F(28))
out.paste(sec, (0, 90 + 4 * 700))
out.save('../img/3d/compare.jpg', quality=86, optimize=True)
"
rm -f *.png *.stl
