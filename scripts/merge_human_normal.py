#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper around merge.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import sys

from preprocessing import merge

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: %s output_file input_file ..." % sys.argv[0])
        raise SystemExit
    merge.main(sys.argv[1], sys.argv[2:])
