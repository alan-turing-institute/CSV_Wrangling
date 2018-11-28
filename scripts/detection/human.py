#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script should be opened within tmux and no other tmux sessions should be 
running.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import json
import libtmux
import os
import sys
import time

from common.encoding import get_encoding
from common.escape import is_potential_escapechar
from common.load import load_file
from common.detector_result import DetectorResult, Dialect, Status, StatusMsg
from common.utils import pairwise


def has_quotechar(data):
    chars = set(data)
    if '"' in chars or "'" in chars or "~" in chars or "`" in chars:
        return True
    return False


def get_quotechar_options(data):
    options = set()
    if '"' in data:
        options.add("q")
    if "'" in data:
        options.add("a")
    if "`" in data:
        options.add("b")
    if "~" in data:
        options.add("t")
    options.add("n")
    return options


def get_escapechar_options(data, encoding, delim, quotechar):
    escapes = set()
    for u, v in pairwise(data):
        if not is_potential_escapechar(u, encoding):
            continue
        if v in [delim, quotechar] and not u in [delim, quotechar]:
            escapes.add(u)
    return escapes


def ask_dqe(
    filename,
    data,
    encoding,
    ask_delim,
    ask_quotechar,
    ask_escapechar,
    old_res,
    less_pane,
):
    if not old_res is None:
        res = {
            "delimiter": old_res.get("delimiter", None),
            "quotechar": old_res.get("quotechar", None),
            "escapechar": old_res.get("escapechar", None),
        }
    else:
        res = {"delimiter": None, "quotechar": None, "escapechar": None}

    opened_vim = False
    opened_less = False

    note = None

    if ask_delim:
        less_pane.send_keys("less -f %s" % filename)
        opened_less = True
        prompt = "What is the delimiter? "
        while True:
            ans = input(prompt)
            if ans == "quit":
                less_pane.send_keys("q")
                opened_less = False
                less_pane.send_keys("exit")
                raise SystemExit
            if ans in ["vi", "vim"]:
                less_pane.send_keys("q")
                opened_less = False
                less_pane.send_keys("vim %s" % filename)
                opened_vim = True
                continue
            if ans in ["hltab", "hlt"]:
                less_pane.send_keys("/\\t")
                continue
            if ans in ["hlspace", "hls"]:
                less_pane.send_keys("/\\ ")
                continue
            if ans == "skip":
                if opened_less:
                    less_pane.send_keys("q")
                elif opened_vim:
                    less_pane.send_keys(":q")
                less_pane.clear()
                return None, note
            if ans == "note":
                note = input("Enter note: ").strip()
                continue
            if ans == "none":
                res["delimiter"] = None
            elif ans == "\\t":
                res["delimiter"] = "\t"
            elif len(ans.strip()) > 1:
                print("Only length 0 or 1 delimiters are allowed")
                continue
            else:
                res["delimiter"] = ans.rstrip("\n")
            break

    print("Delimiter: %r" % res["delimiter"])

    if opened_vim:
        less_pane.send_keys(":q")
        opened_vim = False
        time.sleep(1)
        less_pane.send_keys("less -f %s" % filename)
        opened_less = True

    if ask_quotechar:
        if not opened_less:
            less_pane.send_keys("less -f %s" % filename)
            opened_less = True

        options = get_quotechar_options(data)
        if "q" in options:
            less_pane.send_keys('/"')
            less_pane.send_keys("gg", enter=False, suppress_history=False)
            less_pane.send_keys("n", enter=False, suppress_history=False)
        elif "a" in options:
            less_pane.send_keys("/'")
            less_pane.send_keys("gg", enter=False, suppress_history=False)
            less_pane.send_keys("n", enter=False, suppress_history=False)
        opt_str = "/".join(sorted(options))
        prompt = "What is the quotation mark? [%s] " % opt_str
        while True:
            if list(options) == ["n"]:
                res["quotechar"] = None
                break
            ans = input(prompt)
            ans = ans.rstrip("\n")

            if ans == "quit":
                less_pane.send_keys("q")
                opened_less = False
                less_pane.send_keys("exit")
                raise SystemExit
            if ans in ["vi", "vim"]:
                less_pane.send_keys("q")
                opened_less = False
                less_pane.send_keys("vim %s" % filename)
                opened_vim = True
                continue
            if ans == "skip":
                if opened_less:
                    less_pane.send_keys("q")
                elif opened_vim:
                    less_pane.send_keys(":q")
                less_pane.clear()
                return None, note
            if ans == "note":
                note = input("Enter note: ").strip()
                continue
            if not ans.strip().lower() in options:
                print("Please try again.")
                continue
            if ans == "n":
                res["quotechar"] = None
            else:
                if not ans.upper() in ["Q", "A", "B", "T"]:
                    raise ValueError("Unknown option: %s" % ans)
                res["quotechar"] = {"Q": '"', "A": "'", "B": "`", "T": 
                        "~"}[ans.upper()]
            break

    print("Quotechar: %r" % res["quotechar"])

    if opened_vim:
        less_pane.send_keys(":q")
        opened_vim = False
        time.sleep(1)
        less_pane.send_keys("less -f %s" % filename)
        opened_less = True

    options = get_escapechar_options(
        data, encoding, res["delimiter"], res["quotechar"]
    )
    if ask_escapechar:
        if not options:
            print("No escapechar options.")
            res["escapechar"] = ""
        else:
            if not opened_less:
                less_pane.send_keys("less -f %s" % filename)
                opened_less = True
            if "n" in options:
                raise ValueError("'n' shouldn't be an option in escapechars!")
            if len(options) == 1:
                if '\\' in options:
                    less_pane.send_keys("/\\\\")
                less_pane.send_keys("gg", enter=False, suppress_history=False)
                less_pane.send_keys("n", enter=False, suppress_history=False)
            options.add("n")
            opt_str = "/".join(sorted(options))
            prompt = "What is the escape character? [%s] " % opt_str
            while True:
                ans = input(prompt)
                ans = ans.strip("\n")
                if ans == "quit":
                    less_pane.send_keys("q")
                    opened_less = False
                    less_pane.send_keys("exit")
                    raise SystemExit
                if ans == "skip":
                    if opened_less:
                        less_pane.send_keys("q")
                        less_pane.clear()
                    return None, note
                if ans == "note":
                    note = input("Enter note: ").strip()
                    continue
                if not ans.strip() in options:
                    print("Please try again")
                    continue
                if ans == "n":
                    res["escapechar"] = ""
                else:
                    res["escapechar"] = ans
                break

    print("Escapechar: %r" % res["escapechar"])

    if opened_less:
        less_pane.send_keys("q")
        less_pane.clear()
    return res, note


def annotate_file(filename, less_pane, previous):
    print("")
    encoding = get_encoding(filename)
    data = load_file(filename, encoding=encoding)

    if previous:
        ask_delim = not "delimiter" in previous
        ask_quotechar = not "quotechar" in previous and has_quotechar(data)
        ask_escapechar = not "escapechar" in previous
    else:
        ask_delim = True
        ask_quotechar = has_quotechar(data)
        ask_escapechar = True

    print("Annotating file: %s" % filename)
    res, note = ask_dqe(
        filename,
        data,
        encoding,
        ask_delim,
        ask_quotechar,
        ask_escapechar,
        previous,
        less_pane,
    )

    out = DetectorResult(
        detector="human", filename=filename, runtime=None, status=Status.OK
    )
    if note:
        out.note = note

    if res is None:
        less_pane.send_keys("q")
        less_pane.clear()
        out.status = Status.SKIP
        out.status_msg = StatusMsg.HUMAN_SKIP
        return out

    if res["delimiter"] is None:
        res["delimiter"] = ""
    if res["quotechar"] is None:
        res["quotechar"] = ""

    out.dialect = Dialect.from_dict(res)

    return out


def dump_result(output_file, res):
    with open(output_file, "a") as fid:
        fid.write(res.to_json() + "\n")


def load_previous(output_file):
    previous = {}
    if not os.path.exists(output_file):
        return previous
    with open(output_file, "r") as fid:
        for line in fid.readlines():
            record = json.loads(line.strip())
            previous[record["filename"]] = record
    return previous


def init_tmux():
    tmux_server = libtmux.Server()
    tmux_sess = tmux_server.list_sessions()[-1]
    tmux_win = tmux_sess.attached_window
    less_pane = tmux_win.split_window(attach=False)

    return less_pane


def batch_process(path_file, output_file):
    with open(path_file, "r") as fid:
        files = [l.strip() for l in fid.readlines()]
    files.sort()

    previous = load_previous(output_file)

    done = [x for x in files if x in previous and "dialect" in previous[x]]
    skipped = [
        x for x in files if x in previous and previous[x]["status"] == "SKIP"
    ]
    todo = [x for x in files if not (x in done or x in skipped)]

    if not todo:
        print("All done.")
        return

    print("Number of files remaining: %i" % len(todo))

    less_pane = init_tmux()

    count = 0
    start_time = time.time()
    for filename in todo:
        old_res = previous.get(filename, None)

        if not os.path.exists(filename):
            print("File not found: %s" % filename)
            res = DetectorResult(
                status=Status.SKIP, status_msg=StatusMsg.NON_EXISTENT
            )
            continue

        res = annotate_file(filename, less_pane, old_res)
        res.filename = filename
        dump_result(output_file, res)
        count += 1

        if count % 10 == 0:
            print(
                "\nProgress: %i done out of %i. "
                "This session: %i (%.2f seconds per file)"
                % (
                    count,
                    len(todo),
                    count,
                    ((time.time() - start_time) / count),
                )
            )

    print("All done.")


def main():
    if len(sys.argv) == 2:
        print(annotate_file(sys.argv[1], init_tmux()))
    elif len(sys.argv) == 3:
        batch_process(sys.argv[1], sys.argv[2])
    else:
        print("Usage: %s path_file output_file" % (sys.argv[0]))
        raise SystemExit


if __name__ == "__main__":
    main()
