#!/usr/bin/env python3
# coding=utf-8
"""
Config Handler
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-12"
__email__ = "manuel@summer.ai"


class Term:
    def __init__(self, term):
        self.term = term
        self.is_frd = False
        self.rating = None

        self.url = None
        self.summary = None
        self.date = None
        self.title = None
        self.author = None
        self.document = None
        self.sentence = None

    def copy(self):
        new = Term(self.term)
        new.__dict__.update(self.__dict__)
        return new
