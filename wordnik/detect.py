#!/usr/bin/env python3
# coding=utf-8
"""
FRD detection module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"


def detect(sentence: str, word: str) -> bool:
    """Determines whether a sentence is an FRD.
    """
    # Let's make this simple
    return word.lower() in sentence.lower()
