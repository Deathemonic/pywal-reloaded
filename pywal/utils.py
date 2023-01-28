"""
Helper functions and classes.
"""

import colorsys
import logging
import numpy as np
import struct
import subprocess
import os

from json import load, dump
from pathlib import PosixPath, Path
from platform import system
from shutil import which
from sys import stdout


class Color:
    alpha_num = '100'
    
    def __init__(self, hex_color: str) -> None:
        self.hex_color = hex_color
        
    def __str__(self) -> str:
        return self.hex_color
    
    @property
    def rgb(self) -> str:
        return ','.join(map(str, hex_to_rgb(self.hex_color)))
    
    @property
    def xrgba(self) -> str:
        return hex_to_xrgba(self.hex_color)
    
    @property
    def rgba(self) -> str:
        r, g, b = hex_to_rgb(self.hex_color)
        return f'rgba({r}, {g}, {b}, {self.alpha_dec})'
    
    @property
    def alpha(self) -> str:
        return f"[{self.alpha_num}]{self.hex_color}"            
    
    @property
    def alpha_dec(self) -> float:
        return int(self.alpha_num) / 100

    @property
    def decimal(self) -> str:
        return f"#{int(self.hex_color.strip('#'), 16)}"
    
    @property
    def decimal_strip(self) -> float:
        return int(self.hex_color.strip('#'), 16)
    
    @property
    def octal(self) -> str:
        return f"#{oct(int(self.hex_color.strip('#'), 16))[2:]}"

    @property
    def octal_strip(self) -> str:
        return oct(int(self.hex_color.strip('#'), 16))[2:]
    
    @property
    def strip(self) -> str:
        return self.hex_color.strip('#')
    
    @property
    def red(self) -> str:
        return f'{hex_to_rgb(self.hex_color)[0]/255.:.3f}'

    @property
    def green(self) -> str:
        return f'{hex_to_rgb(self.hex_color)[1]/255.:.3f}'

    @property
    def blue(self) -> str:
        return f'{hex_to_rgb(self.hex_color)[3]/255.:.3f}'
    
    def darken(self, percent: int | float):
        percent = int(percent * 100) if type(percent) is float else percent
        return Color(brighten_color(self.hex_color, percent, False))
    
    def lighten(self, percent: int | float):
        percent = int(percent * 100) if type(percent) is float else percent
        return Color(brighten_color(self.hex_color, percent, True))
        
    def saturate(self, percent: int | float):
        percent = int(percent * 100) if type(percent) is float else percent
        return Color(saturate_color(self.hex_color, percent))


def hex_to_rgb(color: str) -> tuple:
    return struct.unpack('BBB', bytes.fromhex(color.strip('#')))


def hex_to_xrgba(color: str) -> str:
    col = color.lower().strip('#')
    return f'{col[:2]}/{col[2:4]}/{col[4:6]}/ff'


def hex_to_yiq(color: str) -> tuple:
    r, g, b = hex_to_rgb(color)
    y, i, q = colorsys.rgb_to_yiq(r, g, b)
    return np.around(y, decimals=2), np.around(i, decimals=2), np.around(q, decimals=2)


def rgb_to_hex(color: tuple) -> str:
    return '#' + ''.join(f'{x:02x}' for x in color)


def brighten_color(hex: str, amount: float, brighten: bool) -> str:
    color = tuple(min(255, col + amount) if brighten else max(1, col - amount) for col in hex_to_rgb(hex))
    return rgb_to_hex(color)


def saturate_color(color: str, amount: float) -> str:
    r, g, b = hex_to_rgb(color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    s = amount / 100
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((int(r*255), int(g*255), int(b*255)))


def blend_color(color: str, color2: str) -> str:
    r1, g1, b1 = hex_to_rgb(color)
    r2, g2, b2 = hex_to_rgb(color2)

    r3 = int(0.5 * r1 + 0.5 * r2)
    g3 = int(0.5 * g1 + 0.5 * g2)
    b3 = int(0.5 * b1 + 0.5 * b2)

    return rgb_to_hex((r3, g3, b3))


def setup_logging():
    try:
        from rich.logging import RichHandler
        logging.basicConfig(format='%(message)s', level=logging.INFO, datefmt='[%X]', handlers=[RichHandler(rich_tracebacks=True)])
        logging.getLogger('rich')
    except ImportError:
        format = '[%(levelname)s\033[0m] \033[1;31m%(module)s\033[0m: %(message)s'
        logging.basicConfig(format=format, level=logging.INFO, stream=stdout)
        logging.addLevelName(logging.ERROR, '\033[1;31mE')
        logging.addLevelName(logging.INFO, '\033[1;32mI')
        logging.addLevelName(logging.WARNING, '\033[1;33mW')


def create_dir(path: Path | str):
   PosixPath(path).mkdir(parents=True, exist_ok=True) 


def read_file(input_file):
    with open(input_file, 'r') as file:
        return file.read().splitlines()


def read_file_json(input_file):
    with open(input_file, 'r') as json_file:
        return load(json_file)


def read_file_raw(input_file):
    with open(input_file, 'r') as file:
        return file.readlines()


def save_file(data, export_file):
    create_dir(os.path.dirname(export_file))

    try:
        with open(export_file, 'w') as file:
            file.write(data)
    except PermissionError:
        logging.warning(f"Couldn't write to {export_file}")


def save_file_json(data, export_file):
    create_dir(os.path.dirname(export_file))
    with open(export_file, "w") as file:
        dump(data, file, indent=4)


def disown(cmd: str):
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def get_pid(name: str) -> bool:
    if not which("pidof"):
        return False

    try:
        subprocess.check_output(["pidof", "-s", name]) if system() != 'Darwin' else subprocess.check_output(['pidof', name])
    except subprocess.CalledProcessError:
        return False
    return True
