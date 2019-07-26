#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Count the number of dialects

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse

from common.detector_result import Status

from .core import load_detector_results


def count_dialect(result_dicts):
    dialects = set()
    for reference in result_dicts:
        for fname in reference:
            res = reference[fname]
            if not res.status == Status.OK:
                continue
            dialects.add(res.dialect)
    return len(dialects)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    parser.add_argument(
        "-r",
        dest="reference",
        help="Reference file for a specific corpus",
        required=True,
        nargs="+",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    result_dicts = []
    for reference in args.reference:
        _, reference_results = load_detector_results(reference)
        result_dicts.append(reference_results)
    n_dialect = count_dialect(result_dicts)

    with open(args.output, "w") as fid:
        fid.write("%i%%" % n_dialect)


if __name__ == "__main__":
    main()
