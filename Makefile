# Regenerate every manufacturing output from source.
#   make pcb     - KiCad 7 (pcbnew python) + Freerouting 2.x (FREEROUTING_JAR=/path/to/freerouting.jar)
#   make case    - CadQuery (CQ_PYTHON=python with cadquery installed)
#   make render  - README renders (three.js in headless Chromium, see docs/render3d/render.sh)
KICAD_PYTHON ?= /usr/bin/python3
CQ_PYTHON ?= python3

.PHONY: all pcb case render
all: pcb case render

pcb:
	cd hardware/pcb && $(KICAD_PYTHON) generate_pcb.py

case:
	cd hardware/case && $(CQ_PYTHON) case.py

render:
	docs/render3d/render.sh
