#!/usr/bin/env python
# coding=utf-8
"""
Collection of tests.

Tests methods need to start with "test_", otherwise you're free to do
whatever you want here.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-12-07"
__email__ = "manuel@summer.ai"

from serapis.util import merge_dict


def test_merge_dict():
    a = {'k1': 2, 'k2': 4}
    b = {'k1': 7, 'k2': None, 'k3': 5}
    merge_dict(a, b)
    assert a['k1'] == 7  # Updated
    assert a['k2'] == 4  # Unchanged!
    assert a['k3'] == 5  # Added
