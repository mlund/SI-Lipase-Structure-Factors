#!/usr/bin/env python3
"""plot_csv.py - quick XY plots from one or more CSV / whitespace data files.

A self-contained command-line plotter built on matplotlib + numpy. Point it at
one or more data files, pick the X,Y columns to draw, and it either opens an
interactive window or writes an image (-o).

Gist:    https://gist.github.com/mlund/e1a7a530a84aef60b3e1cafdd726f9f3

Requirements
------------
    Python 3.7+, numpy, matplotlib    (pip install numpy matplotlib)

Run with uv (recommended)
-------------------------
Dependencies are declared inline (PEP 723 block below), so uv resolves and
caches them automatically - no manual install or virtualenv needed:

    uv run plot_csv.py --file data.csv          # local copy
    uv run https://gist.githubusercontent.com/mlund/e1a7a530a84aef60b3e1cafdd726f9f3/raw/plot_csv.py --file data.csv

Make `./plot_csv.py` self-bootstrapping under uv by switching the shebang to:

    #!/usr/bin/env -S uv run --script

Install as a command (uv tool)
------------------------------
With the accompanying pyproject.toml, install a persistent `plot_csv` command:

    uv tool install .                  # from a checkout containing pyproject.toml
    plot_csv --file data.csv

    uvx --from . plot_csv --file data.csv     # run once without installing

Install (plain Python)
----------------------
The script is a single self-contained file; download it and make it
executable. From the gist (raw URL):

    curl -L https://gist.githubusercontent.com/mlund/e1a7a530a84aef60b3e1cafdd726f9f3/raw/plot_csv.py -o plot_csv.py
    chmod +x plot_csv.py
    ./plot_csv.py --file data.csv               # needs numpy + matplotlib on PATH

To put it on your PATH, drop it in a bin directory, e.g.:

    install -m 755 plot_csv.py ~/.local/bin/plot_csv    # then: plot_csv --file data.csv

Or fetch a specific revision with the gh CLI:

    gh gist clone e1a7a530a84aef60b3e1cafdd726f9f3

Per-file model
--------------
Each input is introduced with --file. The per-file options --use and --yscale
attach to the *most recently named* file, so different files can be drawn with
different columns and scales:

    --file a.csv --use 0,1 --yscale 2 --file b.csv --use 0,2
                \\-- apply to a.csv --/          \\-- b.csv --/

Defaults per file: --use 0,1 (first two columns) and --yscale 1.0 (no scaling).
--use may be repeated to draw several curves from the same file.

Input format
------------
- Delimiter is auto-detected per file: comma if the first data line contains
  one, otherwise any run of whitespace. Override with -d/--delimiter.
- A non-numeric first row is treated as a header and used for legend / axis
  labels; otherwise columns are labelled "col 0", "col 1", ...
- Lines beginning with '#' are ignored.

Columns are 0-indexed. An axis is labelled from the header when every curve
shares the same column for it; otherwise it gets a generic "X" / "Y" label.

Options
-------
    --file FILE        input data file (repeatable; required)
    --use X,Y          column pair for the preceding file (repeatable; def 0,1)
    --yscale F         multiply the preceding file's Y by F (default 1.0)
    -d, --delimiter D  force a column delimiter (default: auto-detect)
    -s, --style S      matplotlib format string: 'o', '-', 'o-' (default 'o')
    --logx / --logy    log-scale the X / Y axis
    -o, --output FILE  save the figure (png/pdf/svg by extension) instead of
                       opening a window
    -h, --help         show argparse usage and exit

Examples
--------
    # single file, default columns 0,1, interactive window
    plot_csv.py --file data.csv

    # two curves from one file, save to PNG
    plot_csv.py --file data.csv --use 0,1 --use 0,4 -o plot.png

    # overlay two files with different columns, lines+markers
    plot_csv.py --file a.csv --use 0,1 --file b.dat --use 0,2 -s o-

    # scale one dataset and use a log-log plot (e.g. scattering I(q))
    plot_csv.py --file calc.dat --yscale 1e3 --file expt.csv --logx --logy
"""

# PEP 723 inline script metadata - read by `uv run` to build the environment.
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "numpy",
#     "matplotlib",
# ]
# ///

import argparse
import os
import sys
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class FileSpec:
    """A file plus its per-file plotting options."""

    path: str
    uses: list = field(default_factory=list)  # list of (x, y) column pairs
    yscale: float = 1.0


def column_pair(text):
    """argparse type: parse a 'X,Y' argument into an (x, y) tuple of column indices."""
    try:
        x, y = (int(c) for c in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected 'X,Y' column pair, got {text!r}")
    return x, y


class AddFile(argparse.Action):
    """Start a new FileSpec; subsequent per-file options attach to it."""

    def __call__(self, parser, namespace, value, option_string=None):
        files = getattr(namespace, self.dest) or []
        files.append(FileSpec(path=value))
        setattr(namespace, self.dest, files)


class _PerFile(argparse.Action):
    """Base for options that modify the most recently added file."""

    def files(self, parser, namespace):
        files = getattr(namespace, "files", None)
        if not files:
            parser.error(f"{self.option_strings[0]} must follow --file")
        return files


class AppendForLastFile(_PerFile):
    """Append the parsed value to a list attribute on the most recent file."""

    def __call__(self, parser, namespace, value, option_string=None):
        getattr(self.files(parser, namespace)[-1], self.dest).append(value)


class SetForLastFile(_PerFile):
    """Set a scalar attribute on the most recent file."""

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(self.files(parser, namespace)[-1], self.dest, value)


def build_parser():
    # Show the full module docstring (verbatim) as the --help description.
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--file",
        dest="files",
        action=AddFile,
        metavar="FILE",
        required=True,
        help="input CSV/data file (repeatable; per-file --use/--yscale follow it)",
    )
    p.add_argument(
        "--use",
        dest="uses",
        action=AppendForLastFile,
        type=column_pair,
        metavar="X,Y",
        help="column pair to plot for the preceding file (repeatable; default: 0,1)",
    )
    p.add_argument(
        "--yscale",
        dest="yscale",
        action=SetForLastFile,
        type=float,
        metavar="F",
        help="scale the preceding file's y values (default: 1.0)",
    )
    p.add_argument(
        "-d",
        "--delimiter",
        help="column delimiter (default: auto-detect comma or whitespace)",
    )
    p.add_argument(
        "-s",
        "--style",
        default="o",
        help="matplotlib format string, e.g. 'o', '-', 'o-' (default: 'o')",
    )
    p.add_argument("--logx", action="store_true", help="log-scale the x axis")
    p.add_argument("--logy", action="store_true", help="log-scale the y axis")
    p.add_argument(
        "-o", "--output", help="save figure to file instead of showing a window"
    )
    return p


def _is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def load(filename, delimiter):
    """Return (data, header) for a file, auto-detecting delimiter and header."""
    # Read the first non-empty/non-comment line to detect delimiter and header.
    with open(filename) as f:
        for line in f:
            if line.strip() and not line.lstrip().startswith("#"):
                break
        else:
            line = ""

    # Auto-detect delimiter: comma if present, else any whitespace (None).
    if delimiter is None:
        delimiter = "," if "," in line else None
    first = line.strip().split(delimiter)
    has_header = any(not _is_float(c) for c in first)
    header = [c.strip() for c in first] if has_header else None

    data = np.genfromtxt(
        filename, delimiter=delimiter, skip_header=has_header, comments="#"
    )
    if data.ndim == 1:  # single row or single column
        data = data.reshape(1, -1) if data.shape[0] else data
    return data, header


def main(argv=None):
    args = build_parser().parse_args(argv)
    # Files without an explicit --use default to columns 0,1.
    for f in args.files:
        f.uses = f.uses or [(0, 1)]

    multi = len(args.files) > 1
    xcols, ycols = set(), set()
    xlabel = ylabel = None
    for f in args.files:
        data, header = load(f.path, args.delimiter)

        def name(i):
            return header[i] if header and i < len(header) else f"col {i}"

        prefix = f"{os.path.basename(f.path)}: " if multi else ""
        for x, y in f.uses:
            label = f"{prefix}{name(y)} vs {name(x)}"
            if f.yscale != 1.0:
                label += f" (×{f.yscale:g})"
            plt.plot(data[:, x], data[:, y] * f.yscale, args.style, label=label)
            xcols.add(x)
            ycols.add(y)
            if xlabel is None:
                xlabel = name(x)
            if ylabel is None:
                ylabel = name(y)

    # Label each axis from the header when a single column is shared by all curves.
    plt.xlabel(xlabel if len(xcols) == 1 and xlabel else "X")
    plt.ylabel(ylabel if len(ycols) == 1 and ylabel else "Y")
    if args.logx:
        plt.xscale("log")
    if args.logy:
        plt.yscale("log")
    plt.legend()
    plt.tight_layout()

    if args.output:
        plt.savefig(args.output, dpi=150)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        plt.show()


if __name__ == "__main__":
    main()
