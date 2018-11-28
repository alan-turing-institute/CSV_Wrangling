#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This takes a series of detector output files and merges them into a single file 
with the detector name "reference".

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

from common.detector_result import DetectorResult


def main(output_file, input_files):
    combined = {}
    for filename in input_files:
        with open(filename, "r") as fid:
            for line in fid:
                dr = DetectorResult.from_json(line.strip())
                if dr.filename in combined:
                    if dr.dialect == combined[dr.filename].dialect:
                        # allow it if the dialect is the same
                        continue
                    else:
                        raise KeyError(
                            "Duplicate result for file: %s" % dr.filename
                        )
                combined[dr.filename] = dr

    with open(output_file, "w") as fid:
        for filename in sorted(combined.keys()):
            dr = combined[filename]
            dr.original_detector = dr.detector
            dr.detector = "reference"
            fid.write(dr.to_json() + "\n")
