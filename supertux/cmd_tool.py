import sexp
import sys

import argparse

from typing import Callable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SuperTux Origins data tool")

    parser.add_argument("COMMAND", type=str)
    parser.add_argument("FILE", action="append", nargs="+")
    parser.add_argument("--dump", action="store_true", default=False)

    return parser.parse_args()


def dispatch_file(filename: str) -> None:
    if filename.endswith(".sprite"):
        handle_sprite(filename)
    elif filename.endswith(".stl"):
        handle_level(filename)
    else:
        raise RuntimeError(f"{filename}: unhandled file type")


def sprite_move_action_to_actions(sx: sexp.Value) -> sexp.Value:
    return sexp.Array([
        sx[0],
        sexp.Array([sexp.Symbol("version"), sexp.Integer(2)]),
        sexp.Array([sexp.Symbol("actions")] + sx[1:])
    ])


def handle_sprite(filename: str) -> None:
    sxs = sexp.Parser.from_file(filename)
    assert len(sxs) == 1
    sx = sxs[0]
    assert str(sx[0]) == "supertux-sprite"

    sx = sprite_move_action_to_actions(sx)

    sexp.pretty_print(sx, 2, sys.stdout)


def filter_sx_array(sx: sexp.Value, pred: Callable[[sexp.Value], bool]) -> sexp.Value:
    return sexp.Array(
        [x for x in sx if pred(x)]
    )


def level_move_sector_to_sectors(sx: sexp.Value) -> sexp.Value:
    supertux_level_tag = sx[0]
    metadata = [x for x in sx[1:] if str(x[0]) not in ["sector", "version"]]
    sectors = [x for x in sx[1:] if str(x[0]) in ["sector"]]

    return sexp.Array(
        [supertux_level_tag] +
        [sexp.Array([sexp.Symbol("version"), sexp.Integer(4)])] +
        metadata +
        [sexp.Array(
            [sexp.Symbol("sectors")] +
            sectors)])


def handle_level(filename: str) -> None:
    sxs = sexp.Parser.from_file(filename)
    assert len(sxs) == 1
    sx = sxs[0]
    assert str(sx[0]) == "supertux-level"

    sx = level_move_sector_to_sectors(sx)

    # print(sx)
    sexp.pretty_print(sx, 2, sys.stdout)


def main():
    opts = parse_args()

    if opts.COMMAND == "show":
        for filename in opts.FILE[0]:
            dispatch_file(filename)

# EOF #
