# Bayleaf firmware (ZMK)

* `boards/shields/bayleaf/` holds the shield: the matrix (`bayleaf.dtsi`), left/right overlays and Kconfig.
* `bayleaf.keymap`, `bayleaf.conf` and `west.yml` (in `firmware/` itself) hold the user keymap, user Kconfig overrides and the west manifest (ZMK `main`).
* `build.yaml` is the build matrix. It builds left, right and `settings_reset` for `nice_nano//zmk` (nice!nano v2).

GitHub Actions (`.github/workflows/firmware.yml`) builds everything on every push that touches `firmware/`. Download the `bayleaf-firmware` artifact from the run.

## Default keymap

```
Base
| ESC  |  1  |  2  |  3  |  4    |  5    |   |  6    |  7    |  8   |  9   |  0  | BSPC |
| TAB  |  Q  |  W  |  E  |  R    |  T    |   |  Y    |  U    |  I   |  O   |  P  | DEL  |
| CTRL |  A  |  S  |  D  |  F    |  G    |   |  H    |  J    |  K   |  L   |  ;  |  '   |
| SHFT |  Z  |  X  |  C  |  V    |  B    |   |  N    |  M    |  ,   |  .   |  /  | ENT  |
| CTRL | GUI | ALT | GUI | LOWER | SPACE |   | SPACE | RAISE | LEFT | DOWN | UP  | RIGHT|
```

Lower has symbols and F-keys, Raise has numbers and navigation, and Lower+Raise gives Adjust (Bluetooth profiles, USB/BLE output, bootloader, reset).

## Local build

```sh
west init -l firmware && west update && west zephyr-export
west build -s zmk/app -d build/left  -b nice_nano//zmk -- -DSHIELD=bayleaf_left  -DZMK_CONFIG=$PWD/firmware -DZMK_EXTRA_MODULES=$PWD
west build -s zmk/app -d build/right -b nice_nano//zmk -- -DSHIELD=bayleaf_right -DZMK_CONFIG=$PWD/firmware -DZMK_EXTRA_MODULES=$PWD
```
