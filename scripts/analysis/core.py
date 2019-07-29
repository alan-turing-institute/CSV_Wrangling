#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Common definitions for the analysis scripts

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import json
import os

from common.detector_result import DetectorResult

DETECTOR_NAMES = {
    "hypoparsr": "HypoParsr",
    "sniffer": "Sniffer",
    "suitability": "Suitability",
    "our_score_pattern_only": "Pattern",
    "our_score_type_only": "Type",
    "our_score_full_no_tie": "No Tie",
    "our_score_full": "Full",
}

ORDERED_DETECTORS = [
    "hypoparsr",
    "sniffer",
    "suitability",
    "our_score_pattern_only",
    "our_score_type_only",
    "our_score_full_no_tie",
    "our_score_full",
]
TABLE_SPEC = "lrrr|rrrr"

ORDERED_PROP = ["delimiter", "quotechar", "escapechar", "overall"]

CORPUS_NAMES = {"github": "GitHub", "ukdata": "UKdata"}


def check_detectors(names):
    if not set(ORDERED_DETECTORS) == set(names):
        print(
            "Detector set doesn't match!\nExpected: %r\nReceived: %r\n"
            % (sorted(set(ORDERED_DETECTORS)), sorted(set(names)))
        )
        raise SystemExit(1)


def clean_detector_name(detector):
    abbr = DETECTOR_NAMES.get(detector, detector)
    return abbr.replace("_", "\\_")


def load_detector_results(result_file):
    """
    Load the results from a given detector result file. Verify each record in 
    the process.
    """
    detector_names = set()
    results = {}
    with open(result_file, "r") as fid:
        for idx, line in enumerate(fid.readlines()):
            try:
                record = DetectorResult.from_json(line.strip())
            except json.JSONDecodeError:
                print(
                    "\nError parsing the following record in file (line %i): "
                    "%s\n---\n%s" % (idx + 1, result_file, line.strip())
                )
                raise SystemExit(1)

            detector_names.add(record.detector)

            fname = record.filename
            if not os.path.isabs(fname):
                fname = os.path.abspath(fname)
                record.filename = fname
            if fname in results:
                raise ValueError(
                    "Duplicate result for file %s in detector file %s"
                    % (record.filename, result_file)
                )

            record.validate()
            results[fname] = record

    if len(detector_names) > 1:
        raise ValueError(
            "More than one detector name in file: %s" % result_file
        )
    detector = detector_names.pop()
    return detector, results


def is_standard_dialect(dialect):
    if (
        dialect.delimiter == ","
        and dialect.quotechar in ["", '"']
        and dialect.escapechar == ""
    ):
        return True
    return False
