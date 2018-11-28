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
    generate_fail_figure,
    generate_bar_plot,
    generate_box_plots,
    generate_violin_plots_both,
    generate_tables,
    generate_non_standard_table,
)


def main():
    result_type = sys.argv.pop(1)
    if result_type == "fail_figure":
        generate_fail_figure.main()
    elif result_type == "accuracy_bar":
        generate_bar_plot.main()
    elif result_type == "boxplot":
        generate_box_plots.main()
    elif result_type == "violins":
        generate_violin_plots_both.main()
    elif result_type == "tables":
        generate_tables.main()
    elif result_type == "std_messy":
        generate_non_standard_table.main()
    else:
        raise ValueError("Unknown result type: %s" % result_type)


if __name__ == "__main__":
    main()
