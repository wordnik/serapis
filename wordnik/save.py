#!/usr/bin/env python3
# coding=utf-8
"""
Saves a FRD into a database
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"


def save(result: dict):
    """Saves the FRD
    """
    print("{}: '{:40}...' -> {:.3f}".format(result['url'], str(result['sentence']), result['rating']))
