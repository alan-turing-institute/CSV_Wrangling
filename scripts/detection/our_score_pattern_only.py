#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Get the best parameter set by using only the pattern score of our data 
consistency measure.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
"""

from collections import Counter

from .core import run
from .our_score_base import determine_dqr, make_abstraction
from .our_score_full import EPS_PAT


DETECTOR = "our_score_pattern_only"


def get_scores(data, dialects, verbose=False):
    scores = {}
    for dialect in sorted(dialects):
        A = make_abstraction(data, dialect)
        row_patterns = Counter(A.split("R"))
        pattern_score = 0
        for pat_p, n_p in row_patterns.items():
            Lk = len(pat_p.split("D"))
            pattern_score += n_p * (max(EPS_PAT, Lk - 1) / Lk)
        pattern_score /= len(row_patterns)

        score = pattern_score
        scores[dialect] = score

        if verbose:
            print(
                "%15r:\tpattern = %.6f\tfinal = %s"
                % (
                    dialect,
                    pattern_score,
                    "0" if scores[dialect] == 0 else "%.6f" % scores[dialect],
                )
            )

    return scores


def wrap_determine_dqr(filename, verbose=False):
    return determine_dqr(filename, get_scores, verbose=verbose)


def main():
    run(determine_dqr=wrap_determine_dqr, detector=DETECTOR)
