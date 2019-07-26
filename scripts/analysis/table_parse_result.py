#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate a table with percentages along a "no result"/"incorrect 
result"/"correct result" split.

          | Sniff | Suit | Hypo | Our (full) |
----------------------------------------------
No Result |       |      |      |            |
Incorrect |       |      |      |            |
Correct   |       |      |      |            |


Author: Gertjan van den Burg
Date: 2019-04-02

"""

import argparse
import json

from .core import (
    ORDERED_DETECTORS,
    TABLE_SPEC,
    clean_detector_name,
    check_detectors,
)
from .latex import build_latex_table


def create_table(results, output_file):
    row_no_result = ["No Result"]
    row_incorrect = ["Incorrect"]
    row_correct = ["Correct"]

    check_detectors(results["no_result_all"].keys())
    check_detectors(results["incorrect_result_all"].keys())
    check_detectors(results["correct_result_all"].keys())

    for key in ORDERED_DETECTORS:
        row_no_result.append(results["no_result_all"][key] * 100.0)
        row_incorrect.append(results["incorrect_result_all"][key] * 100.0)
        row_correct.append(results["correct_result_all"][key] * 100.0)

        # check that the values add up to 100% (minus precision errors)
        diff = abs(
            sum((r[-1] for r in [row_no_result, row_incorrect, row_correct]))
            - 100.0
        )
        if not diff < 1e-13:
            raise AssertionError("Difference is larger than eps: %r" % diff)

    headers = [""] + list(map(clean_detector_name, ORDERED_DETECTORS))

    table = [row_no_result, row_incorrect, row_correct]
    with open(output_file, "w") as fid:
        fid.write(
            build_latex_table(
                table,
                headers,
                floatfmt=".2f",
                bests=[min, min, max],
                table_spec=TABLE_SPEC,
            )
        )


def parse_args():
    parser = argparse.ArgumentParser("Create parsing result table")
    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
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

    needed_keys = [
        "no_result_all",
        "incorrect_result_all",
        "correct_result_all",
    ]
    for key in needed_keys:
        if not key in data:
            raise ValueError(
                "Required key '%s' not present in summary file." % key
            )

    create_table(data, args.output)


if __name__ == "__main__":
    main()
