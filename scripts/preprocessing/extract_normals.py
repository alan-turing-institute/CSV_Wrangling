#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script extracts the detected normal forms into an output file that can be 
used for the comparison.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import json

from tqdm import tqdm

from common.dialect import Dialect
from common.detector_result import DetectorResult, Status, StatusMsg


def load_normals(filename):
    data = []
    with open(filename, "r") as fid:
        for line in fid:
            data.append(json.loads(line.strip()))
    return data


def main(normal_file, output_file):
    normals = load_normals(normal_file)

    results = {}
    for entry in tqdm(normals):
        filename = entry["filename"]
        form_id = entry["form_id"]
        params = entry["params"]

        if form_id == "FAIL":
            # unreadable file
            dr = DetectorResult(
                detector="normal",
                filename=filename,
                status=Status.FAIL,
                status_msg=StatusMsg.UNREADABLE,
            )
        else:
            dialect = Dialect(
                delimiter=params["delim"],
                quotechar=params["quotechar"],
                escapechar=params["escapechar"],
            )

            dr = DetectorResult(
                detector="normal",
                dialect=dialect,
                filename=filename,
                status=Status.OK,
            )

        if filename in results:
            raise KeyError("Filename %s already exists, duplicate!" % filename)

        results[filename] = dr

    with open(output_file, "w") as fid:
        for filename in sorted(results.keys()):
            fid.write(results[filename].to_json() + "\n")

    print("All done.")
