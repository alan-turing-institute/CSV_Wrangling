#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Common functions for the Python code of the experiment.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
"""

import os
import json
import time
import argparse
import codecs
import unicodedata

from tqdm import tqdm

from common.detector_result import DetectorResult, Status, StatusMsg


def can_be_delim_unicode(char, encoding=None):
    as_unicode = codecs.decode(bytes(char, encoding), encoding=encoding)
    ctr = unicodedata.category(as_unicode)
    if ctr in ["Lu", "Ll", "Lt", "Lm", "Lo"]:
        return False
    elif ctr in ["Nd", "Nl", "No"]:  # number
        return False
    elif ctr in ["Po", "Pd", "Pc"]:  # punctuation
        return True
    elif ctr in ["Ps", "Pe"]:  # open and close brackets (maybe include?)
        return False
    elif ctr == "Zs":  # space
        return True
    elif ctr == "Sm":  # math symbols
        return True
    elif ctr == "Cc":  # other control (i.e. tab etc.)
        if as_unicode == "\t":
            return True
        return False
    elif ctr == "Co":  # private use (maybe used for NA?)
        # NOTE: This is tricky, we may slow our algorithm down a lot by
        # including all these code points as potential delimiters, but we
        # may also find the delimiter here.
        # Let's see if we _ever_ find a file that uses a private use
        # codepoint as a delimiter.
        return False
    return True



def get_potential_quotechars(data):
    quotechars = set([""])
    if "'" in data:
        quotechars.add("'")
    if '"' in data:
        quotechars.add('"')
    if "~" in data:
        quotechars.add("~")
    return quotechars


def dump_result(output_file, res):
    with open(output_file, "a") as fid:
        fid.write(res.to_json() + "\n")


def load_previous(output_file):
    previous = set()
    if not os.path.exists(output_file):
        return previous
    with open(output_file, "r") as fid:
        for line in fid.readlines():
            record = json.loads(line.strip())
            previous.add(record["filename"])
    return previous


def main(
    path_file,
    output_file,
    determine_dqr=None,
    detector=None,
    verbose=False,
    progress=False,
):
    with open(path_file, "r") as fid:
        files = [l.strip() for l in fid.readlines()]
    files.sort()

    previous = load_previous(output_file)

    for filename in tqdm(files, disable=not progress, desc=detector):
        if filename in previous:
            continue

        if not os.path.exists(filename):
            res = DetectorResult(
                detector=detector,
                dialect=None,
                filename=filename,
                runtime=None,
                status=Status.FAIL,
                status_msg=StatusMsg.NON_EXISTENT,
            )
            dump_result(output_file, res)
            continue

        if not progress:
            print("[%s] Analyzing file: %s" % (detector, filename))

        start_time = time.time()
        try:
            res = determine_dqr(filename, verbose=verbose)
        except KeyboardInterrupt:
            raise
        except:
            print("Uncaught exception occured parsing file: %s" % filename)
            raise

        res.runtime = time.time() - start_time
        res.filename = filename
        res.detector = detector
        dump_result(output_file, res)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
    parser.add_argument(
        "-p", "--progress", dest="progress", action="store_true"
    )
    parser.add_argument(
        "input_file",
        help="Input file can be a file of paths to CSV file, or the path of a single CSV file. If the former, output_file must be set",
    )
    parser.add_argument(
        "output_file",
        help="Output file (JSON) to write the results to",
        default=None,
        nargs="?",
    )
    return parser.parse_args()


def run(determine_dqr, detector):
    args = parse_args()
    if args.output_file is None:
        print(determine_dqr(args.input_file, verbose=args.verbose))
    else:
        main(
            args.input_file,
            args.output_file,
            determine_dqr=determine_dqr,
            detector=detector,
            verbose=args.verbose,
            progress=args.progress,
        )
