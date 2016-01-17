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
import unicodecsv as csv


def test_wordnik_patterns_compile():
    from serapis.features import patterns
    for rule, pattern in patterns.items():
        assert re.compile(pattern), "Rule {} is not a valid regular expression".format(rule)


def test_wordnik_patterns_match():
    from serapis.features import match_wordnik_rules
    with open("serapis/tests/data/patterns.yaml") as f:
        test_cases = yaml.load(f)
    for rule, sentence in test_cases.items():
        assert rule in match_wordnik_rules(sentence), "Rule {} does not match '{}'".format(rule, sentence)


def test_wordnik_patterns_perc():
    from serapis.features import match_wordnik_rules
    from serapis.preprocess import clean_sentence
    min_coverage = 0.2
    matches = 0.0
    with open("serapis/tests/data/frds_wordnik.csv") as f:
        test_cases = list(csv.reader(f))
    for term, sentence in test_cases:
        s_clean, _ = clean_sentence(sentence, term)
        matches += 1 if match_wordnik_rules(s_clean) else 0
    assert matches / len(test_cases) > min_coverage, "Only matched {:.2f}% of data set".format(100 * matches / len(test_cases))
