#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Percentage of failure cases that were because of no_results or timeout.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse

from common.detector_result import StatusMsg, Status

from .constant_accuracy_overall import load_and_merge


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        dest="detector",
        help="Detector result(s)",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "-r",
        dest="reason",
        help="Reason for failure",
        choices=["no_results", "timeout"],
        required=True,
    )
    parser.add_argument(
        "-o", dest="output", help="Output tex file to write to", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()
    detector_results = load_and_merge(args.detector)
    n_failure = sum(
        (1 for x in detector_results.values() if x.status == Status.FAIL)
    )
    if args.reason == "no_results":
        n_with_reason = sum(
            (
                1
                for x in detector_results.values()
                if x.status == Status.FAIL
                and x.status_msg == StatusMsg.NO_RESULTS
            )
        )
    elif args.reason == "timeout":
        n_with_reason = sum(
            (
                1
                for x in detector_results.values()
                if x.status == Status.FAIL and x.status_msg == StatusMsg.TIMEOUT
            )
        )
    else:
        raise ValueError

    prop = n_with_reason / n_failure * 100
    with open(args.output, "w") as fid:
        fid.write("%.1f\\%%%%" % prop)


if __name__ == "__main__":
    main()
