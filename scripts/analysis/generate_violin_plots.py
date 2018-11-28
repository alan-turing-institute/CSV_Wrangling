#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creating violin plots in PGFplots

Based on:
https://matplotlib.org/_modules/matplotlib/axes/_axes.html#Axes.violinplot

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import json
import math
import numpy as np
import os
import pandas as pd

import matplotlib.cbook as cbook
import matplotlib.mlab as mlab

from .core import ORDERED_DETECTORS, check_detectors, clean_detector_name
from .latex import build_latex_doc


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


def get_vpstats(dataset, points=500, bw_method=None):
    def _kde_method(X, coords):
        if np.all(X[0] == X):
            return (X[0] == coords).astype(float)
        kde = mlab.GaussianKDE(X, bw_method)
        return kde.evaluate(coords)

    vpstats = cbook.violin_stats(dataset, _kde_method, points=points)
    return vpstats


def fill_betweenx(
    y,
    x1,
    x2,
    name=None,
    edgecolor=None,
    edgethick=None,
    facecolor=None,
    alpha=0.2,
):
    edgecolor = "none" if edgecolor is None else edgecolor
    edgethick = "" if edgethick is None else ", " + edgethick
    left_name, right_name = name + "Left", name + "Right"
    tex = "\\addplot [draw=%s %s, name path=%s] coordinates {%%\n" % (
        edgecolor,
        edgethick,
        left_name,
    )
    for xx, yy in zip(x1, y):
        tex += "(%.16f, %.16f)\n" % (xx, yy)
    tex += "};\n"
    tex += "\\addplot [draw=%s %s, name path=%s] coordinates {%%\n" % (
        edgecolor,
        edgethick,
        right_name,
    )
    for xx, yy in zip(x2, y):
        tex += "(%.16f, %.16f)\n" % (xx, yy)
    tex += "};\n"
    tex += "\\addplot [%s, opacity=%f] fill between [of=%s and %s];\n" % (
        facecolor,
        alpha,
        left_name,
        right_name,
    )
    return tex


def fill_between():
    raise NotImplementedError


def hlines():
    raise NotImplementedError


def vlines():
    raise NotImplementedError


def temp_dump(dataset):
    maxlen = max((len(x) for x in dataset))
    newdata = []
    for x in dataset:
        if len(x) == maxlen:
            newdata.append(x)
        else:
            y = x + [float("nan")] * (maxlen - len(x))
            newdata.append(y)

    as_dict = {}
    for name, x in zip(ORDERED_DETECTORS, newdata):
        as_dict[name] = x
    df = pd.DataFrame(as_dict)
    df.to_csv("/tmp/beandata_ukdata.csv")


def prepare_violin_plot(
    runtimes,
    positions=None,
    widths=0.5,
    vert=True,
    showmeans=False,
    showmedians=True,
    showextrema=True,
):
    check_detectors(runtimes.keys())

    # We make the violin plot of the log data
    mylog = lambda x: math.log(x) / math.log(10)
    dataset = [list(map(mylog, runtimes[k])) for k in ORDERED_DETECTORS]

    vpstats = get_vpstats(dataset)

    means = []
    mins = []
    maxes = []
    medians = []

    artists = {}

    N = len(vpstats)
    datashape_message = (
        "List of violinplot statistics and `{0}` "
        "values must have the same length"
    )

    if positions is None:
        positions = range(1, N + 1)
    elif len(positions) != N:
        raise ValueError(datashape_message.format("positions"))

    if np.isscalar(widths):
        widths = [widths] * N
    elif len(widths) != N:
        raise ValueError(datashape_message.format("widths"))

    # Calculate ranges for statistics lines
    pmins = -0.25 * np.array(widths) + positions
    pmaxes = 0.25 * np.array(widths) + positions

    if vert:
        fill = fill_betweenx
        perp_lines = hlines
        par_lines = vlines
    else:
        fill = fill_between
        perp_lines = vlines
        par_lines = hlines

    fillcolor = "gray"
    edgecolor = "black"
    edgethick = "thick"

    medians_xleft = []
    medians_xright = []
    means_xleft = []
    means_xright = []

    bodies = []
    for values, stats, pos, width, name in zip(
        dataset, vpstats, positions, widths, ORDERED_DETECTORS
    ):

        min_value = min(values)
        max_value = max(values)

        coords = stats["coords"]
        coords = np.insert(coords, 0, min_value)
        coords = np.append(coords, max_value)

        vals = np.array(stats["vals"])
        vals = 0.5 * width * vals

        # The implementation in Matplotlib uses the expression:
        #
        #     vals = 0.5 * width * vals / vals.max()
        #
        # This divides by the maximum value in vals to stretch the figure out
        # to completely cover the width. However, I think this is misleading
        # because when you plot multiple violins side by side, it appears that
        # one is fatter than the other, whereas they should have the exact same
        # area in theory. Moreover, the KDE already does normalization (see:
        # https://github.com/matplotlib/matplotlib/blob/0688e127e7fc8f64ef4d4c8f6befa32e17d09455/lib/matplotlib/mlab.py#L3639)
        # We therefore removed the division by vals.max().

        x_left = -vals + pos
        x_left = np.insert(x_left, 0, pos)
        x_left = np.append(x_left, pos)

        x_right = vals + pos
        x_right = np.insert(x_right, 0, pos)
        x_right = np.append(x_right, pos)

        bodies += [
            fill(
                coords,
                x_left,
                x_right,
                name=name,
                facecolor=fillcolor,
                edgecolor=edgecolor,
                edgethick=edgethick,
                alpha=0.3,
            )
        ]

        mins.append(stats["min"])
        maxes.append(stats["max"])

        # We need to do some interpolation to get the right line for the width
        # of the lines.
        avg_val = _interpolate(stats["coords"], vals, stats["median"])
        medians_xleft.append(-avg_val + pos)
        medians_xright.append(avg_val + pos)
        medians.append(stats["median"])

        avg_val = _interpolate(stats["coords"], vals, stats["mean"])
        means_xleft.append(-avg_val + pos)
        means_xright.append(avg_val + pos)
        means.append(stats["mean"])

    artists["bodies"] = bodies

    if showmeans:
        artists["cmeans"] = [
            {
                "xleft": means_xleft[k],
                "xright": means_xright[k],
                "yleft": means[k],
                "yright": means[k],
            }
            for k in range(len(widths))
        ]
    if showmedians:
        artists["cmedians"] = [
            {
                "xleft": medians_xleft[k],
                "xright": medians_xright[k],
                "yleft": medians[k],
                "yright": medians[k],
            }
            for k in range(len(widths))
        ]
    if showextrema:
        artists["cmaxes"] = [
            {
                "xleft": pmins[k],
                "xright": pmaxes[k],
                "yleft": maxes[k],
                "yright": maxes[k],
            }
            for k in range(len(widths))
        ]
        artists["cmins"] = [
            {
                "xleft": pmins[k],
                "xright": pmaxes[k],
                "yleft": mins[k],
                "yright": mins[k],
            }
            for k in range(len(widths))
        ]

    return artists


def create_violin_plot(violin_plot, output_file):

    abbrev = [clean_detector_name(d) for d in ORDERED_DETECTORS]
    xtick = ",".join([str(i + 1) for i in range(len(abbrev))])
    xticklabels = ",".join(abbrev)

    ytick = ",".join([str(i) for i in range(-4, 4)])
    yticklabels = ",".join(["{$10^{" + str(i) + "}$}" for i in range(-4, 4)])

    tex = (
        "\\documentclass[preview=true]{standalone}\n"
        "\\usepackage{tikz}\n"
        "\\usepackage{pgfplots}\n"
        "\\pgfplotsset{compat=1.16}\n"
        "\\usepgfplotslibrary{fillbetween}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\n"
        "\\begin{axis}[\n"
        "xtick={%s},\n"
        "xticklabels={%s},\n"
        "ytick={%s},\n"
        "yticklabels={%s},\n"
        "ylabel={Runtime (s)},\n"
        "width=500pt,\n"
        "height=200pt,\n"
        "ymajorgrids,\n"
        "grid style={opacity=0.1},\n"
        "]\n" % (xtick, xticklabels, ytick, yticklabels)
    )
    for body in violin_plot["bodies"]:
        tex += body

    for key in [k for k in violin_plot if k.startswith("c")]:
        for cmean in violin_plot[key]:
            style = (
                "dashed, dash pattern=on 2pt off 2pt"
                if key == "cmedians"
                else "solid"
            )
            tex += "\\addplot [%s, thick, black] coordinates {%%\n" % style
            tex += "(%.16f, %.16f)\n" % (cmean["xleft"], cmean["yleft"])
            tex += "(%.16f, %.16f)\n" % (cmean["xright"], cmean["yright"])
            tex += "};\n"

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
        dest="summary",
        help="Summary file with the input data",
        required=True,
    )
    return parser.parse_args()


def main(summary_file, output_file):
    with open(summary_file, "r") as fid:
        summary = json.load(fid)

    violin_data = prepare_violin_plot(
        summary["runtimes"], showmedians=True, showmeans=False, showextrema=True
    )
    create_violin_plot(violin_data, output_file)


if __name__ == "__main__":
    args = parse_args()
    main(args.summary, args.output)
