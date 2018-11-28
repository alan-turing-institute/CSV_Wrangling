#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get the best parameter set by using only the type score of our data consistency 
measure.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
"""

from .core import run
from .our_score_base import determine_dqr, get_cells, is_clean
from .our_score_full import EPS_TYP


DETECTOR = "our_score_type_only"


def get_scores(data, dialects, verbose=False):
    scores = {}
    for dialect in sorted(dialects):
        cells = get_cells(data, dialect)
        n_clean = sum((is_clean(cell) for cell in cells))
        n_cells = len(cells)

        if n_cells == 0:
            type_score = EPS_TYP
        else:
            type_score = max(EPS_TYP, n_clean / n_cells)
        score = type_score

        scores[dialect] = score

        if verbose:
            print(
                "%15r:\ttype = %.6f\tfinal = %s"
                % (
                    dialect,
                    type_score,
                    "0" if scores[dialect] == 0 else "%.6f" % scores[dialect],
                )
            )

    return scores


def wrap_determine_dqr(filename, verbose=False):
    return determine_dqr(filename, get_scores, verbose=verbose)


def main():
    run(determine_dqr=wrap_determine_dqr, detector=DETECTOR)
