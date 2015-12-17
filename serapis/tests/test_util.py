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
from serapis.util import read_csv
from serapis.util import write_csv
import os


def test_merge_dict():
    a = {'k1': 2, 'k2': 4}
    b = {'k1': 7, 'k2': None, 'k3': 5}
    merge_dict(a, b)
    assert a['k1'] == 7  # Updated
    assert a['k2'] == 4  # Unchanged!
    assert a['k3'] == 5  # Added


def test_csv():
    test_file = "serapis/tests/data/test_sentences.csv"
    rows = read_csv("serapis/tests/data/sentence_8000.csv", skip_header=True)
    assert len(rows) == 7874
    assert type(rows[0][1]) is unicode
    write_csv(rows[:10], test_file, header=("frd", "term", "sentence"))
    rows = read_csv(test_file, skip_header=True)
    assert len(rows) == 10
    assert type(rows[0][1]) is unicode
    os.remove(test_file)
