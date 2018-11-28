#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Uses the suitability metric from the Proactive Wrangler paper to decide on the 
dialect.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""


from common.dialect import Dialect
from common.encoding import get_encoding
from common.escape import is_potential_escapechar
from common.load import load_file
from common.parser import parse_file
from common.detector_result import DetectorResult, Status, StatusMsg
from common.utils import pairwise

from .core import run, get_potential_quotechars
from .lib.types.rudi_types import eval_types
from ._ties import break_ties

DETECTOR = "suitability"
WRANGLER_DELIMS = [",", ":", "|", "\t"]


def extract_cells(data, dialect):
    cells = []
    rows = parse_file(data, dialect)
    for row in rows:
        cells.extend(row)
    return cells


def get_columns(cells):
    cols = {}
    for row in cells:
        for i, c in enumerate(row):
            if not i in cols:
                cols[i] = []
            cols[i].append(c)
    return cols


def count_empties(cells, dialect):
    count = 0
    for row in cells:
        for cell in row:
            if cell == "":
                count += 1
            if not dialect.quotechar is None:
                if cell == (dialect.quotechar + dialect.quotechar):
                    count += 1
    return count


def count_delimiters(cells):
    """Count the cells that contain a delimiter

    It is not entirely trivial whether or not the "continue" statement should 
    be there, as we could also count each occurrence of a delimiter in a cell 
    separately. However, since the normalization in the second term of (1) in 
    Guo et al. (2011) is normalized by |R|*|C| it seems naturally to include 
    it.
    """
    count = 0
    for row in cells:
        for cell in row:
            for d in WRANGLER_DELIMS:
                if d in cell:
                    count += 1
                    continue  # see note
    return count


def column_homogeneity(column):
    """
    As the Proactive Wrangler (PW) paper doesn't give sufficient details on all 
    the types they implement, we use our own type inference engine (from 
    rudi_types) to guess the type. Note that "unicode_alphanum" is a generic 
    string type as is None. Empty cells are treated separately and are not 
    considered a type in the PW paper.

    """
    type_counts = {}
    for cell in column:
        detected_type = eval_types(cell)
        if detected_type is None:
            detected_type = "string"
        if detected_type == "unicode_alphanum":
            detected_type = "string"
        if detected_type == "empty":
            continue
        if not detected_type in type_counts:
            type_counts[detected_type] = 0
        type_counts[detected_type] += 1

    R = len(column)

    homogeneity = 0
    for t in type_counts:
        homogeneity += pow(type_counts[t] / R, 2.0)

    return homogeneity


def compute_suitability(data, dialect):
    cells = extract_cells(data, dialect)
    columns = get_columns(cells)

    R = len(cells)
    C = len(columns)

    E = count_empties(cells, dialect)
    D = count_delimiters(cells)

    homo = sum((column_homogeneity(columns[cidx]) for cidx in columns))
    if R * C == 0:
        suitability = 0
    else:
        suitability = (1 - homo / C) + (E + D) / (R * C)

    return suitability


def get_dialects(data, encoding):
    delims = WRANGLER_DELIMS
    quotechars = get_potential_quotechars(data)
    escapechars = {}

    for delim in delims:
        delim_escapes = set()
        for u, v in pairwise(data):
            if v == delim and is_potential_escapechar(u, encoding):
                delim_escapes.add(u)
        for quotechar in quotechars:
            escapes = set(delim_escapes)
            for u, v in pairwise(data):
                if v == quotechar and is_potential_escapechar(u, encoding):
                    escapes.add(u)
            escapes.add("")
            escapechars[(delim, quotechar)] = escapes

    dialects = []
    for delim in delims:
        for quotechar in quotechars:
            for escapechar in escapechars[(delim, quotechar)]:
                d = Dialect(delim, quotechar, escapechar)
                dialects.append(d)
    return dialects


def determine_dqr(filename, verbose=False):
    encoding = get_encoding(filename)
    data = load_file(filename, encoding=encoding)
    if data is None:
        return DetectorResult(
            status=Status.SKIP, status_msg=StatusMsg.UNREADABLE
        )

    dialects = get_dialects(data, encoding)
    scores = []

    for dialect in sorted(dialects):
        S = compute_suitability(data, dialect)
        if verbose:
            print("%15r\tsuitability = %.6f" % (dialect, S))
        scores.append((S, dialect))

    min_suit = min((x[0] for x in scores))
    min_dialects = [x[1] for x in scores if x[0] == min_suit]

    if len(min_dialects) > 1:
        res = break_ties(data, min_dialects)
    else:
        res = min_dialects[0]

    if res is None:
        return DetectorResult(
            status=Status.FAIL, status_msg=StatusMsg.MULTIPLE_ANSWERS
        )

    res = DetectorResult(dialect=res, status=Status.OK)

    return res


def main():
    run(determine_dqr=determine_dqr, detector=DETECTOR)
