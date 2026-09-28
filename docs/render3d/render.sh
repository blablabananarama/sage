#!/bin/sh
# Photoreal-ish renders -> docs/img/3d/*.jpg  (three.js in headless Chromium via Playwright)
#   needs: node, kicad-cli, rsvg-convert, python with numpy+Pillow, a Chromium (CHROME=/path/to/chrome)
set -e
cd "$(dirname "$0")"
python3 make_textures.py
cp ../../hardware/case/out/bayleaf-case-left.stl ../../hardware/case/out/bayleaf-case-right.stl .
[ -d node_modules ] || npm install --no-save playwright three
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 & SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1
node shoot.mjs '{
"hero":"w=2400&h=1250&cam=174,-395,265&tx=174&ty=-42&tz=0&fov=31",
"top":"w=2400&h=900&cam=174,-47.5,1500&tx=174&ty=-46.5&tz=0&fov=5.6&bg=%23f4f5f6",
"closeup":"halves=left&w=2000&h=1300&cam=190,-150,95&tx=110&ty=-35&tz=2&fov=30",
"exploded":"halves=left&explode=11&w=2000&h=1500&cam=230,-230,190&tx=75&ty=-46&tz=18&fov=36",
"profile":"halves=left&w=2400&h=1000&cam=-40,-135,9&tx=60&ty=-60&tz=1&fov=26"
}'
python3 -c "
from PIL import Image
for n in ['hero','top','closeup','exploded','profile']:
    Image.open(n + '.png').convert('RGB').save('../img/3d/' + n + '.jpg', quality=88, optimize=True)
"
rm -f *.png *.stl
