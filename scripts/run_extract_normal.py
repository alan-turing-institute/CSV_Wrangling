#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper for normal form extraction

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import sys

from preprocessing import extract_normals

if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: %s normals.json output_file" % sys.argv[0])
        raise SystemExit
    extract_normals.main(sys.argv[1], sys.argv[2])
