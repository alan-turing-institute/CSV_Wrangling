#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate a HTML test page to compare the arXiv submitted version with what 
Travis generates.

Author: Gertjan van den Burg
Date: 2019-05-17

"""

import argparse
import dominate
import hashlib
import sys
import os
import base64

domtags = dominate.tags
domutil = dominate.util

CSS = r"""
body {
    background-color: #2c2c2c;
    color: #fffff1;
}
h1 {
    margin: 0 auto;
    max-width: 90%;
    text-align: center;
}
a {
    color: #fffff1;
}
.intro {
    margin: 0 auto;
    max-width: 80%;
}
.container {
    margin: 0 auto;
    max-width: 90%;
}
.wrapper {
    width: 100%;
    margin: auto;
    padding: 10px;
}
.arxiv {
    width: 45%;
    float: left;
    padding: 5pt;
}
.generated {
    margin-left: 50%;
    width: 45%;
    padding: 5pt;
}
.wrapper .name {
    display: block;
}
.code-wrap {
    border: solid;
    border-width: 1px;
}
.correct {
    border-color: green;
}
.incorrect {
    border-color: red;
}
code {
    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
    line-height: 1.6;
    overflow-x: auto;
}
"""


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    raise SystemExit(1)


def md5sum(filename):
    blocksize = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as fid:
        buf = fid.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fid.read(blocksize)
    return hasher.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result-dir",
        required=True,
        help="Directory with generated results.",
        dest="result_dir",
    )
    parser.add_argument(
        "--tar-dir",
        required=True,
        help="Directory with files extracted from tar file.",
        dest="tar_dir",
    )
    parser.add_argument("--output", required=True, help="Output file")
    return parser.parse_args()


def main():
    args = parse_args()

    doc = dominate.document(title="Verifying arXiv:1811.11242")
    with doc.head:
        domtags.meta(charset="utf-8")
        domtags.style(CSS)

    with doc:
        domtags.h1("Verifying arXiv:1811.11242")
        with domtags.div(_class="intro"):
            with domtags.p():
                domutil.text("This page compares the results for the ")
                domtags.a(
                    "CSV Wrangling paper",
                    href="https://arxiv.org/abs/1811.11242",
                )
                domutil.text(
                    """ as submitted to arXiv with those generated by Travis.  
                    This serves to illustrate the reproducibility and 
                    verifiability of the work """
                )
                domtags.a(
                    "(available here)",
                    href="https://github.com/alan-turing-institute/CSV_Wrangling",
                )
                domutil.text(". I admit this may be taking it a bit too far.")

    container = doc.add(domtags.div(_class="container"))

    section = None

    for root, dirs, files in os.walk(args.tar_dir):
        local_root = root[len(args.tar_dir) :]
        local_root = local_root.lstrip("/")
        if (
            local_root in ["constants", "figures", "tables"]
            and not local_root == section
        ):
            container.add(
                domtags.h3(local_root.capitalize(), _class="section")
            )
            section = local_root
        for filename in sorted(files):
            tar_pth = os.path.join(args.tar_dir, local_root, filename)
            gen_pth = os.path.join(args.result_dir, local_root, filename)

            if not os.path.exists(gen_pth):
                exception(
                    "File '{filename}' missing from generated results.".format(
                        filename=gen_pth
                    )
                )

            tar_md5 = md5sum(tar_pth)
            gen_md5 = md5sum(gen_pth)

            wrapper = container.add(domtags.div(_class="wrapper"))
            wrapper.add(domtags.span(domtags.b(filename), _class="name"))

            extension = os.path.splitext(filename)[-1]
            if extension == ".tex":
                cls = "correct" if tar_md5 == gen_md5 else "incorrect"
                with wrapper.add(domtags.div(_class="arxiv")):
                    domtags.p("arXiv:")
                    with domtags.div(_class="code-wrap " + cls):
                        domtags.code(open(tar_pth).read())

                with wrapper.add(domtags.div(_class="generated")):
                    domtags.p("Generated:")
                    with domtags.div(_class="code-wrap " + cls):
                        domtags.code(open(gen_pth).read())

                if tar_md5 == gen_md5:
                    wrapper.add(
                        domtags.span(domutil.raw("Exact match: &#x2705;"))
                    )
                else:
                    wrapper.add(
                        domtags.span(domutil.raw("Exact match: &#x274C;"))
                    )

            elif extension == ".pdf":
                with wrapper.add(domtags.div(_class="arxiv")):
                    domtags.object_(
                        data="data:application/pdf;base64,"
                        + base64.b64encode(open(tar_pth, "rb").read()).decode(
                            "utf-8"
                        ),
                        width="100%",
                        height="250px",
                        type="application/pdf",
                    )

                with wrapper.add(domtags.div(_class="generated")):
                    domtags.object_(
                        data="data:application/pdf;base64,"
                        + base64.b64encode(open(gen_pth, "rb").read()).decode(
                            "utf-8"
                        ),
                        width="100%",
                        height="250px",
                        type="application/pdf",
                    )
                wrapper.add(
                    domtags.p(
                        "PDF figures aren't automatically checked due to reproducibility limitations of pdflatex that weren't addressed in the original version submitted to arXiv."
                    )
                )

    with open(args.output, "w") as fp:
        fp.write(str(doc))


if __name__ == "__main__":
    main()
