#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper around result generation.

See the individual scripts for more usage info.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import sys

from analysis import (
    figure_fail,
    figure_bar_plot,
    figure_box_plot,
    figure_violins,
    table_accuracy,
    table_std_messy,
    table_parse_result
)


def main():
    result_type = sys.argv.pop(1)
    if result_type == "fail_figure":
        figure_fail.main()
    elif result_type == "accuracy_bar":
        figure_bar_plot.main()
    elif result_type == "boxplot":
        figure_box_plot.main()
    elif result_type == "violins":
        figure_violins.main()
    elif result_type == "tables":
        table_accuracy.main()
    elif result_type == "std_messy":
        table_std_messy.main()
    elif result_type == "parse_result":
        table_parse_result.main()
    else:
        raise ValueError("Unknown result type: %s" % result_type)


if __name__ == "__main__":
    main()
