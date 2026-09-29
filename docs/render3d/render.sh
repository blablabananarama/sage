#!/bin/sh
# Photoreal-ish renders -> docs/img/3d/*.jpg  (three.js in headless Chromium via Playwright)
#   needs: node, kicad-cli, rsvg-convert, python with numpy+Pillow, a Chromium (CHROME=/path/to/chrome)
set -e
cd "$(dirname "$0")"
python3 make_textures.py   # needs numpy + Pillow
cp ../../hardware/case/out/bayleaf-shell-left.stl ../../hardware/case/out/bayleaf-shell-right.stl ../../hardware/case/out/bayleaf-plate-left.stl ../../hardware/case/out/bayleaf-plate-right.stl .
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
"legends":"legends=1&w=2400&h=1250&cam=174,-400,250&tx=174&ty=-44&tz=0&fov=30"
}'
python3 -c "
from PIL import Image
for n in ['hero','desk','back','front','closeup','exploded','inside','top','legends']:
    Image.open(n + '.png').convert('RGB').save('../img/3d/' + n + '.jpg', quality=88, optimize=True)
"
rm -f *.png *.stl
