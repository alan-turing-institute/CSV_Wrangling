#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get the number of files in a given summary file.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        dest="summary",
        help="Summary file with the results",
        required=True,
    )

    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.summary, "r") as fid:
        data = json.load(fid)

    n_files = data["n_files_all"]
    with open(args.output, "w") as fid:
        fid.write("%i%%" % n_files)


if __name__ == "__main__":
    main()
