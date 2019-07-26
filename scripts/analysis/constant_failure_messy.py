#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Failure on messy files averaged over both corpora.

Author: Gertjan van den Burg
Copyright (c) 2019 - The Alan Turing Institute
License: See the LICENSE file.
Date: 2019-04-15

"""

import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", dest="detector", help="Detector name", required=True
    )
    parser.add_argument(
        "-s",
        dest="summary",
        help="Summary file(s) with the results",
        required=True,
        nargs="+",
    )

    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()

    n_messy_total = 0
    n_messy_correct_total = 0
    for summary_file in args.summary:
        with open(summary_file, "r") as fid:
            data = json.load(fid)
        if not args.detector in data["messy_accuracy_all"]:
            raise KeyError(
                "Detector name %s doesn't exist in messy_accuracy_all dict"
                % args.detector
            )

        n_messy = data["n_files_messy"]
        acc_messy = data["messy_accuracy_all"][args.detector]
        n_messy_correct = acc_messy * n_messy

        n_messy_total += n_messy
        n_messy_correct_total += n_messy_correct

    perc = (n_messy_total - n_messy_correct_total) / n_messy_total * 100.0

    with open(args.output, "w") as fid:
        fid.write("%.0f\\%%%%" % perc)


if __name__ == "__main__":
    main()
