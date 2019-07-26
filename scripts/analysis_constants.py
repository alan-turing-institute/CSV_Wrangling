#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper for constants generation.

The constants are generated with separate Python scripts available in the 
``analysis`` directory. This file provides a wrapper. See the scripts of each 
of the different constants for more info.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import sys

from analysis import (
    constant_n_dialect,
    constant_n_files,
    constant_n_incorrect_prop,
    constant_accuracy_overall,
    constant_improve_sniffer,
    constant_improve_sniffer_messy,
    constant_fail_percentage,
    constant_failure,
    constant_failure_messy,
    constant_prop_potential_dialect,
    constant_known_type,
)


def main():
    const_name = sys.argv.pop(1)
    if const_name == "n_dialect":
        constant_n_dialect.main()
    elif const_name == "n_files":
        constant_n_files.main()
    elif const_name == "accuracy_overall":
        constant_accuracy_overall.main()
    elif const_name == "improve_sniffer":
        constant_improve_sniffer.main()
    elif const_name == "improve_sniffer_messy":
        constant_improve_sniffer_messy.main()
    elif const_name == "failure":
        constant_failure.main()
    elif const_name == "fail_percentage":
        constant_fail_percentage.main()
    elif const_name == "num_incorrect_prop":
        constant_n_incorrect_prop.main()
    elif const_name == "prop_potential_dialect":
        constant_prop_potential_dialect.main()
    elif const_name == "fail_percentage_messy":
        constant_failure_messy.main()
    elif const_name == "known_type":
        constant_known_type.main()
    else:
        raise ValueError("Unknown constant: %s" % const_name)


if __name__ == "__main__":
    main()
