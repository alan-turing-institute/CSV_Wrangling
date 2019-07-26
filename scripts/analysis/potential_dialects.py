#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quick script to check the distribution of the number of dialects that we 
consider.

Author: Gertjan van den Burg
Date: 2019-04-09

"""

import argparse
import json

from tqdm import tqdm

from common.encoding import get_encoding
from common.load import load_file
from detection.our_score_base import get_potential_dialects


def get_stats(filename):
    encoding = get_encoding(filename)
    data = load_file(filename, encoding=encoding)
    if data is None:
        return None
    n_alpha = len(set(data))
    n_dialect = len(get_potential_dialects(data, encoding))
    return dict(filename=filename, n_alpha=n_alpha, n_dialect=n_dialect)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="File with filenames to consider", required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file to write the numbers to",
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.output, "w") as oid:
        with open(args.input, "r") as fid:
            total = sum((1 for _ in fid))
            fid.seek(0)
            for line in tqdm(fid, total=total):
                filename = line.strip()
                s = get_stats(filename)
                if s is None:
                    continue
                line = json.dumps(s)
                oid.write(line + "\n")


if __name__ == "__main__":
    main()
