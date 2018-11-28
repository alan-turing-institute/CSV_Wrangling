# -*- coding: utf-8 -*-

"""
Common functions for loading files

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
Date: 2018-11-06
"""

from .encoding import get_encoding


def load_file(filename, encoding="unknown"):
    if encoding == "unknown":
        encoding = get_encoding(filename)
    with open(filename, "r", newline="", encoding=encoding) as fid:
        try:
            return fid.read()
        except UnicodeDecodeError:
            print(
                "UnicodeDecodeError occurred for file: %s. "
                "This means the encoding was determined incorrectly "
                "or the file is corrupt." % filename
            )
            return None
