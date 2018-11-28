#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Overall failure rate of a method for a single corpus.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

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

    fails = data["failures"]
    if not args.detector in fails:
        raise KeyError(
            "Detector name %s doesn't exist in failure dict" % args.detector
        )
    perc = fails[args.detector] * 100.0

    with open(args.output, "w") as fid:
        fid.write("%.2f\\%%%%" % perc)


if __name__ == "__main__":
    main()
