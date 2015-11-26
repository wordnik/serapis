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
__date__ = "2015-11-25"
__email__ = "manuel@summer.ai"


import yaml
import re


def test_wordnik_patterns_compile():
    from serapis.features import patterns
    for rule, pattern in patterns.items():
        assert re.compile(pattern), "Rule {} is not a valid regular expression".format(rule)


def test_wordnik_patterns_match():
    from serapis.features import match
    with open("serapis/tests/data/patterns.yaml") as f:
        test_cases = yaml.load(f)
    for rule, sentence in test_cases.items():
        assert match(sentence)[rule], "Rule {} does not match '{}'".format(rule, sentence)
