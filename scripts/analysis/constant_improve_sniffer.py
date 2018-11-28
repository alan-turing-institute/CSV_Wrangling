#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Accuracy improvement of a method over sniffer.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse

from .constant_accuracy_overall import load_and_merge, compute_accuracy_overall


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        dest="reference",
        help="Reference file(s) with ground truth",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "-d",
        dest="detector",
        help="Detector result(s)",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "-s", dest="sniffer", help="Sniffer result(s)", required=True, nargs="+"
    )
    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()
    reference_results = load_and_merge(args.reference)
    detector_results = load_and_merge(args.detector)
    sniffer_results = load_and_merge(args.sniffer)
    acc_det = compute_accuracy_overall(reference_results, detector_results)
    acc_snf = compute_accuracy_overall(reference_results, sniffer_results)
    diff = acc_det - acc_snf
    with open(args.output, "w") as fid:
        fid.write("%.1f\\%%%%" % diff)


if __name__ == "__main__":
    main()
