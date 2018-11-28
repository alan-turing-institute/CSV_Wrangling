#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definitions for a DetectorResult object.

Author: Gertjan van den Burg
Copyright (c) 2018 - The Alan Turing Institute
License: See the LICENSE file.

"""


import enum
import json
import socket
import sys

from .dialect import Dialect


class Status(enum.Enum):
    UNKNOWN = 0
    OK = 1
    FAIL = 2
    SKIP = 3


class StatusMsg(enum.Enum):
    UNKNOWN = 0
    MULTIPLE_ANSWERS = 1
    NO_RESULTS = 2
    TIMEOUT = 3
    UNREADABLE = 4
    NON_EXISTENT = 5
    NO_DIALECTS = 6
    HUMAN_SKIP = 7
    AMBIGUOUS_QUOTECHAR = 8


class DetectorResult(object):
    def __init__(
        self,
        detector=None,
        dialect=None,
        filename=None,
        hostname=None,
        runtime=None,
        status=None,
        status_msg=None,
        original_detector=None,
        note=None
    ):
        self.detector = detector
        self.dialect = dialect
        self.filename = filename
        self.hostname = hostname or socket.gethostname()
        self.runtime = runtime
        self.status = status
        self.status_msg = status_msg
        self.original_detector = original_detector or detector
        self.note = note

    def validate(self):
        assert isinstance(self.status, Status)
        if not self.status_msg is None:
            assert isinstance(self.status_msg, StatusMsg)
        assert not self.detector is None
        assert not self.hostname is None
        assert not self.filename is None
        if self.status == Status.OK:
            assert not self.dialect is None
            assert isinstance(self.dialect, Dialect)
            try:
                self.dialect.validate()
            except ValueError:
                print("Dialect validation error for: %r" % self)
                raise
        else:
            assert self.dialect is None

    def to_json(self):
        self.validate()
        output = {
            "detector": self.detector,
            "filename": self.filename,
            "hostname": self.hostname,
            "runtime": self.runtime,
            "status": self.status.name,
        }
        if not self.dialect is None:
            output["dialect"] = self.dialect.to_dict()
        if not self.status_msg is None:
            output["status_msg"] = self.status_msg.name
        if not self.note is None:
            output['note'] = self.note
        if not self.detector == self.original_detector:
            output["original_detector"] = self.original_detector
        as_json = json.dumps(output)
        return as_json

    @classmethod
    def from_json(cls, line):
        """ load from a json line """
        d = json.loads(line)
        try:
            d["dialect"] = (
                Dialect.from_dict(d["dialect"]) if "dialect" in d else None
            )
        except:
            print("Error occurred parsing dialect from line: %s" % line, 
                    file=sys.stderr)
            raise
        d["status"] = Status[d["status"]]
        d["status_msg"] = (
            StatusMsg[d["status_msg"]] if "status_msg" in d else None
        )
        dr = cls(**d)
        dr.validate()
        return dr

    def __repr__(self):
        s = (
            "DetectorResult(detector=%r, dialect=%r, runtime=%r, status=%r, status_msg=%r)"
            % (
                self.detector,
                self.dialect,
                self.runtime,
                self.status.value,
                self.status_msg,
            )
        )
        return s
