#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get the best dialect with our data consistency measure.

This is the base package that contains common functions.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
"""

import itertools
import re

from collections import Counter

from common.dialect import Dialect
from common.encoding import get_encoding
from common.escape import is_potential_escapechar
from common.load import load_file
from common.parser import parse_file
from common.detector_result import DetectorResult, Status, StatusMsg
from common.utils import pairwise

from .lib.types.rudi_types import eval_types

from .core import can_be_delim_unicode, get_potential_quotechars
from ._ties import break_ties

BLOCKED_DELIMS = [".", "/", '"', "'"]


def masked_by_quotechar(S, quotechar, escapechar, test_char):
    """Test if a character is always masked by quote characters

    >>> masked_by_quotechar('A"B&C"A', '"', '', '&')
    True
    >>> masked_by_quotechar('A"B&C"A&A', '"', '', '&')
    False
    >>> masked_by_quotechar('A|"B&C"A', '"', '|', '&')
    False
    >>> masked_by_quotechar('A"B"C', '"', '', '')
    False
    """
    if test_char == "":
        return False
    escape_next = False
    in_quotes = False
    i = 0
    while i < len(S):
        s = S[i]
        if s == quotechar:
            if escape_next:
                i += 1
                continue
            if not in_quotes:
                in_quotes = True
            else:
                if i + 1 < len(S) and S[i + 1] == quotechar:
                    i += 1
                else:
                    in_quotes = False
        elif s == test_char and not in_quotes:
            return False
        elif s == escapechar:
            escape_next = True
        i += 1
    return True


def get_potential_delimiters(data, encoding):
    delims = set()
    c = Counter(data)
    for delim, _ in c.most_common():
        if (
            can_be_delim_unicode(delim, encoding=encoding)
            and not delim in BLOCKED_DELIMS
        ):
            delims.add(delim)
    delims.add("")
    return delims


def get_cells(data, dialect):
    rows = parse_file(data, dialect=dialect)
    all_cells = []
    for row in rows:
        all_cells.extend(row)
    return all_cells


def make_base_abstraction(S, dialect):
    stack = ""
    escape_next = False
    for s in S:
        if s in ["\r", "\n"]:
            if not stack.endswith("R"):
                stack += "R"
        elif s == dialect.delimiter:
            if escape_next:
                stack += "C"
                escape_next = False
            else:
                stack += "D"
        elif s == dialect.quotechar:
            if escape_next:
                stack += "C"
                escape_next = False
            else:
                stack += "Q"
        elif s == dialect.escapechar:
            if escape_next:
                if not stack.endswith("C"):
                    stack += "C"
                escape_next = False
            else:
                escape_next = True
        else:
            if escape_next:
                escape_next = False
            if not stack.endswith("C"):
                stack += "C"

    return stack


def merge_with_quotechar(S, dialect):
    in_quotes = False
    i = 0
    quote_pairs = []
    while i < len(S):
        s = S[i]
        if not s == "Q":
            i += 1
            continue

        if not in_quotes:
            in_quotes = True
            begin_quotes = i
        else:
            if i + 1 < len(S) and S[i + 1] == "Q":
                i += 1
            else:
                end_quotes = i
                quote_pairs.append((begin_quotes, end_quotes))
                in_quotes = False
        i += 1

    # replace quoted blocks by C
    Sl = list(S)
    for begin, end in quote_pairs:
        for i in range(begin, end + 1):
            Sl[i] = "C"
    S = "".join(Sl)

    return S


def strip_trailing(abstract):
    while abstract.endswith("R"):
        abstract = abstract[:-1]
    return abstract


def fill_empties(abstract):
    while "DD" in abstract:
        abstract = abstract.replace("DD", "DCD")

    while "DR" in abstract:
        abstract = abstract.replace("DR", "DCR")

    while "RD" in abstract:
        abstract = abstract.replace("RD", "RCD")

    while "CC" in abstract:
        abstract = abstract.replace("CC", "C")

    if abstract.startswith("D"):
        abstract = "C" + abstract

    if abstract.endswith("D"):
        abstract += "C"

    return abstract


def filter_urls(data):
    pat = "(?:(?:[A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)(?:(?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?"
    url_idxs = []
    for match in re.finditer(pat, data):
        url_idxs.append(match.span())
    Sl = list(data)
    for begin, end in url_idxs:
        for i in range(begin, end):
            Sl[i] = "U"
    return "".join(Sl)


def make_abstraction(data, dialect):
    """
    Make the abstract representation of a CSV file.

    Tests
    -----

    >>> make_abstraction('A,B,C', Dialect(delimiter=',', quotechar='', escapechar=''))
    'CDCDC'
    >>> make_abstraction('A,\\rA,A,A\\r', Dialect(delimiter=',', quotechar='', escapechar=''))
    'CDCRCDCDC'
    >>> make_abstraction('a,a,\\n,a,a\\ra,a,a\\r\\n', Dialect(delimiter=',', quotechar='', escapechar=''))
    'CDCDCRCDCDCRCDCDC'
    >>> make_abstraction('a,"bc""d""e""f""a",\\r\\n', Dialect(delimiter=',', quotechar='"', escapechar=''))
    'CDCDC'
    >>> make_abstraction('a,"bc""d"",|"f|""', Dialect(delimiter=',', quotechar='"', escapechar='|'))
    'CDC'
    >>> make_abstraction(',,,', Dialect(delimiter=',', quotechar='', escapechar=''))
    'CDCDCDC'
    >>> make_abstraction(',"",,', Dialect(delimiter=',', quotechar='"', escapechar=''))
    'CDCDCDC'
    >>> make_abstraction(',"",,\\r\\n', Dialect(delimiter=',', quotechar='"', escapechar=''))
    'CDCDCDC'

    Escape char:

    >>> make_abstraction('A,B|,C', Dialect(delimiter=',', quotechar='', escapechar='|'))
    'CDC'
    >>> make_abstraction('A,"B,C|"D"', Dialect(delimiter=',', quotechar='"', escapechar='|'))
    'CDC'
    >>> make_abstraction('a,|b,c', Dialect(delimiter=',', quotechar='', escapechar='|'))
    'CDCDC'
    >>> make_abstraction('a,b|,c', Dialect(delimiter=',', quotechar='', escapechar='|'))
    'CDC'
    >>> make_abstraction('a,"b,c|""', Dialect(delimiter=',', quotechar='"', escapechar='|'))
    'CDC'
    >>> make_abstraction('a,b||c', Dialect(delimiter=',', quotechar='', escapechar='|'))
    'CDC'
    >>> make_abstraction('a,"b|"c||d|"e"', Dialect(delimiter=',', quotechar='"', escapechar='|'))
    'CDC'
    >>> make_abstraction('a,"b|"c||d","e"', Dialect(delimiter=',', quotechar='"', escapechar='|'))
    'CDCDC'

    """

    A = make_base_abstraction(data, dialect)
    A = merge_with_quotechar(A, dialect)
    A = fill_empties(A)
    A = strip_trailing(A)

    return A


def is_clean(cell):
    return not (eval_types(cell) is None)


def get_potential_dialects(data, encoding):
    """
    We consider as escape characters those characters for which 
    is_potential_escapechar() is True and that occur at least once before a 
    quote character or delimiter in the dialect.

    One may wonder if self-escaping is an issue here (i.e. "\\\\", two times 
    backslash). It is not. In a file where a single backslash is desired and 
    escaping with a backslash is used, then it only makes sense to do this in a 
    file where the backslash is already used as an escape character (in which 
    case we include it). If it is never used as escape for the delimiter or 
    quotechar, then it is not necessary to self-escape.
    """
    delims = get_potential_delimiters(data, encoding)
    quotechars = get_potential_quotechars(data)
    escapechars = {}

    for delim, quotechar in itertools.product(delims, quotechars):
        escapechars[(delim, quotechar)] = set([""])

    for u, v in pairwise(data):
        if not is_potential_escapechar(u, encoding):
            continue
        for delim, quotechar in itertools.product(delims, quotechars):
            if v == delim or v == quotechar:
                escapechars[(delim, quotechar)].add(u)

    dialects = []
    for delim in delims:
        for quotechar in quotechars:
            for escapechar in escapechars[(delim, quotechar)]:
                if masked_by_quotechar(data, quotechar, escapechar, delim):
                    continue
                d = Dialect(delim, quotechar, escapechar)
                dialects.append(d)
    return dialects


def determine_dqr(filename, score_func, verbose=False, do_break_ties=True):
    encoding = get_encoding(filename)
    data = load_file(filename, encoding=encoding)
    if data is None:
        return DetectorResult(
            status=Status.SKIP, status_msg=StatusMsg.UNREADABLE
        )

    # fix-up to replace urls by a character, this removes many potential
    # delimiters that only occur in urls and cause noise.
    dialects = get_potential_dialects(filter_urls(data), encoding)
    if not dialects:
        return DetectorResult(
            status=Status.FAIL, status_msg=StatusMsg.NO_DIALECTS
        )

    if verbose:
        print(
            "Length of data: %i\n"
            "Considering %i dialects\n" % (len(data), len(dialects))
        )

    scores = score_func(data, dialects, verbose=verbose)

    score_sort = sorted(
        [(scores[dialect], dialect) for dialect in scores],
        key=lambda x: x[0],
        reverse=True,
    )

    max_prob = score_sort[0][0]
    dialects_with_score = [x[1] for x in score_sort if x[0] == max_prob]

    if len(dialects_with_score) > 1:
        if do_break_ties:
            res = break_ties(data, dialects_with_score)
        else:
            res = None
    else:
        res = dialects_with_score[0]

    if res is None:
        if verbose:
            print("More than 1 parameter set!")
            for d in dialects_with_score:
                print(d)
        return DetectorResult(
            status=Status.FAIL, status_msg=StatusMsg.MULTIPLE_ANSWERS
        )

    res = DetectorResult(dialect=res, status=Status.OK)

    return res
