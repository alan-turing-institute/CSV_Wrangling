#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Make summaries from the detector result files.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import argparse
import json

from common.dialect import ATTRIBUTES
from common.detector_result import Status

from .core import load_detector_results, is_standard_dialect


def prop_equal(res1, res2, attr_name):
    return getattr(res1.dialect, attr_name) == getattr(res2.dialect, attr_name)


def compute_attribute_accuracy(
    reference, detector, attr_name, detector_name, original_detector=None
):
    n_equal, n_total = 0, 0
    od = original_detector

    for fname in reference:
        res_ref = reference[fname]
        if not fname in detector:
            print(
                "Warning: no result for %s in for detector %s"
                % (fname, detector_name)
            )
            continue
        res_det = detector[fname]
        if od is not None and res_ref.original_detector != od:
            continue
        if not res_ref.status == Status.OK:
            continue
        n_total += 1
        if res_det.status == Status.OK:
            n_equal += prop_equal(res_ref, res_det, attr_name)

    return n_equal / n_total


def compute_overall_accuracy(
    reference, detector, detector_name, original_detector=None
):
    n_equal, n_total = 0, 0
    od = original_detector
    for fname in reference:
        res_ref = reference[fname]
        if not fname in detector:
            print(
                "Warning: no result for %s in for detector %s"
                % (fname, detector_name)
            )
            continue
        res_det = detector[fname]
        if od is not None and res_ref.original_detector != od:
            continue
        if not res_ref.status == Status.OK:
            continue
        n_total += 1
        if res_det.status == Status.OK:
            n_equal += res_ref.dialect == res_det.dialect
    return n_equal / n_total


def compute_standard_accuracy(reference, detector, standard=True):
    total_standard, total_messy = 0, 0
    correct_standard, correct_messy = 0, 0
    for fname in reference:
        res_ref = reference[fname]
        if not res_ref.status == Status.OK:
            continue
        if not fname in detector:
            print("Warning: no result for file: %s" % fname)
            continue
        res_det = detector[fname]

        is_std = is_standard_dialect(res_ref.dialect)
        if is_std:
            total_standard += 1
        else:
            total_messy += 1

        if not res_det.status == Status.OK:
            continue

        is_correct = res_det.dialect == res_ref.dialect
        if is_std:
            correct_standard += 1 if is_correct else 0
        else:
            correct_messy += 1 if is_correct else 0
    if standard:
        return correct_standard / total_standard
    return correct_messy / total_messy


def compute_fail_percentage(reference, detector, detector_name):
    n_fail, n_total = 0, 0
    for fname in reference:
        if reference[fname].status == Status.OK:
            n_total += 1
        else:
            continue
        if not fname in detector:
            print(
                "Warning: no result for %s in for detector %s"
                % (fname, detector_name)
            )
            continue
        if detector[fname].status == Status.FAIL:
            n_fail += 1
    return n_fail / n_total


def compute_nic_split_accuracy(reference, detector, mode=None):
    files_total = 0
    files_with_mode = 0
    for fname in reference:
        res_ref = reference[fname]
        if not res_ref.status == Status.OK:
            continue
        if not fname in detector:
            print("Warning: no result for file: %s" % fname)
            continue
        res_det = detector[fname]

        files_total += 1

        if mode == "no_results":
            if not res_det.status == Status.OK:
                files_with_mode += 1
        elif mode == "incorrect_results":
            if (
                res_det.status == Status.OK
                and res_det.dialect != res_ref.dialect
            ):
                files_with_mode += 1
        elif mode == "correct_results":
            if (
                res_det.status == Status.OK
                and res_det.dialect == res_ref.dialect
            ):
                files_with_mode += 1
        else:
            raise ValueError("Unknown mode: %r" % mode)
    return files_with_mode / files_total

def collect_computation_times(reference, detector, detector_name):
    runtimes = []
    for fname in sorted(reference.keys()):
        if not reference[fname].status == Status.OK:
            continue
        if not fname in detector:
            print(
                "Warning: no result for %s in for detector %s"
                % (fname, detector_name)
            )
            continue
        # Note that we don't check whether the detector returned with status
        # OK, because we want to include failures and timeouts in the runtime
        # plots as well.
        rt = detector[fname].runtime
        if rt is None:
            raise ValueError(
                "Runtime is None for result: %r" % detector[fname]
            )
        runtimes.append(detector[fname].runtime)

    return runtimes


def count_reference_ok(reference, original_detector=None):
    n_ok = 0
    od = original_detector
    for fname in reference:
        if od is not None and reference[fname].original_detector != od:
            continue
        if reference[fname].status == Status.OK:
            n_ok += 1
    return n_ok


def count_standard(reference_results, standard=True):
    count = 0
    for fname in reference_results:
        ref = reference_results[fname]
        if not ref.status == Status.OK:
            continue

        is_std = is_standard_dialect(ref.dialect)
        if standard:
            if is_std:
                count += 1
        else:
            if not is_std:
                count += 1
    return count


def summarize_accuracy(
    reference_results, detector_results_all, original_detector=None
):
    accuracy = {}
    for attr_name in ATTRIBUTES:
        accuracy[attr_name] = {}
        for detector in detector_results_all:
            detector_results = detector_results_all[detector]
            accuracy[attr_name][detector] = compute_attribute_accuracy(
                reference_results,
                detector_results,
                attr_name,
                detector,
                original_detector=original_detector,
            )

    assert "overall" not in accuracy.keys()
    accuracy["overall"] = {}
    for detector in detector_results_all:
        detector_results = detector_results_all[detector]
        accuracy["overall"][detector] = compute_overall_accuracy(
            reference_results,
            detector_results,
            detector,
            original_detector=original_detector,
        )
    return accuracy


def summarize_standard_accuracy(
    reference_results, detector_results_all, standard=True
):

    accuracy = {}
    for detector in detector_results_all:
        detector_results = detector_results_all[detector]
        accuracy[detector] = compute_standard_accuracy(
            reference_results, detector_results, standard=standard
        )
    return accuracy


def summarize_nic_split_accuracy(
    reference_results, detector_results_all, mode=None
):
    allowed_modes = ["no_results", "incorrect_results", "correct_results"]
    if mode is None or not mode in allowed_modes:
        raise ValueError("mode must be one of: %r" % allowed_modes)

    accuracies = {}
    for detector in detector_results_all:
        detector_results = detector_results_all[detector]
        accuracies[detector] = compute_nic_split_accuracy(
            reference_results, detector_results, mode=mode
        )
    return accuracies


def create_summary(reference_results, detector_results_all):
    summary = {}
    summary["n_files_all"] = count_reference_ok(
        reference_results, original_detector=None
    )
    summary["n_files_human"] = count_reference_ok(
        reference_results, original_detector="human"
    )
    summary["n_files_normal"] = count_reference_ok(
        reference_results, original_detector="normal"
    )
    summary["n_files_standard"] = count_standard(
        reference_results, standard=True
    )
    summary["n_files_messy"] = count_standard(
        reference_results, standard=False
    )

    # Compute accuracy
    summary["detection_accuracy_all"] = summarize_accuracy(
        reference_results, detector_results_all, original_detector=None
    )
    summary["detection_accuracy_human"] = summarize_accuracy(
        reference_results, detector_results_all, original_detector="human"
    )
    summary["detection_accuracy_normal"] = summarize_accuracy(
        reference_results, detector_results_all, original_detector="normal"
    )

    # Compute standard/non-standard split
    summary["standard_accuracy_all"] = summarize_standard_accuracy(
        reference_results, detector_results_all, standard=True
    )
    summary["messy_accuracy_all"] = summarize_standard_accuracy(
        reference_results, detector_results_all, standard=False
    )

    # Compute No result/Incorrect results/Correct result split
    summary["no_result_all"] = summarize_nic_split_accuracy(
        reference_results, detector_results_all, mode="no_results"
    )
    summary["incorrect_result_all"] = summarize_nic_split_accuracy(
        reference_results, detector_results_all, mode="incorrect_results"
    )
    summary["correct_result_all"] = summarize_nic_split_accuracy(
        reference_results, detector_results_all, mode="correct_results"
    )

    # Compute failure rates
    failures = {}
    for detector in detector_results_all:
        detector_results = detector_results_all[detector]
        failures[detector] = compute_fail_percentage(
            reference_results, detector_results, detector
        )
    summary["failures"] = failures

    # Collect runtimes
    runtimes = {}
    for detector in detector_results_all:
        detector_results = detector_results_all[detector]
        runtimes[detector] = collect_computation_times(
            reference_results, detector_results, detector
        )
    summary["runtimes"] = runtimes

    return summary


def parse_args():
    parser = argparse.ArgumentParser(description="Compare detector results")
    parser.add_argument(
        "-c",
        dest="corpus",
        help="Name of the corpus we're looking at",
        required=True,
    )
    parser.add_argument(
        "-s",
        dest="summary_file",
        help="output file for the summary statistics",
        required=True,
    )
    parser.add_argument(
        "-r",
        dest="reference_file",
        help="reference output file with ground truth",
        required=True,
    )
    parser.add_argument(
        "-o",
        dest="output_file",
        nargs="+",
        help="output_file(s) from different detectors",
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    _, ref_results = load_detector_results(args.reference_file)
    detector_results = {}
    for fname in args.output_file:
        name, results = load_detector_results(fname)
        detector_results[name] = results

    summary_data = create_summary(ref_results, detector_results)
    summary_data["corpus"] = args.corpus
    with open(args.summary_file, "w") as fid:
        fid.write(json.dumps(summary_data, indent=2))
