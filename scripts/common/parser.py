#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Our CSV parser.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
Date: 2018-10-22

"""


def parse_file(
    S, dialect=None, delimiter=None, quotechar=None, escapechar=None
):
    """
    Parse a CSV file given as a string by ``S`` into a list of lists.

    This function automatically takes double quotes into account, uses 
    universal newlines, and can deal with quotes that start *inside* a cell.  
    Quotes are only stripped from cells if they occur at the start and the end 
    of the cell.

    Tests
    -----

    Testing splitting on delimiter with or without quotes

    >>> parse_file('A,B,C,D,E', delimiter=',', quotechar='"')
    [['A', 'B', 'C', 'D', 'E']]
    >>> parse_file('A,B,C,D,E', delimiter=',', quotechar='')
    [['A', 'B', 'C', 'D', 'E']]
    >>> parse_file('A,B,C,D,E')
    [['A,B,C,D,E']]
    >>> parse_file('A,"B",C,D,E', delimiter=',', quotechar='"')
    [['A', 'B', 'C', 'D', 'E']]
    >>> parse_file('A,"B,C",D,E', delimiter=',', quotechar='"')
    [['A', 'B,C', 'D', 'E']]
    >>> parse_file('A,"B,C",D,E', delimiter=',', quotechar='')
    [['A', '"B', 'C"', 'D', 'E']]
    >>> parse_file('"A","B","C",,,,', delimiter=',', quotechar='')
    [['"A"', '"B"', '"C"', '', '', '', '']]

    Testing splitting on rows only:

    >>> parse_file('A"B"C\\rA"B""C""D"', quotechar='')
    [['A"B"C'], ['A"B""C""D"']]
    >>> parse_file('A"B"C\\nA"B""C""D"', quotechar='')
    [['A"B"C'], ['A"B""C""D"']]
    >>> parse_file('A"B"C\\r\\nA"B""C""D"', quotechar='')
    [['A"B"C'], ['A"B""C""D"']]
    >>> parse_file('A"B\\r\\nB"C\\r\\nD"E"F\\r\\nG', quotechar='"')
    [['A"B\\r\\nB"C'], ['D"E"F'], ['G']]
    >>> parse_file('A"B\\nB"C\\nD"E"F\\nG', quotechar='"')
    [['A"B\\nB"C'], ['D"E"F'], ['G']]
    >>> parse_file('A"B\\nB\\rB"C\\nD"E"F\\nG', quotechar='"')
    [['A"B\\nB\\rB"C'], ['D"E"F'], ['G']]

    Tests from Python's builtin CSV module:

    >>> parse_file('')
    []
    >>> parse_file('a,b\\r', delimiter=',')
    [['a', 'b']]
    >>> parse_file('a,b\\n', delimiter=',')
    [['a', 'b']]
    >>> parse_file('a,b\\r\\n', delimiter=',')
    [['a', 'b']]
    >>> parse_file('a,"', delimiter=',', quotechar='"')
    [['a', '']]
    >>> parse_file('"a', delimiter=',', quotechar='"')
    [['a']]
    >>> parse_file('a,|b,c', delimiter=',', quotechar='"', escapechar='|') # differs from Python (1)
    [['a', '|b', 'c']]
    >>> parse_file('a,b|,c', delimiter=',', quotechar='"', escapechar='|')
    [['a', 'b,c']]
    >>> parse_file('a,"b,|c"', delimiter=',', quotechar='"', escapechar='|') # differs from Python (1)
    [['a', 'b,|c']]
    >>> parse_file('a,"b,c|""', delimiter=',', quotechar='"', escapechar='|')
    [['a', 'b,c"']]
    >>> parse_file('a,"b,c"|', delimiter=',', quotechar='"', escapechar='|') # differs from Python (2)
    [['a', 'b,c']]
    >>> parse_file('1,",3,",5', delimiter=',', quotechar='"')
    [['1', ',3,', '5']]
    >>> parse_file('1,",3,",5', delimiter=',', quotechar='')
    [['1', '"', '3', '"', '5']]
    >>> parse_file(',3,"5",7.3, 9', delimiter=',', quotechar='"')
    [['', '3', '5', '7.3', ' 9']]
    >>> parse_file('"a\\nb", 7', delimiter=',', quotechar='"')
    [['a\\nb', ' 7']]

    Double quotes:

    >>> parse_file('a,"a""b""c"', delimiter=',', quotechar='"')
    [['a', 'a"b"c']]

    Mix double and escapechar:

    >>> parse_file('a,"bc""d"",|"f|""', delimiter=',', quotechar='"', escapechar='|')
    [['a', 'bc"d","f"']]

    Other tests:

    >>> parse_file('a,b "c" d,e', delimiter=',', quotechar='')
    [['a', 'b "c" d', 'e']]
    >>> parse_file('a,b "c" d,e', delimiter=',', quotechar='"')
    [['a', 'b "c" d', 'e']]
    >>> parse_file('a,\\rb,c', delimiter=',')
    [['a', ''], ['b', 'c']]
    >>> parse_file('a,b\\r\\n\\r\\nc,d\\r\\n', delimiter=',')
    [['a', 'b'], ['c', 'd']]
    >>> parse_file('\\r\\na,b\\rc,d\\n\\re,f\\r\\n', delimiter=',')
    [['a', 'b'], ['c', 'd'], ['e', 'f']]

    Further escape char tests:

    >>> parse_file('a,b,c||d', delimiter=',', quotechar='', escapechar='|')
    [['a', 'b', 'c|d']]
    >>> parse_file('a,b,c||d,e|,d', delimiter=',', quotechar='', escapechar='|')
    [['a', 'b', 'c|d', 'e,d']]

    Quote mismatch until EOF:

    >>> parse_file('a,b,c"d,e\\n', delimiter=',', quotechar='"')
    [['a', 'b', 'c"d,e\\n']]
    >>> parse_file('a,b,c"d,e\\n', delimiter=',', quotechar='')
    [['a', 'b', 'c"d', 'e']]
    >>> parse_file('a,b,"c,d', delimiter=',', quotechar='"')
    [['a', 'b', 'c,d']]
    >>> parse_file('a,b,"c,d\\n', delimiter=',', quotechar='"')
    [['a', 'b', 'c,d\\n']]

    Single column:

    >>> parse_file('a\\rb\\rc\\n')
    [['a'], ['b'], ['c']]

    These tests illustrate a difference with the Python parser, which in this 
    case would return ``[['a', 'abc', 'd']]``.

    >>> parse_file('a,"ab"c,d', delimiter=',', quotechar='')
    [['a', '"ab"c', 'd']]
    >>> parse_file('a,"ab"c,d', delimiter=',', quotechar='"')
    [['a', '"ab"c', 'd']]


    Notes
    -----

    (1) We only interpret the escape character if it precedes the provided 
    delimiter, quotechar, or itself. Otherwise, the escape character does not 
    serve any purpose, and should not be dropped automatically.

    (2) For some reason the Python test suite places this escape character 
    *inside* the preceding quoted block. This seems counterintuitive and 
    incorrect and thus this behavior has not been duplicated.

    """
    if not dialect is None:
        delimiter = dialect.delimiter if delimiter is None else delimiter
        quotechar = dialect.quotechar if quotechar is None else quotechar
        escapechar = dialect.escapechar if escapechar is None else escapechar

    quote_cond = lambda c, q: q and c.startswith(q) and c.endswith(q)

    in_quotes = False
    in_escape = False
    rows = []
    i = 0
    row = []
    field = ""
    end_row = False
    end_field = False
    s = None
    while i < len(S):
        s = S[i]
        if s == quotechar:
            if in_escape:
                in_escape = False
            elif not in_quotes:
                in_quotes = True
            else:
                if i + 1 < len(S) and S[i + 1] == quotechar:
                    i += 1
                else:
                    in_quotes = False
            field += s
        elif s in ["\r", "\n"]:
            if in_quotes:
                field += s
            elif field == "" and row == []:
                pass
            else:
                end_row = True
                end_field = True
        elif s == delimiter:
            if in_escape:
                in_escape = False
                field += s
            elif in_quotes:
                field += s
            else:
                end_field = True
        elif s == escapechar:
            if in_escape:
                field += s
                in_escape = False
            else:
                in_escape = True
        else:
            if in_escape:
                field += escapechar
                in_escape = False
            field += s

        if end_field:
            if quote_cond(field, quotechar):
                field = field[1:-1]
            row.append(field)
            field = ""
            end_field = False

        if end_row:
            rows.append(row)
            row = []
            end_row = False

        i += 1

    if quote_cond(field, quotechar):
        field = field[1:-1]
    elif in_quotes:
        if field.startswith(quotechar):
            field = field[1:]
        s = ""
    if not s in ["\r", "\n", None]:
        row.append(field)
        rows.append(row)

    return rows
