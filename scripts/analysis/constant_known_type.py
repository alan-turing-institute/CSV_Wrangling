#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compute the percentage of cells with a known type.

Author: Gertjan van den Burg
Copyright (c) 2019 - The Alan Turing Institute
License: See the LICENSE file.
Date: 2019-04-15

"""

import argparse
import multiprocessing

from tqdm import tqdm

from common.encoding import get_encoding
from common.load import load_file
from detection.our_score_base import is_clean, get_cells
from common.detector_result import Status

from .core import load_detector_results


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--n-jobs",
        help="Number of parallel jobs",
        default=6,
        dest="n_jobs",
    )
    parser.add_argument(
        "-r",
        "--reference",
        help="Reference file(s) with ground truth",
        nargs="+",
        required=True,
    )
    parser.add_argument("-o", "--output", help="Output file")
    return parser.parse_args()


def _worker(res_ref):
    filename = res_ref.filename
    encoding = get_encoding(filename)
    data = load_file(filename, encoding=encoding)
    if data is None:
        return None

    cells = get_cells(data, res_ref.dialect)
    n_clean = sum((is_clean(cell) for cell in cells))
    n_cells = len(cells)
    return (n_clean, n_cells)


def main():
    args = parse_args()

    reference_results = {}
    for reference in args.reference:
        _, ref_results = load_detector_results(reference)
        reference_results.update(ref_results)

    n_cells = 0
    n_clean = 0

    only_ok = {
        k: v for k, v in reference_results.items() if v.status == Status.OK
    }

    with multiprocessing.Pool(args.n_jobs) as pool:
        with tqdm(total=len(only_ok)) as pbar:
            for n_clean_x, n_cells_x in pool.imap_unordered(
                _worker, only_ok.values()
            ):
                n_clean += n_clean_x
                n_cells += n_cells_x
                pbar.update()

    perc = n_clean / n_cells * 100
    with open(args.output, "w") as fid:
        fid.write("%.1f\\%%%%" % perc)


if __name__ == "__main__":
    main()
