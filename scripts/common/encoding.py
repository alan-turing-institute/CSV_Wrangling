# -*- coding: utf-8 -*-

"""
Common functions for encoding detection

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
Date: 2018-11-06
"""

import chardet

def get_encoding(filename):
    detector = chardet.UniversalDetector()
    final_chunk = False
    blk_size = 65536
    with open(filename, "rb") as fid:
        while (not final_chunk) and (not detector.done):
            chunk = fid.read(blk_size)
            if len(chunk) < blk_size:
                final_chunk = True
            detector.feed(chunk)
    detector.close()
    encoding = detector.result.get("encoding", None)
    return encoding
