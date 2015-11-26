#!/usr/bin/env python
# coding=utf-8
"""
Compilation script. Everything that can be precompiled should be done here.
Invoke this script with

    python -m serapis.compile

before packaging the application.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, Manuel Ebert"
__date__ = "2015-11-25"
__email__ = "manuel@1450.me"

from . import patterns

if __name__ == "__main__":
    patterns = patterns.compile()
