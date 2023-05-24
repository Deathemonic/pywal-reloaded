"""
Generate a colorscheme using fast_colorthief.
"""

import logging
import sys

try:
    import fast_colorthief
except ImportError:
    logging.error("fast_colorthief isn't installed on your system.")
    logging.info("Install it by running. (pip3 install fast-colorthief)")
    logging.info("Or try another backend. (wal --backend)")
    sys.exit(1)

from pywal import utils


def gen_colors(img: str):
    return [utils.rgb_to_hex(color) for color in fast_colorthief.get_palette(img, 16)]


def adjust(cols: list, light: bool):
    cols.sort(key=utils.hex_to_yiq)
    raw_colors = [*cols, *cols]

    if light:
        raw_colors[0] = utils.brighten_color(cols[0], 0.90, True)
        raw_colors[7] = utils.brighten_color(cols[0], 0.75, False)

    else:
        # for color in raw_colors:
        #     color = utils.brighten_color(color, 0.40, True)

        raw_colors[0] = utils.brighten_color(cols[0], 0.80, False)
        raw_colors[7] = utils.brighten_color(cols[0], 0.60, True)

    raw_colors[8] = utils.brighten_color(cols[0], 0.20, True)
    raw_colors[15] = raw_colors[7]

    return raw_colors


def get(img: str, light: bool = False):
    cols = gen_colors(img)
    return adjust(cols, light)


print(get("/home/deathemonic/Pictures/wallpapers/wallpaper_1.jpg"))
