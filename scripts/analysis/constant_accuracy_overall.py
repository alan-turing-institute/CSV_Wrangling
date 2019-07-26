#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Overall accuracy of a method averaged over multiple corpora.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import sys

from common.detector_result import Status

from .core import load_detector_results

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
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def load_and_merge(filenames):
    results = {}
    for res_file in filenames:
        _, res = load_detector_results(res_file)
        for fname in res:
            if fname in results:
                print(
                    "Error: duplicate result for file %s" % fname,
                    file=sys.stderr,
                )
                raise SystemExit
            results[fname] = res[fname]
    return results


def compute_accuracy_overall(ref_results, det_results):
    total = 0
    correct = 0
    for fname in ref_results:
        ref = ref_results[fname]
        if not ref.status == Status.OK:
            continue
        total += 1
        det = det_results[fname]
        if not det.status == Status.OK:
            continue
        correct += ref.dialect == det.dialect
    return correct / total * 100


def main():
    args = parse_args()
    reference_results = load_and_merge(args.reference)
    detector_results = load_and_merge(args.detector)
    acc = compute_accuracy_overall(reference_results, detector_results)
    with open(args.output, "w") as fid:
        fid.write("%.0f\\%%%%" % acc)


if __name__ == "__main__":
    main()
