#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper for normal form detection.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import sys

from preprocessing import filter_non_normal

if __name__ == '__main__':
    if not len(sys.argv) == 4:
        print("Usage: %s input_dir normal_file non_normal_file" % sys.argv[0])
        raise SystemExit
    filter_non_normal.main(sys.argv[1], sys.argv[2], sys.argv[3])
