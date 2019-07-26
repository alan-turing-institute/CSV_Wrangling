#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Print the failure cases to the terminal.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import itertools
import numpy as np

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

from tabulate import tabulate

from common.dialect import ATTRIBUTES
from common.detector_result import Status

from .core import load_detector_results, is_standard_dialect


def parse_args():
    parser = argparse.ArgumentParser(
        description="Show failure cases for given detector results"
    )
    parser.add_argument(
        "-r",
        dest="reference_file",
        help="reference output file with ground truth",
        required=True,
    )
    parser.add_argument(
        "-d", dest="detector_file", help="detector output file", required=True
    )
    parser.add_argument(
        "-p",
        dest="attr_name",
        choices=ATTRIBUTES + ["overall"],
        help="Attribute to show failure for. If omitted, shows the files for which the detector failed.",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-c",
        dest="confusion",
        help="Plot and print the confusion matrix",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        dest="only_messy",
        help="Show only failures for messy files",
        action="store_true",
    )

    return parser.parse_args()


def show_complete_failure(
    ref_results, detector, det_results, only_messy=False
):
    print("Detector: %s. Failure cases." % detector)
    count = 0
    total = 0
    for fname in ref_results:
        res_ref = ref_results[fname]
        if not res_ref.status == Status.OK:
            continue
        if only_messy and is_standard_dialect(res_ref.dialect):
            continue
        total += 1
        if det_results[fname].status == Status.SKIP:
            continue
        if det_results[fname].status == Status.FAIL:
            print(fname)
            count += 1
    print(
        "Total: %i out of %i (%.2f%%)" % (count, total, (count / total * 100))
    )


def plot_confusion(cm, clean_classes):
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.colorbar()
    tick_marks = np.arange(len(clean_classes))

    plt.xticks(tick_marks, clean_classes, rotation=45)
    plt.yticks(tick_marks, clean_classes)

    fmt = "d"
    thresh = cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(
            j,
            i,
            format(cm[i, j], fmt),
            horizontalalignment="center",
            color="white" if cm[i, j] > thresh else "black",
        )
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()


def show_property_failure(
    ref_results, detector, det_results, attr_name, show_confusion=False,
    only_messy=False
):
    print("Detector: %s. Property: %s." % (detector, attr_name))
    count = 0
    total = 0
    y_true = []
    y_pred = []
    for fname in ref_results:
        res_ref = ref_results[fname]
        if not res_ref.status == Status.OK:
            continue
        if only_messy and is_standard_dialect(res_ref.dialect):
            continue
        total += 1
        if not det_results[fname].status == Status.OK:
            continue
        if attr_name == "overall":
            prop_ref = ref_results[fname].dialect
            prop_det = det_results[fname].dialect
            y_true.append(repr(prop_ref))
            y_pred.append(repr(prop_det))
        else:
            prop_ref = getattr(ref_results[fname].dialect, attr_name)
            prop_det = getattr(det_results[fname].dialect, attr_name)
            y_true.append(prop_ref)
            y_pred.append(prop_det)
        if not prop_ref == prop_det:
            print("%s  ref=%r  %s=%r" % (fname, prop_ref, detector, prop_det))
            count += 1
    print(
        "Total: %i out of %i (%.2f%%)" % (count, total, (count / total * 100))
    )
    if show_confusion:
        classes = []
        for c in y_true + y_pred:
            if not c in classes:
                classes.append(c)
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        trans = {
            "\t": "Tab",
            "": "Empty",
            " ": "Space",
            "。": "CDot",
            "：": "CCol",
        }
        clean = [trans.get(x, x) for x in classes]
        print(tabulate(cm, headers=clean, showindex=clean))
        plot_confusion(cm, clean)
        plt.show()


def main():
    args = parse_args()
    detector, det_results = load_detector_results(args.detector_file)
    _, ref_results = load_detector_results(args.reference_file)
    if args.attr_name is None:
        show_complete_failure(
            ref_results, detector, det_results, only_messy=args.only_messy
        )
    else:
        show_property_failure(
            ref_results,
            detector,
            det_results,
            args.attr_name,
            show_confusion=args.confusion,
            only_messy=args.only_messy,
        )
