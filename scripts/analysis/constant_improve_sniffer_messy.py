#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Accuracy improvement of a method over sniffer for messy files.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import json
import math


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--round-up", help="Whether or not to round up", action="store_true"
    )
    parser.add_argument(
        "-s", dest="summary", help="Summary file(s)", required=True, nargs="+"
    )
    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()

    n_messy_tot = 0
    n_messy_correct_ours = 0
    n_messy_correct_snif = 0

    for summary_file in args.summary:
        with open(summary_file, "r") as fid:
            data = json.load(fid)

        n_messy = data["n_files_messy"]
        acc_messy_ours = data["messy_accuracy_all"]["our_score_full"]
        acc_messy_snif = data["messy_accuracy_all"]["sniffer"]

        n_messy_tot += n_messy
        n_messy_correct_ours += acc_messy_ours * n_messy
        n_messy_correct_snif += acc_messy_snif * n_messy

    acc_ours = n_messy_correct_ours / n_messy_tot
    acc_snif = n_messy_correct_snif / n_messy_tot

    improv = (acc_ours - acc_snif) * 100

    with open(args.output, "w") as fid:
        if args.round_up:
            fid.write("%.0f\\%%%%" % math.ceil(improv))
        else:
            fid.write("%.1f\\%%%%" % improv)


if __name__ == "__main__":
    main()
