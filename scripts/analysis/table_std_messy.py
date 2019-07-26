#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate a table with accuracies showing standard/non-standard split.

        | Sniff | Suit | Hypo | Our (full) |
--------------------------------------------
Std (N) |       |      |      |            |
NStd (N)|       |      |      |            |
Totl (N)|       |      |      |            |


Author: Gertjan van den Burg
Date: 2018-11-18

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
    n_standard = results["n_files_standard"]
    n_messy = results["n_files_messy"]
    n_total = results["n_files_all"]
    assert n_total == n_standard + n_messy

    row_std = ["Standard (%i)" % n_standard]
    row_mes = ["Messy (%i)" % n_messy]
    row_tot = ["Total (%i)" % n_total]

    check_detectors(results["standard_accuracy_all"].keys())
    check_detectors(results["messy_accuracy_all"].keys())
    check_detectors(results["detection_accuracy_all"]["overall"].keys())

    for key in ORDERED_DETECTORS:
        row_std.append(results["standard_accuracy_all"][key] * 100.0)
        row_mes.append(results["messy_accuracy_all"][key] * 100.0)
        row_tot.append(
            results["detection_accuracy_all"]["overall"][key] * 100.0
        )

    headers = [""] + list(map(clean_detector_name, ORDERED_DETECTORS))

    table = [row_std, row_mes, row_tot]
    with open(output_file, "w") as fid:
        fid.write(
            build_latex_table(
                table, headers, floatfmt=".2f", table_spec=TABLE_SPEC
            )
        )


def parse_args():
    parser = argparse.ArgumentParser("Create standard/non-standard table")
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
        "n_files_standard",
        "n_files_messy",
        "standard_accuracy_all",
        "messy_accuracy_all",
    ]
    for key in needed_keys:
        if not key in data:
            raise ValueError(
                "Required key '%s' not present in summary file." % key
            )

    create_table(data, args.output)


if __name__ == "__main__":
    main()
