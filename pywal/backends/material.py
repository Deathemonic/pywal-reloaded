""" This doesn't work, because it's just a template for now """

import json
import logging
import os

import globals

if globals.USER_HAS_COLR:
    import colr
from . import color_utils
from . import math_utils
from .extra_image_utils import sourceColorsFromImage
from material_color_utilities_python.utils.theme_utils import *


def dict_to_rgb(dark_scheme):
    return {key: hexFromArgb() for key, color in dark_scheme.items()}


def tones_from_palette(palette):
    return {x: palette.tone for x in range(100)}


def get_custom_colors(custom_colors):
    value = hexFromArgb(custom_color['color']['value'])
    return {
        value: {
            'color': dict_to_rgb(custom_color['color']),
            'value': hexFromArgb(custom_color['value']),
            'light': dict_to_rgb(custom_color['light']),
            'dark': dict_to_rgb(custom_color['dark']),
        } for custom_color in custom_colors
    }


def get_image(wallpaper):
    img = Image.open(wallpaper)
    # resize image proportionally
    img = img.resize((64, int((float(img.size[1]) * float((64 / float(img.size[0])))))), Image.Resampling.LANCZOS)
    # get best colors
    source_colors = sourceColorsFromImage(img, top=False)
    # close image file
    img.close()
    return source_colors[0]


def assign_pallete(theme, best_colors, seedNo):
    dark_scheme = json.loads(theme['schemes']['dark'].toJSON())
    light_scheme = json.loads(theme['schemes']['light'].toJSON())
    primary_palete = theme['palettes']['primary']
    secondary_palete = theme['palettes']['secondary']
    tertiary_palete = theme['palettes']['tertiary']
    neutral_palete = theme['palettes']['neutral']
    neutral_variant_palete = theme['palettes']['neutralVariant']
    error_palette = theme['palettes']['error']
    custom_colors = theme['customColors']

    return {
        'best': best_colors,
        'seed': {
            seedNo: hexFromArgb(theme['source']),
        },
        'schemes': {
            'light': dict_to_rgb(light_scheme),
            'dark': dict_to_rgb(dark_scheme),
        },
        'palettes': {
            'primary': dict_to_rgb(tones_from_palette(primary_palete)),
            'secondary': dict_to_rgb(tones_from_palette(secondary_palete)),
            'tertiary': dict_to_rgb(tones_from_palette(tertiary_palete)),
            'neutral': dict_to_rgb(tones_from_palette(neutral_palete)),
            'neutralVariant': dict_to_rgb(tones_from_palette(neutral_variant_palete)),
            'error': dict_to_rgb(tones_from_palette(error_palette)),
        },
        'custom': [
            get_custom_colors(custom_colors)
        ]
    }


def get_material_you_colors(wallpaper_data, ncolor, source_type):
    """
        Get material you colors from wallpaper or hex color using material-color-utility

        Args:
            wallpaper_data (tuple): wallpaper (type and data)
            ncolor (int): Alternative color number flag passed to material-color-utility
            source_type (str): image or color string passed to material-color-utility
        Returns:
            str: string data from python-material-color-utilities
    """

    try:
        seed_color = get_image(wallpaper_data) if source_type == "image" else argbFromHex(wallpaper_data)
        source_colors = [seed_color] if seed_color else 0

        # best colors
        best_colors = {str(i): hexFromArgb(color) for i, color in enumerate(source_colors)}
        # generate theme from seed color
        theme = themeFromSourceColor(seed_color)
        # Given a image, the alt color and hex color
        # return a selected color or a single color for hex code
        totalColors = len(best_colors)
        ncolor = 0 if not ncolor or ncolor is None else math_utils.clip(ncolor, 0, totalColors, 0)
        seedColor = hexFromArgb(source_colors[ncolor]) if totalColors > ncolor else hexFromArgb(source_colors[-1])
        seedNo = ncolor if totalColors > ncolor else seedNo = totalColors-1

        if seedColor != 0:
            theme = themeFromSourceColor(argbFromHex(seedColor))
            return assign_pallete(theme, best_colors, seedNo)

    except Exception as e:
        logging.error(
            f'Error trying to get colors from {wallpaper_data}:\n{e}')
        return None


def get_color_schemes(wallpaper, ncolor=None):
    """
        Display best colors, allow to select alternative color,
        and make and apply color schemes for dark and light mode

        Args:
            wallpaper (tuple): wallpaper (type and data)
            light (bool): wether use or not light scheme
            ncolor (int): Alternative color number flag passed to material-color-utility
    """
    if wallpaper != None:
        materialYouColors = None
        wallpaper_type = wallpaper[0]
        wallpaper_data = wallpaper[1]
        if wallpaper_type == "image":
            source_type = "image"
            if os.path.exists(wallpaper_data):
                if not os.path.isdir(wallpaper_data):
                    # get colors from material-color-utility
                    materialYouColors = get_material_you_colors(
                        wallpaper_data, ncolor=ncolor, source_type=source_type)
                else:
                    logging.error(
                        f'"{wallpaper_data}" is a directory, aborting')

        elif wallpaper_type == "color":
            source_type = "color"
            wallpaper_data = color_utils.color2hex(wallpaper_data)
            materialYouColors = get_material_you_colors(
                wallpaper_data, ncolor=ncolor, source_type=source_type)

        if materialYouColors != None:
            try:
                if len(materialYouColors['best']) > 1:
                    best_colors = f'Best colors: {globals.TERM_STY_BOLD}'

                    for index, col in materialYouColors['best'].items():
                        if globals.USER_HAS_COLR:
                            best_colors += f'{globals.TERM_COLOR_DEF+globals.TERM_STY_BOLD}{index}:{colr.color(col,fore=col)}'
                        else:
                            best_colors += f'{globals.TERM_COLOR_DEF+globals.TERM_STY_BOLD}{index}:{globals.TERM_COLOR_WHI}{col}'
                        if int(index) < len(materialYouColors['best'])-1:
                            best_colors = best_colors+","
                    logging.info(best_colors)

                seed = materialYouColors['seed']
                sedColor = list(seed.values())[0]
                seedNo = list(seed.keys())[0]
                if globals.USER_HAS_COLR:
                    logging.info(
                        f'Using seed: {globals.TERM_COLOR_DEF+globals.TERM_STY_BOLD}{seedNo}:{colr.color(sedColor, fore=sedColor)}')
                else:
                    logging.info(
                        f'Using seed: {globals.TERM_COLOR_DEF+globals.TERM_STY_BOLD}{seedNo}:{globals.TERM_COLOR_WHI}{sedColor}')

                return materialYouColors

            except Exception as e:
                logging.error(f'Error:\n{e}')
                return None

    else:
        logging.error(
            f'''Error: Couldn't set schemes with "{wallpaper_data}"''')
        return None


def export_schemes(schemes):
    """Export generated schemes to MATERIAL_YOU_COLORS_JSON
    Args:
        schemes (ThemeConfig): generated color schemes
    """
    colors = schemes.get_material_schemes()
    colors.update({
        "extras": schemes.get_extras(),
        "pywal": {
            "light": schemes.get_wal_light_scheme(),
            "dark": schemes.get_wal_dark_scheme()
        }
    })

    with open(globals.MATERIAL_YOU_COLORS_JSON, 'w', encoding='utf8') as material_you_colors:
        json.dump(colors, material_you_colors, indent=4, ensure_ascii=False)