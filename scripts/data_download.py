#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Downloader for the experimental data.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.
Date: 2018-11-26

"""

import argparse
import hashlib
import json
import os
import requests
import sys
import tempfile
import shutil


def md5sum(filename):
    blocksize = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as fid:
        buf = fid.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fid.read(blocksize)
    return hasher.hexdigest()


def download_url(urls, md5old, output_dir):
    tmpfd, tmpfname = tempfile.mkstemp()
    tmpfid = os.fdopen(tmpfd, "wb")

    req = None
    for url in urls:
        # TODO: Catch error when URL no longer exists
        try:
            req = requests.get(url, stream=True)
            break
        except requests.exceptions.ConnectionError:
            print(
                "Connection error occurred trying to get url: %s" % url,
                file=sys.stderr,
            )
            continue
    if req is None:
        return None

    for chunk in req.iter_content(chunk_size=1024):
        if chunk:
            tmpfid.write(chunk)
    tmpfid.close()

    md5new = md5sum(tmpfname)
    if not md5new == md5old:
        print(
            "Checksum mismatch for URL '%s'. Skipping this file." % url,
            file=sys.stderr,
        )
        return None
    target = os.path.join(output_dir, md5new + ".csv")
    shutil.move(tmpfname, target)
    return target


def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-i",
        "--input",
        help="JSONlines file with urls and hashes",
        required=True,
    )
    parser.add_argument(
        "-o", "--output", help="output directory", required=True
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # load the input file
    url_and_hash = []
    with open(args.input, "r") as fid:
        for line in fid:
            obj = json.loads(line.strip())
            url_and_hash.append(obj)

    # Remove files that already exist
    have_obj = []
    have_files = os.listdir(args.output)
    for f in have_files:
        h = os.path.splitext(f)[0]
        obj = next((x for x in url_and_hash if x["md5"] == h), None)
        if obj is None:
            # ignore files not in our list
            continue
        have_obj.append(obj)
    for obj in have_obj:
        url_and_hash.remove(obj)

    # start the download
    for obj in url_and_hash:
        target = download_url(obj["urls"], obj["md5"], args.output)
        if target is None:
            continue
        print("Downloaded file '%s'" % target)


if __name__ == "__main__":
    main()
