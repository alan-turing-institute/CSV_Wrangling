#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This detector uses the Python CSV Sniffer to detect the dialect.

A timeout is needed on the Sniffer because the regular expression for detecting 
double quotes can run into catastrophic backtracking if a CSV file has many 
empty lines at the end that only contain delimiters (i.e. ",,,,,,,,,," lines).

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import csv

from multiprocessing import Process, Manager

from .core import run

from common.encoding import get_encoding
from common.load import load_file
from common.detector_result import DetectorResult, Dialect, Status, StatusMsg

DETECTOR = "sniffer"
TIMEOUT = 120


def worker(args, return_dict, **kwargs):
    res = determine_dqr(*args, **kwargs)
    return_dict["output"] = res


def run_with_timeout(args, kwargs, limit):
    # See: https://stackoverflow.com/a/26664130/1154005
    # and: https://stackoverflow.com/a/10415215/1154005

    manager = Manager()
    return_dict = manager.dict()

    p = Process(target=worker, args=(args, return_dict), kwargs=kwargs)
    p.start()
    p.join(limit)
    if p.is_alive():
        p.terminate()
        return None
    if "output" in return_dict:
        return return_dict["output"]
    return None


def sniff(sample, delimiters=None):
    """
    This function mimics the Sniffer.sniff() method from the Python CSV 
    function, with one exception: it doesn't change the detected quotechar to 
    default to '"'. We do this because we want to know the detected quote 
    character.

    """
    sniffer = csv.Sniffer()

    quotechar, doublequote, delimiter, skipinitialspace = sniffer._guess_quote_and_delimiter(
        sample, delimiters
    )

    if not delimiter:
        delimiter, skipinitialspace = sniffer._guess_delimiter(
            sample, delimiters
        )
    if not delimiter:
        raise csv.Error("Could not determine delimiter")

    class dialect(csv.Dialect):
        _name = "sniffed"
        lineterminator = "\r\n"  # unused
        quoting = csv.QUOTE_MINIMAL

    dialect.doublequote = doublequote
    dialect.delimiter = delimiter
    dialect.quotechar = quotechar  # See above
    dialect.skipinitialspace = skipinitialspace
    dialect.escapechar = '' if dialect.escapechar is None else dialect.escapechar

    return dialect


def determine_dqr(filename, verbose=False):
    """ Run the python CSV Sniffer """
    encoding = get_encoding(filename)
    data = load_file(filename, encoding=encoding)
    if data is None:
        return DetectorResult(
            status=Status.SKIP, status_msg=StatusMsg.UNREADABLE
        )

    try:
        dialect = sniff(data)
    except csv.Error:
        return DetectorResult(
            status=Status.FAIL, status_msg=StatusMsg.NO_RESULTS
        )

    config = {
        "delimiter": dialect.delimiter,
        "quotechar": dialect.quotechar,
        "escapechar": dialect.escapechar,
    }
    res = DetectorResult(dialect=Dialect.from_dict(config), status=Status.OK)

    return res


def wrap_determine_dqr(filename, verbose=False):
    res = run_with_timeout((filename,), {"verbose": verbose}, TIMEOUT)
    if res is None:
        return DetectorResult(status=Status.FAIL, status_msg=StatusMsg.TIMEOUT)
    return res


def main():
    run(determine_dqr=wrap_determine_dqr, detector=DETECTOR)
