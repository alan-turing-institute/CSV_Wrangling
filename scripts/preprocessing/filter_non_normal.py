#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Split CSV files between those where ground truth can be determined 
automatically (normal forms) and those that need human annotation (non-normal).

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import os
import json

from tqdm import tqdm
from tabulate import tabulate

from .normal_forms import detect_form


def main(input_dir, normal_file, non_normal_file):
    files = [os.path.join(input_dir, x) for x in os.listdir(input_dir)]
    files.sort()

    normal_fid = open(normal_file, "w")
    nonnormal_fid = open(non_normal_file, "w")

    counts = {}

    for f in tqdm(files):
        form_id, params = detect_form(f, record_result=False, verbose=False)

        if not form_id in counts:
            counts[form_id] = 0
        counts[form_id] += 1

        if form_id is None:
            nonnormal_fid.write(f + "\n")
        else:
            data = {"filename": f, "form_id": form_id, "params": params}
            normal_fid.write(json.dumps(data) + "\n")

    normal_fid.close()
    nonnormal_fid.close()

    table = [
        {"form": "None" if k is None else k, "count": v}
        for k, v in counts.items()
    ]

    print(tabulate(table, headers="keys"))
