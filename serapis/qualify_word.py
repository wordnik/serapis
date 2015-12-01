#!/usr/bin/env python
# coding=utf-8
"""
DOC
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-30"
__email__ = "manuel@summer.ai"


def qualify(term):
    """Decides whether a word is a potential candidate.
    """
    # Comments are how many disqualified words out of 10k the rule caught
    # Ordered it in descending order (fast failure mode)
    if any(len(word) > 15 for word in term.split()):  # 51%
        return False
    if term.count(" ") > 5:  # 28%
        return False
    if any(c in term for c in "█,!?:"):  # 18%
        return False
    if len(term) < 3:  # 1%
        return False
    if sum(ord(c) > 255 for c in term) > 2:  # 0.8%
        return False
    if "__" in term:  # 0.6%
        return False
    return True


def clean(term):
    return term.strip(" \n[](),.")
