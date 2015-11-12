#!/usr/bin/env python3
# coding=utf-8
"""
Saves a FRD into a database
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

from objects import Term


def save(term: Term):
    """Saves the FRD
    """
    print("{}: '{:40}...' -> {:.3f}".format(term.url, str(term.sentence), term.rating))
