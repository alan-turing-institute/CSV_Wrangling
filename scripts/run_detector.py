#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper for detector executables.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import sys

from detection import (
    our_score_full,
    our_score_full_no_tie,
    our_score_pattern_only,
    our_score_type_only,
    sniffer,
    suitability,
)


def main():
    detector = sys.argv.pop(1)
    if detector == "our_score_full":
        our_score_full.main()
    elif detector == "our_score_full_no_tie":
        our_score_full_no_tie.main()
    elif detector == "our_score_type_only":
        our_score_type_only.main()
    elif detector == "our_score_pattern_only":
        our_score_pattern_only.main()
    elif detector == "sniffer":
        sniffer.main()
    elif detector == "suitability":
        suitability.main()
    else:
        raise ValueError("Unknown detector: %s" % detector)


if __name__ == "__main__":
    main()
