#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Get the best parameter set by using our data consistency measure.

This variation does not break ties.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
"""

from collections import Counter

from .core import run
from .our_score_base import (
    count_cd_in_pat,
    determine_dqr,
    get_cells,
    is_clean,
    make_abstraction,
)


DETECTOR = "our_score_full_no_tie"

# The value of EPS_PAT is tricky, because if we choose it too high it may give
# too many false single-column files. This value seems to work quite well.
EPS_PAT = 1e-3
EPS_TYP = 1e-10


def get_scores(data, dialects, verbose=False):
    scores = {}
    max_score = -float("inf")
    for dialect in sorted(dialects):
        A = make_abstraction(data, dialect)
        row_patterns = Counter(A.split("R"))
        pattern_score = 0
        for pat_p, n_p in row_patterns.items():
            n_cd = count_cd_in_pat(pat_p)
            Lk = n_cd + 1
            pattern_score += n_p * (max(EPS_PAT, Lk - 1) / Lk)
        pattern_score /= len(row_patterns)

        if pattern_score == 0:
            # if pattern score is zero, the outcome will be zero, so we
            # don't have to check types.
            type_score = float("nan")
            score = 0
        elif pattern_score < max_score:
            # since the type score is in [0, 1], if the pattern score
            # is smaller than the current best score, it can't possibly
            # be improved by types, so we don't have to bother.
            type_score = float("nan")
            score = 0
        else:
            cells = get_cells(data, dialect)
            n_clean = sum((is_clean(cell) for cell in cells))
            n_cells = len(cells)

            if n_cells == 0:
                type_score = EPS_TYP
            else:
                type_score = max(EPS_TYP, n_clean / n_cells)
            score = type_score * pattern_score

        scores[dialect] = score
        max_score = max(max_score, score)

        if verbose:
            print(
                "%15r:\ttype = %.6f\tpattern = %.6f\tfinal = %s"
                % (
                    dialect,
                    type_score,
                    pattern_score,
                    "0" if scores[dialect] == 0 else "%.6f" % scores[dialect],
                )
            )

    return scores


def wrap_determine_dqr(filename, verbose=False):
    return determine_dqr(
        filename, get_scores, verbose=verbose, do_break_ties=False
    )


def main():
    run(determine_dqr=wrap_determine_dqr, detector=DETECTOR)
