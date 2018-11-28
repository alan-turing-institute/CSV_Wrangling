#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shared utility functions.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""

import math


def pairwise(iterable):
    "s - > (s0, s1), (s1, s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)
    next(b, None)
    return zip(a, b)


def softmax(iterable):
    maxx = max(iterable)
    offset = [x - maxx for x in iterable]
    denom = sum(map(math.exp, offset))
    return [math.exp(o) / denom for o in offset]
