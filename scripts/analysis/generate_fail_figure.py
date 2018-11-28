#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert summary data to a bar plot with failure rates.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import json
import argparse
import os

from .core import (
    CORPUS_NAMES,
    DETECTOR_NAMES,
    ORDERED_DETECTORS,
    check_detectors,
)
from .latex import build_latex_doc

BAR_PATTERNS = [
    "north east lines",
    "none",
    "north west lines",
    "horizontal lines",
    "vertical lines",
    "grid",
    "crosshatch",
]


def clean_name(detector):
    abbr = DETECTOR_NAMES.get(detector, detector)
    return abbr.replace("_", "\\_")


def create_fail_graph(results, output_file):
    fail_data = {corpus: results[corpus]["failures"] for corpus in results}
    for corpus in fail_data:
        check_detectors(fail_data[corpus].keys())

    abbrev = [clean_name(d) for d in ORDERED_DETECTORS]
    tex = (
        "\\documentclass[preview=true]{standalone}\n"
        "\\usepackage{tikz}\n"
        "\\usepackage{pgfplots}\n"
        "\\usetikzlibrary{patterns}\n"
        "\\pgfplotsset{compat=1.16}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\n"
        "\\begin{axis}[\n"
        "\tybar,\n"
        "\twidth={600},\n"
        "\theight={200},\n"
        "\tymin=0,\n"
        "\tlegend pos={north east},\n"
        "\tylabel={Failure (\\%%)},\n"
        "\tsymbolic x coords={%s},\n"
        "\txtick=data,\n"
        "\tnodes near coords,\n"
        "\tevery node near coord/.append style={font=\\tiny, /pgf/number format/fixed},\n"
        "\tnodes near coords align={vertical},\n"
        "\t]\n" % ",".join(abbrev)
    )

    corpora = sorted(fail_data.keys())

    for pattern, corpus in zip(BAR_PATTERNS, corpora):
        line = "\\addplot[postaction={pattern=%s}] coordinates {" % pattern
        for detector in ORDERED_DETECTORS:
            line += "(%s,%.16f) " % (
                clean_name(detector),
                fail_data[corpus][detector] * 100.0,
            )
        line += "};\n"
        tex += line

    tex += "\\legend{%s}\n" % ", ".join([CORPUS_NAMES.get(c) for c in corpora])

    tex += "\\end{axis}\n" "\\end{tikzpicture}\n" "\\end{document}"

    tex_file = os.path.splitext(output_file)[0] + ".tex"
    with open(tex_file, "w") as fid:
        fid.write(tex)

    build_latex_doc(tex, output_name=output_file)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", dest="output", help="Output pdf file to write to", required=True
    )
    parser.add_argument(
        "-s",
        dest="summaries",
        help="Summary file with the results",
        required=True,
        nargs="+",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    all_data = {}
    for summary_file in args.summaries:
        with open(summary_file, "r") as fid:
            data = json.load(fid)
        all_data[data["corpus"]] = data

    create_fail_graph(all_data, args.output)

