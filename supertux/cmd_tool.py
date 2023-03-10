import io
import sexp
import sys

import argparse

from typing import Callable, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SuperTux Origins data tool")

    parser.add_argument("COMMAND", type=str)
    parser.add_argument("FILE", action="append", nargs="+")
    parser.add_argument("--in-place", action="store_true", default=False,
                        help="Modify file in place")

    return parser.parse_args()


def get_int_value(objs: sexp.Value, name: str) -> Optional[int]:
    for kv_pair in objs[1:]:
        if kv_pair.is_array() and str(kv_pair[0]) == name:
            return kv_pair[1].value
    return []


def pretty_print(sx: sexp.Value, indent: int, fout):
    _pretty_print("", [], sx, 1, indent, fout)
    fout.write("\n")


def _pretty_print(path: list, stack: list, sx: sexp.Value, depth: int, indent: int, fout):
    width_hint = None
    if path == "supertux-level.sectors.sector.objects.tilemap" and str(sx[0]) == "tiles":
        width_hint = get_int_value(stack[-2], 'width')

    if not sx.is_array():
        fout.write(str(sx))
    else:  # sx.is_array()
        if path == "":
            path = str(sx[0])
        else:
            path += "." + str(sx[0])

        fout.write("(")
        fout.write(str(sx[0]))

        if len(sx) > 1 and sx[1].is_array() and sx[1][0].value != "_":
            fout.write("\n")
            for i in range(1, len(sx)):
                if sx[i].is_array():
                    fout.write(depth * indent * " ")
                    _pretty_print(path, stack + [sx[i]], sx[i], depth + 1, indent, fout)
                else:
                    fout.write(depth * indent * " ")
                    fout.write(str(sx[i]))

                if i != len(sx) - 1:
                    fout.write("\n")

            fout.write("\n" + (depth - 1) * indent * " " + ")")
        else:
            multiline_array = len(sx) > 2 and sx[1].is_string()

            if multiline_array:
                fout.write("\n")
                for i in range(1, len(sx)):
                    fout.write(depth * indent * " ")
                    fout.write(str(sx[i]))
                    fout.write("\n")

                fout.write((depth - 1) * indent * " ")
                fout.write(")")
            else:
                if width_hint is None:
                    for i in range(1, len(sx)):
                        fout.write(" ")
                        fout.write(str(sx[i]))
                    fout.write(")")
                else:
                    fout.write("\n")
                    column_count = 0
                    fout.write(depth * indent * " ")
                    for i in range(1, len(sx)):
                        fout.write(str(sx[i]))
                        fout.write(" ")
                        column_count += 1
                        if column_count == width_hint:
                            fout.write("\n")
                            fout.write(depth * indent * " ")
                            column_count = 0
                    fout.write(")")


def dispatch_file(filename: str, opts: argparse.Namespace) -> None:
    if filename.endswith(".sprite"):
        handle_sprite(filename, opts)
    elif filename.endswith(".stl") or filename.endswith(".stlv"):
        handle_level(filename, opts)
    else:
        raise RuntimeError(f"{filename}: unhandled file type")


def sprite_move_action_to_actions(sx: sexp.Value) -> sexp.Value:
    metadata = [x for x in sx[1:] if str(x[0]) not in ["action", "version"]]
    actions = [x for x in sx[1:] if str(x[0]) in ["action"]]

    return sexp.Array(
        [sx[0]] +
        [sexp.Array([sexp.Symbol("version"), sexp.Integer(2)])] +
        metadata +
        [sexp.Array([sexp.Symbol("actions")] + actions)]
    )


def handle_sprite(filename: str, opts: argparse.Namespace) -> None:
    sxs = sexp.Parser.from_file(filename)
    assert len(sxs) == 1
    sx = sxs[0]
    assert str(sx[0]) == "supertux-sprite"

    sx = sprite_move_action_to_actions(sx)

    if opts.in_place:
        print(f"{filename}: modifying in place")
        with io.StringIO() as strio:
            pretty_print(sx, 2, strio)
            with open(filename, "w") as fout:
                fout.write(strio.getvalue())
    else:
        print(f";; {filename}")
        pretty_print(sx, 2, sys.stdout)

def filter_sx_array(sx: sexp.Value, pred: Callable[[sexp.Value], bool]) -> sexp.Value:
    return sexp.Array(
        [x for x in sx if pred(x)]
    )


def level_move_sector_to_sectors(sx: sexp.Value) -> sexp.Value:
    supertux_level_tag = sx[0]
    metadata = [x for x in sx[1:] if str(x[0]) not in ["sectors", "version"]]
    # sectors = [x for x in sx[1:] if str(x[0]) in ["sector"]]
    sectors = [x for x in sx[1:] if str(x[0]) in ["sectors"]][0][1:]

    for idx, sector in enumerate(sectors):
        sector_metadata = [x for x in sector[1:] if str(x[0]) in ["name", "init-script"]]
        sector_objects = [x for x in sector[1:] if str(x[0]) not in ["name", "init-script"]]
        sectors[idx] = sexp.Array([sexp.Symbol("sector")] +
                                  sector_metadata +
                                  [sexp.Array([sexp.Symbol("objects")] +
                                              sector_objects)])

    return sexp.Array(
        [supertux_level_tag] +
        [sexp.Array([sexp.Symbol("version"), sexp.Integer(4)])] +
        metadata +
        [sexp.Array(
            [sexp.Symbol("sectors")] +
            sectors)])


def handle_level(filename: str, opts: argparse.Namespace) -> None:
    sxs = sexp.Parser.from_file(filename)
    assert len(sxs) == 1
    sx = sxs[0]
    assert str(sx[0]) == "supertux-level"

    sx = level_move_sector_to_sectors(sx)

    if opts.in_place:
        print(f"{filename}: modifying in place")
        with io.StringIO() as strio:
            pretty_print(sx, 2, strio)
            with open(filename, "w") as fout:
                fout.write(strio.getvalue())
    else:
        print(f";; {filename}")
        pretty_print(sx, 2, sys.stdout)


def main():
    opts = parse_args()
    if opts.COMMAND == "refactor":
        for filename in opts.FILE[0]:
            dispatch_file(filename, opts)

# EOF #
