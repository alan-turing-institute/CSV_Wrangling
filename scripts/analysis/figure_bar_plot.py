#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert summary data to a bar plot.

Author: Gertjan van den Burg

"""

import json
import os
import argparse

from .core import (
    ORDERED_DETECTORS,
    ORDERED_PROP,
    check_detectors,
    clean_detector_name,
)
from .latex import build_latex_doc


def create_prop_graph(results, output_file):
    for prop in results:
        check_detectors(results[prop].keys())

    abbrev = [clean_detector_name(d) for d in ORDERED_DETECTORS]
    tex = (
        "\\documentclass[preview=true]{standalone}\n"
        "\\pdfinfoomitdate=1\n"
        "\\pdftrailerid{}\n"
        "\\pdfsuppressptexinfo=1\n"
        "\\usepackage{tikz}\n"
        "\\usepackage{pgfplots}\n"
        "\\pgfplotsset{compat=1.16}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\n"
        "\\begin{axis}[\n"
        "\tybar,\n"
        "\twidth={400},\n"
        "\theight={200},\n"
        "\tymin=0,\n"
        "\tlegend style={at={(0.5,-0.15)}, anchor=north, legend columns=-1},\n"
        "\tylabel={Accuracy (\\%%)},\n"
        "\tsymbolic x coords={%s},\n"
        "\txtick=data,\n"
        "\tnodes near coords,\n"
        "\tnodes near coords align={vertical},\n"
        "\tevery node near coord/.append style={font=\\tiny},\n"
        "\t]\n" % ",".join(abbrev)
    )
    for prop in ORDERED_PROP:
        line = "\\addplot coordinates {"
        for detector in ORDERED_DETECTORS:
            line += "(%s,%.16f) " % (
                clean_detector_name(detector),
                results[prop][detector],
            )
        line += "};\n"

        tex += line

    tex += "\\legend{%s}\n" % ",".join(ORDERED_PROP)
    tex += "\\end{axis}\n" "\\end{tikzpicture}\n" "\\end{document}"

    tex_file = os.path.splitext(output_file)[0] + ".tex"
    with open(tex_file, "w") as fid:
        fid.write(tex)

    build_latex_doc(tex, output_name=output_file)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "type",
        choices=["all", "human", "normal"],
        help="Subset of data to generate plot for",
        default="all",
    )
    parser.add_argument(
        "-o", dest="output", help="Output pdf file to write to", required=True
    )
    parser.add_argument(
        "-s",
        dest="summary",
        help="Summary file with the results",
        required=True,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.summary, "r") as fid:
        data = json.load(fid)

    key = "detection_accuracy_" + args.type
    if not key in data:
        raise ValueError("Can't find key %s in file %s" % (key, args.summary))

    create_prop_graph(data[key], args.output)
