#!/usr/bin/env python3
# coding=utf-8
"""
FRD rating module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import math


def rate(result: dict) -> bool:
    """Rates the quality of an FRD
    """
    words = result['sentence'].split()
    return 1 - math.sqrt(1 / len(words))
