#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create box plots for runtime.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import json
import numpy as np
import os

from .core import ORDERED_DETECTORS, check_detectors, clean_detector_name
from .latex import build_latex_doc


def create_box_and_whisker_plot(runtimes, output_file):
    check_detectors(runtimes.keys())
    abbrev = [clean_detector_name(d) for d in ORDERED_DETECTORS]

    xtick = ",".join([str(i + 1) for i in range(len(abbrev))])
    xticklabels = ",".join(abbrev)

    tex = (
        "\\documentclass[preview=true]{standalone}\n"
        "\\usepackage{tikz}\n"
        "\\usepackage{pgfplots}\n"
        "\\pgfplotsset{compat=1.16}\n"
        "\\usepgfplotslibrary{statistics}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\n"
        "\\begin{semilogyaxis}[\n"
        "boxplot/draw direction=y,\n"
        "xtick={%s},\n"
        "xticklabels={%s},\n"
        "ylabel={Runtime (s)},\n"
        "width=500pt,\n"
        "height=200pt\n"
        "]\n" % (xtick, xticklabels)
    )

    for detector in ORDERED_DETECTORS:
        rt = runtimes[detector]
        q1, median, q3 = np.percentile(rt, [25, 50, 75])
        upper_whisker = max(rt)
        lower_whisker = min(rt)
        boxplot_tex = (
            "\\addplot+[\n"
            "\tdraw=black,\n"
            "\tsolid,\n"
            "\tboxplot prepared={\n"
            "\t\tmedian=%f,\n"
            "\t\tlower quartile=%f,\n"
            "\t\tupper quartile=%f,\n"
            "\t\tupper whisker=%f,\n"
            "\t\tlower whisker=%f\n"
            "},\n"
            "] coordinates {};\n"
            % (median, q1, q3, upper_whisker, lower_whisker)
        )
        tex += boxplot_tex

    tex += "\\end{semilogyaxis}\n" "\\end{tikzpicture}\n" "\\end{document}"

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
        dest="summary",
        help="Summary file with the input data",
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.summary, "r") as fid:
        summary = json.load(fid)

    create_box_and_whisker_plot(summary["runtimes"], args.output)
