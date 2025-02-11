"""
Generate a palette using various backends.
"""

import logging
import os
import random
import re
import sys

from pywal import utils, theme
from .config import MODULE_DIR, CACHE_DIR, __cache_version__


def list_backends():
    return [
        b.name.replace(".py", "")
        for b in os.scandir(os.path.join(MODULE_DIR, "backends"))
        if "__" not in b.name
    ]


def normalize_img_path(img: str):
    return img.replace("\\", "/") if os.name == "nt" else img


def format_colors(colors: list, img: str):
    return {
        "wallpaper": normalize_img_path(img),
        "alpha": utils.Color.alpha_num,
        "special": {
            "background": colors[0],
            "foreground": colors[15],
            "cursor": colors[15],
        },
        "colors": {
            "color0": colors[0],
            "color1": colors[1],
            "color2": colors[2],
            "color3": colors[3],
            "color4": colors[4],
            "color5": colors[5],
            "color6": colors[6],
            "color7": colors[7],
            "color8": colors[8],
            "color9": colors[9],
            "color10": colors[10],
            "color11": colors[11],
            "color12": colors[12],
            "color13": colors[13],
            "color14": colors[14],
            "color15": colors[15],
        },
    }


def generic_adjust(colors: list[str], light: bool):
    if light:
        for color in colors:
            color = utils.saturate_color(color, 0.60)
            color = utils.brighten_color(color, 0.5, False)

        colors[0] = utils.brighten_color(colors[0], 0.95, True)
        colors[7] = utils.brighten_color(colors[0], 0.75, False)
        colors[8] = utils.brighten_color(colors[0], 0.25, False)
    else:
        colors[0] = utils.brighten_color(colors[0], 0.80, False)
        colors[7] = utils.brighten_color(colors[0], 0.75, True)
        colors[8] = utils.brighten_color(colors[0], 0.25, True)
    colors[15] = colors[7]

    return colors


def saturate_colors(colors, amount):
    if amount and float(amount) <= 1.0:
        for i, _ in enumerate(colors):
            if i not in [0, 7, 8, 15]:
                colors[i] = utils.saturate_color(colors[i], float(amount))

    return colors


def cache_frame(img: str, backend: str, light: str, cache_dir: str, sat: str = ""):
    color_type = "light" if light else "dark"
    file_name = re.sub("[/|\\|.]", "_", img)
    file_size = os.path.getsize(img)

    return [
        cache_dir,
        "schemes",
        f"{file_name}_{color_type}_{backend}_{sat}_{file_size}_{__cache_version__}.json",
    ]


def get_backend(backend: str):
    if backend == "random":
        backends = list_backends()
        random.shuffle(backends)
        return backends[0]

    return backend


def palette():
    for i in range(16):
        if i % 8 == 0:
            print()

        if i > 7:
            i = f"8;5;{i}"

        print("\033[4%sm%s\033[0m" % (i, " " * (80 // 20)), end="")

    print("\n")


def get(img: str, light: bool | str = False, backend: str = "wal", cache_dir: str = CACHE_DIR, sat: str = "",):
    cache_name = cache_frame(img, backend, light, cache_dir, sat)
    cache_file = os.path.join(*cache_name)

    if os.path.isfile(cache_file):
        colors = theme.file(cache_file)
        colors["alpha"] = utils.Color.alpha_num
        logging.info("Found cached colorscheme.")

    else:
        logging.info("Generating a colorscheme.")
        backend = get_backend(backend)

        # Dynamically import the backend we want to use.
        # This keeps the dependencies "optional".
        try:
            __import__(f"pywal.backends.{backend}")
        except ImportError:
            __import__("pywal.backends.wal")
            backend = "wal"

        logging.info(f"Using {backend} backend.")
        backend = sys.modules[f"pywal.backends.{backend}"]
        colors = getattr(backend, "get")(img, light)
        colors = format_colors(saturate_colors(colors, sat), img)

        utils.save_file_json(colors, cache_file)
        logging.info("Generation complete.")

    return colors
