#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creating violin plots in PGFplots (two-sided version)

Based on:
https://matplotlib.org/_modules/matplotlib/axes/_axes.html#Axes.violinplot
https://github.com/statsmodels/statsmodels/blob/master/statsmodels/graphics/boxplots.py

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import json
import numpy as np
import os
import math

from scipy.stats import gaussian_kde

from .core import (
    CORPUS_NAMES,
    ORDERED_DETECTORS,
    check_detectors,
    clean_detector_name,
)
from .latex import build_latex_doc

# Color
# COLOR_LEFT = "B40204"
# COLOR_RIGHT = "00AABA"
# COLOR_MINMAX = "FF0000"

# Grayscale
COLOR_LEFT = "101010"
COLOR_RIGHT = "878787"
COLOR_MINMAX = "000000"

USE_LOG = True


def transform(x):
    if USE_LOG:
        return math.log(x, 10)
    return x


def untransform(x):
    if USE_LOG:
        return pow(10, x)
    return x


def _interpolate(coords, values, x):
    """ Return the estimated value of x by interpolating the nearest neighbors 
    in coords. It is assumed coords is sorted and is of the same length as 
    values.
    """
    if x in coords:
        return values[coords == x]
    below_idx, above_idx = None, None
    for idx, c in enumerate(coords):
        if c < x:
            below_idx = idx
        if c > x:
            above_idx = idx
            break
    avg_val = (values[below_idx] + values[above_idx]) / 2
    return avg_val


def _single_violin_data(pos, pos_data, width, side, plot_opts):
    # Based almost entirely on_single_violin from statsmodels
    bw_factor = plot_opts.get("bw_factor", None)

    def _violin_range(pos_data, plot_opts):
        """Return array with correct range, with which violins can be plotted."""
        cutoff = plot_opts.get("cutoff", False)
        cutoff_type = plot_opts.get("cutoff_type", "std")
        cutoff_val = plot_opts.get("cutoff_val", 1.5)

        s = 0.0
        if not cutoff:
            if cutoff_type == "std":
                s = cutoff_val * np.std(pos_data)
            else:
                s = cutoff_val

        x_lower = kde.dataset.min() - s
        x_upper = kde.dataset.max() + s
        return np.linspace(x_lower, x_upper, 501)

    pos_data = np.asarray(pos_data)
    kde = gaussian_kde(pos_data, bw_method=bw_factor)

    xvals = _violin_range(pos_data, plot_opts)
    violin = kde.evaluate(xvals)

    # NOTE: we removed normalization by violin.max()
    violin = width * violin

    if side == "both":
        envelope_l, envelope_r = (-violin + pos, violin + pos)
    elif side == "right":
        envelope_l, envelope_r = (np.zeros_like(violin) + pos, violin + pos)
    elif side == "left":
        envelope_l, envelope_r = (-violin + pos, np.zeros_like(violin) + pos)
    else:
        msg = "`side` parameter should be one of {'left', 'right', 'both'}."
        raise ValueError(msg)

    return xvals, envelope_l, envelope_r


def get_median_coords(coords, left, right, median):
    data = {}
    data["xleft"] = _interpolate(coords, left, median)
    data["xright"] = _interpolate(coords, right, median)
    data["yleft"] = median
    data["yright"] = median
    return data


def get_extrema_coords(pos, pos_data, width, side):
    # min
    xleft = pos
    xleft -= width if side in ["left", "both"] else 0
    xright = pos
    xright += width if side in ["right", "both"] else 0
    yleft = yright = np.min(pos_data)
    min_coords = {
        "xleft": xleft,
        "xright": xright,
        "yleft": yleft,
        "yright": yright,
    }
    # max
    yleft = yright = np.max(pos_data)
    max_coords = {
        "xleft": xleft,
        "xright": xright,
        "yleft": yleft,
        "yright": yright,
    }
    return min_coords, max_coords


def generate_violin_data(
    summary_data, side="both", showmedian=True, showextrema=True, plot_opts={}
):

    check_detectors(summary_data["runtimes"].keys())

    dataset = list(
        map(
            np.asarray,
            [
                list(map(transform, summary_data["runtimes"][key]))
                for key in ORDERED_DETECTORS
            ],
        )
    )

    positions = np.arange(len(dataset)) + 1
    pos_span = np.max(positions) - np.min(positions)
    width = np.min(
        [0.15 * np.max([pos_span, 1.]), plot_opts.get("violin_width", 0.8) / 2.]
    )

    violin_data = []
    for pos_data, pos, name in zip(dataset, positions, ORDERED_DETECTORS):
        xvals, envelope_l, envelope_r = _single_violin_data(
            pos, pos_data, width, side, plot_opts
        )

        # return back to actual data
        xvals = np.array([untransform(x) for x in xvals])
        pos_data = np.array([untransform(x) for x in pos_data])

        data = {
            "name": name,
            "side": side,
            "xvals": xvals,
            "envelope_l": envelope_l,
            "envelope_r": envelope_r,
        }

        if showmedian:
            data["median"] = get_median_coords(
                xvals, envelope_l, envelope_r, np.median(pos_data)
            )
        if showextrema:
            data["min"], data["max"] = get_extrema_coords(
                pos, pos_data, width / 3, side
            )

        violin_data.append(data)

    return violin_data


def generate_tex_for_line(xleft=0, yleft=0, xright=0, yright=0, linestyle=""):
    tex = ""
    tex += "\\addplot[%s] coordinates {%%\n" % linestyle
    tex += "(%.16f, %.16f)\n" % (xleft, yleft)
    tex += "(%.16f, %.16f)\n" % (xright, yright)
    tex += "};\n"
    return tex


def generate_tex_for_violin(
    violin, edgecolor=None, edgethick=None, fillcolor=None, alpha=0.5
):
    name = violin["name"] + violin["side"]

    edgecolor = "none" if edgecolor is None else edgecolor
    edgethick = "" if edgethick is None else ", " + edgethick
    fillcolor = "fill=none" if fillcolor is None else fillcolor
    left_name, right_name = name + "Left", name + "Right"

    tex = "\\addplot [draw=%s %s, name path=%s] coordinates {%%\n" % (
        edgecolor,
        edgethick,
        left_name,
    )
    for xx, yy in zip(violin["envelope_l"], violin["xvals"]):
        tex += "(%.16f, %.16f)\n" % (xx, yy)
    tex += "};\n"
    tex += "\\addplot [draw=%s %s, name path=%s] coordinates {%%\n" % (
        edgecolor,
        edgethick,
        right_name,
    )
    for xx, yy in zip(violin["envelope_r"], violin["xvals"]):
        tex += "(%.16f, %.16f)\n" % (xx, yy)
    tex += "};\n"
    tex += "\\addplot [%s, opacity=%f] fill between [of=%s and %s];\n" % (
        fillcolor,
        alpha,
        left_name,
        right_name,
    )

    if "median" in violin:
        # linestyle = "dashed, dash pattern=on 2pt off 2pt"
        violin["median"]["linestyle"] = "densely dotted, thick, black"

        tex += generate_tex_for_line(**violin["median"])
    if "min" in violin:
        violin["min"]["linestyle"] = "solid, ColorMinMax"
        tex += generate_tex_for_line(**violin["min"])
    if "max" in violin:
        violin["max"]["linestyle"] = "solid, ColorMinMax"
        tex += generate_tex_for_line(**violin["max"])

    return tex


def generate_latex(violindata, legend_data, opacity=0.5):
    abbrev = [clean_detector_name(d) for d in ORDERED_DETECTORS]
    xtick = ",".join([str(i + 1) for i in range(len(abbrev))])
    xticklabels = ",".join(abbrev)

    yrange = [pow(10, x) for x in [-6, -4, -2, 0, 2, 4]]
    ytick = ",".join([str(i) for i in yrange])

    legend_entries = ", ".join(
        [CORPUS_NAMES.get(c) for c in legend_data["corpora"]]
    )

    tex = (
        "\\documentclass[preview=true]{standalone}\n"
        "\\usepackage{tikz}\n"
        "\\usepackage{pgfplots}\n"
        "\\pgfplotsset{compat=1.16}\n"
        "\\usepgfplotslibrary{fillbetween}\n"
        "\\definecolor{ColorLeft}{HTML}{%s}\n"
        "\\definecolor{ColorRight}{HTML}{%s}\n"
        "\\definecolor{ColorMinMax}{HTML}{%s}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\n"
        "\\begin{semilogyaxis}[\n"
        "xtick={%s},\n"
        "xticklabels={%s},\n"
        "ytick={%s},\n"
        "ylabel={Runtime (s)},\n"
        "width=600pt,\n"
        "height=200pt,\n"
        "ymajorgrids,\n"
        "grid style={opacity=0.1},\n"
        "legend entries={%s},\n"
        "legend pos={south west},\n"
        "]\n"
        % (
            COLOR_LEFT,
            COLOR_RIGHT,
            COLOR_MINMAX,
            xtick,
            xticklabels,
            ytick,
            legend_entries,
        )
    )

    tex += (
        "\\addlegendimage{only marks, mark=square*, ColorLeft, opacity=%g}\n"
        % (opacity)
    )
    tex += (
        "\\addlegendimage{only marks, mark=square*, ColorRight, opacity=%g}\n"
        % (opacity)
    )

    for corpus in violindata:
        for violin in violindata[corpus]:
            fillcolor = (
                "ColorLeft" if violin["side"] == "left" else "ColorRight"
            )
            tex += generate_tex_for_violin(
                violin, edgecolor="black", fillcolor=fillcolor, alpha=opacity
            )

    tex += "\\end{semilogyaxis}\n" "\\end{tikzpicture}\n" "\\end{document}"
    return tex


def create_twosided_violin(corpus_data, output_file):
    corpora = sorted(corpus_data.keys())
    sides = ["left", "right"]
    assert len(corpora) == 2
    legend_data = {"corpora": corpora, "colors": [COLOR_LEFT, COLOR_RIGHT]}

    violindata = {}
    for corpus, side in zip(corpora, sides):
        violindata[corpus] = generate_violin_data(
            corpus_data[corpus], side=side, showmedian=True
        )

    tex = generate_latex(violindata, legend_data)
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
        help="Summary file(s) with the results",
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

    create_twosided_violin(all_data, args.output)
