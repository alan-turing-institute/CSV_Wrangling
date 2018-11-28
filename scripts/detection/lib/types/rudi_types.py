#!/usr/bin/env python

"""

Rudimentary types, used as a first pass to detect cell types given a potential 
delimiter.

Potentially add (small reward?):

    - Latitude and longitude
    - Alternative date(time) formats:
        x 2009-01-02T00:00
        x 18/10/2014
        x 04/07/11
        - 26-Feb
        - 10/12/2015 HH:MM
        - 10-Jul-12
        - Dec-13
    - File sizes and bandwidth speed
    - Unix Paths
    x Currency (\p{Sc} + float)


Notes:

    - Testing dates with Maya or Pendulum might work, but I got some false 
      positives such as "T2P" being interpreted as a time.

    - Maybe check out Moment.js? Many datetime formats for many locales. This 
      might be overkill for a "rudimentary type guess" though.

    x We can make this faster by compiling the regexes.

Should we consider a type hierarchy? Some urls (www.xxx.yyy) are also strings

Author: Gertjan van den Burg

"""

import regex
import sys


STRIP_WHITESPACE = True
TO_CHECK = []
CHECK_ALL = False

# Used this site: https://unicode-search.net/unicode-namesearch.pl
SPECIALS_ALLOWED = [
    # Periods
    "\u002e",
    "\u06d4",
    "\u3002",
    "\ufe52",
    "\uff0e",
    "\uff61",
    # Parentheses
    "\u0028",
    "\u0029",
    "\u27ee",
    "\u27ef",
    "\uff08",
    "\uff09",
    # Question marks
    "\u003F",
    "\u00BF",
    "\u037E",
    "\u055E",
    "\u061F",
    "\u1367",
    "\u1945",
    "\u2047",
    "\u2048",
    "\u2049",
    "\u2CFA",
    "\u2CFB",
    "\u2E2E",
    "\uA60F",
    "\uA6F7",
    "\uFE16",
    "\uFE56",
    "\uFF1F",
    chr(69955),  # chakma question mark
    chr(125279),  # adlam initial question mark
    # Exclamation marks
    "\u0021",
    "\u00A1",
    "\u01C3",
    "\u055C",
    "\u07F9",
    "\u109F",
    "\u1944",
    "\u203C",
    "\u2048",
    "\u2049",
    "\uAA77",
    "\uFE15",
    "\uFE57",
    "\uFF01",
    chr(125278),  # adlam initial exclamation mark
]

PATTERNS = {
    "number_1": regex.compile(
        "(?=[+-\.\d])[+-]?(?:0|[1-9]\d*)?(((?P<dot>\.)?(?(dot)(?P<yes_dot>\d*(\d+[eE][+-]?\d+)?)|(?P<no_dot>([eE][+-]?\d+)?)))|((?P<comma>,)?(?(comma)(?P<yes_comma>\d+(\d+[eE][+-]?\d+)?)|(?P<no_comma>([eE][+-]?\d+)?))))"
    ),
    "number_2": regex.compile("[+-]?(?:[1-9]|[1-9]\d{0,2})(?:\,\d{3})+\.\d*"),
    "number_3": regex.compile("[+-]?(?:[1-9]|[1-9]\d{0,2})(?:\.\d{3})+\,\d*"),
    "url": regex.compile(
        "(?:(?:[A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)(?:(?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?"
    ),
    "email": regex.compile(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    ),
    "unicode_alphanum": regex.compile(
        "(\p{N}+\p{L}+[\p{N}\p{L}\ "
        + regex.escape("".join(SPECIALS_ALLOWED))
        + "]*|\p{L}+[\p{N}\p{L}\ "
        + regex.escape("".join(SPECIALS_ALLOWED))
        + "]+)"
    ),
    "time_hhmmss": regex.compile(
        "(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])"
    ),
    "time_hhmm": regex.compile("(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])"),
    "time_HHMM": regex.compile("(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])"),
    "time_HH": regex.compile("(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])"),
    "time_hmm": regex.compile("([0-9]|1[0-9]|2[0-3]):([0-5][0-9])"),
    "currency": regex.compile("\p{Sc}\s?(.*)"),
    "unix_path": regex.compile(
        "[\/~]{1,2}(?:[a-zA-Z0-9\.]+(?:[\/]{1,2}))+(?:[a-zA-Z0-9\.]+)"
    ),
}


def load_date_patterns():
    year2 = "(?:\d{2})"
    year4 = "(?:[12]\d{3})"

    month_leading = "(?:0[1-9]|1[0-2])"
    month_sparse = "(?:[1-9]|1[0-2])"

    day_leading = "(?:0[1-9]|[12]\d|3[01])"
    day_sparse = "(?:[1-9]|[12]\d|3[01])"

    sep = "[-/\.\ ]"

    counter = 0
    for year in [year2, year4]:
        for month in [month_leading, month_sparse]:
            for day in [day_leading, day_sparse]:
                fmt = {"year": year, "month": month, "day": day, "sep": sep}

                pat_1 = "{year}{sep}{month}{sep}{day}".format(**fmt)
                pat_2 = "{day}{sep}{month}{sep}{year}".format(**fmt)
                pat_3 = "{month}{sep}{day}{sep}{year}".format(**fmt)

                pat_cn = "{year}年{month}月{day}日".format(**fmt)
                pat_ko = "{year}년{month}월{day}일".format(**fmt)

                for pattern in [pat_1, pat_2, pat_3, pat_cn, pat_ko]:
                    PATTERNS["date_%i" % counter] = regex.compile(pattern)
                    counter += 1

    # These should be allowed as dates, but are also numbers.
    for year in [year2, year4]:
        fmt = {
            "year": year,
            "month": month_leading,
            "day": day_leading,
            "sep": "",
        }
        pat_1 = "{year}{sep}{month}{sep}{day}".format(**fmt)
        pat_2 = "{day}{sep}{month}{sep}{year}".format(**fmt)
        pat_3 = "{month}{sep}{day}{sep}{year}".format(**fmt)

        for pattern in [pat_1, pat_2, pat_3, pat_cn]:
            PATTERNS["date_%i" % counter] = regex.compile(pattern)
            counter += 1


# TODO Ugly to do this here, but this is research code...

load_date_patterns()


def test_with_regex(cell, patname):
    # Test if cell *fully* matches reg (e.g. entire cell is number, maybe allow
    # stripping of leading/trailing spaces)
    if STRIP_WHITESPACE:
        cell = cell.strip()
    pat = PATTERNS.get(patname, None)
    match = pat.fullmatch(cell)
    return match is not None


def test_number(cell):
    # NOTE: This is more general than trying to coerce to float(), because it
    # allows use of the comma as radix point.
    if cell == "":
        return False
    if test_with_regex(cell, "number_1"):
        return True
    if test_with_regex(cell, "number_2"):
        return True
    if test_with_regex(cell, "number_3"):
        return True
    return False


def test_url_or_email(cell):
    return test_with_regex(cell, "url") or test_with_regex(cell, "email")


def test_unicode_alphanum(cell):
    # TODO: I'm not sure if it's desirable to allow alphanumeric cells, because
    # it's not clear if they include "junk" cells due to incorrect delimiter
    # (think: space). Maybe it's better to have only character cells?
    # NOTE: This function assumes that number and url are already excluded.

    return test_with_regex(cell, "unicode_alphanum")


def test_date(cell):
    if test_number(cell):
        return False

    for patname in PATTERNS:
        if patname.startswith("date_"):
            if test_with_regex(cell, patname):
                return True
    return False


def test_time(cell):
    # HH:MM:SS, HH:MM, or H:MM
    return (
        test_with_regex(cell, "time_hmm")
        or test_with_regex(cell, "time_hhmm")
        or test_with_regex(cell, "time_hhmmss")
    )


def test_empty(cell):
    if STRIP_WHITESPACE:
        cell = cell.strip()
    return cell == ""


def test_percentage(cell):
    cell = cell.strip()
    return cell.endswith("%") and test_number(cell.rstrip("%"))


def test_currency(cell):
    if STRIP_WHITESPACE:
        cell = cell.strip()
    pat = PATTERNS.get("currency", None)
    m = pat.fullmatch(cell)
    if m is None:
        return False
    grp = m.group(1)
    if not test_number(grp):
        return False
    return True


def test_datetime(cell):
    # Takes care of cells with '[date] [time]' and '[date]T[time]' (iso)
    if " " in cell:
        parts = cell.split(" ")
        if len(parts) > 2:
            return False
        return test_date(parts[0]) and test_time(parts[1])
    elif "T" in cell:
        parts = cell.split("T")
        if len(parts) > 2:
            return False
        isdate = test_date(parts[0])
        if not isdate:
            return False
        # [date]T[time]
        if test_time(parts[1]):
            return True
        # [date]T[time][+-][time]
        if "+" in parts[1]:
            subparts = parts[1].split("+")
            istime1 = test_time(subparts[0])
            istime2 = test_time(subparts[1])
            if not istime1:
                return False
            if istime2:
                return True
            if test_with_regex(subparts[1], "time_HHMM"):
                return True
            if test_with_regex(subparts[1], "time_HH"):
                return True
        elif "-" in parts[1]:
            subparts = parts[1].split("-")
            istime1 = test_time(subparts[0])
            istime2 = test_time(subparts[1])
            if not istime1:
                return False
            if istime2:
                return True
            if test_with_regex(subparts[1], "time_HHMM"):
                return True
            if test_with_regex(subparts[1], "time_HH"):
                return True
    return False


def test_nan(cell):
    if STRIP_WHITESPACE:
        cell = cell.strip()
    # other forms (na and nan) are caught by unicode_alphanum
    if cell.lower() == "n/a":
        return True
    return False


def eval_types(cell, break_away=True):
    type_tests = [
        ("empty", test_empty),
        ("url_or_email", test_url_or_email),
        ("number", test_number),
        ("time", test_time),
        ("percentage", test_percentage),
        ("currency", test_currency),
        ("unicode_alphanum", test_unicode_alphanum),
        ("nan", test_nan),
        ("date", test_date),
        ("datetime", test_datetime),
    ]

    detected = []
    for name, func in type_tests:
        if func(cell):
            detected.append(name)
            if break_away:
                break

    if len(detected) > 1:
        print(
            "Type tests aren't mutually exclusive!\nCell: %r\nTypes: %r"
            % (cell, detected),
            file=sys.stderr,
        )
        raise ValueError
    if len(detected) == 0:
        return None
    return detected[0]
