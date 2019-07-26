#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert summary data to a latex table

Author: Gertjan van den Burg

"""

import json
import argparse

from .core import (
    ORDERED_DETECTORS,
    TABLE_SPEC,
    clean_detector_name,
    check_detectors,
)
from .latex import build_latex_table


def create_table(results, output_file):
    table = []
    for prop in results:
        row = [prop.capitalize()]
        check_detectors(results[prop].keys())
        for key in ORDERED_DETECTORS:
            row.append(results[prop][key] * 100.0)
        table.append(row)

    headers = ["Property"] + list(map(clean_detector_name, ORDERED_DETECTORS))

    with open(output_file, "w") as fid:
        fid.write(
            build_latex_table(
                table, headers, floatfmt=".2f", table_spec=TABLE_SPEC
            )
        )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "type",
        choices=["all", "human", "normal"],
        help="Subset of data to generate plot for",
        default="all",
    )
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

    key = "detection_accuracy_" + args.type
    if not key in data:
        raise ValueError("Can't find key %s in file %s" % (key, args.summary))

    create_table(data[key], args.output)
