import logging
import typing

from . import types

logger = logging.getLogger("super_prompt_color")

def reset_color() -> str:
    return "\033[0m"

def ansi_color(color_code: int) -> str:
    if color_code in range(30, 38) or color_code in range(40, 48):
        return f"\033[{color_code}m"
    logger.error("Invalid color code %d", color_code)
    return reset_color()
    
def rgb_color(R:int, G: int, B:int) -> str:
    if all([
        R in range(0, 256),
        G in range(0, 256),
        B in range(0, 256)
    ]):
        return f"\033[38;2;{R};{G};{B}m"
    return reset_color()

def color(color_spec: typing.Optional[types.Color]) -> str:
    if color_spec is None:
        return ""
    if isinstance(color_spec, int):
        return ansi_color(color_spec)
    return rgb_color(**color_spec)
