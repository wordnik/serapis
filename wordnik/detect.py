#!/usr/bin/env python3
# coding=utf-8
"""
FRD detection module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

from objects import Term


def detect(term: Term) -> bool:
    """Determines whether a sentence is an FRD.
    """
    # Let's make this simple
    return term.term.lower() in term.document.lower()
