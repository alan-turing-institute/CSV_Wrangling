
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compute the factor that relates the size of the alphabet to the size of the set 
of potential dialects.

To be exact, we want F in the equation: |Dialects| = F * |UniqueChars|

This is averaged over both datasets in the test set.

Author: Gertjan van den Burg
Date: 2019-04-10

"""

import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        dest="input",
        help="Overview files with the results from the ``potential_dialects.py`` script.",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()
    fracs = []
    for filename in args.input:
        with open(filename, "r") as fid:
            for line in fid:
                data = json.loads(line.strip())
                fracs.append(data["n_dialect"] / data["n_alpha"])

    result = sum(fracs) / len(fracs)
    with open(args.output, "w") as fid:
        fid.write("%.1f%%" % result)


if __name__ == "__main__":
    main()
