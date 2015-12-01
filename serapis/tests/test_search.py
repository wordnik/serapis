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


import csv
from serapis.config import config
config.load()


def test_language_detection():
    from serapis.language import detect_language
    with open("serapis/tests/data/language_detection.csv") as f:
        test_cases = list(csv.reader(f))
    for language, sentence in test_cases:
        sentence = sentence.decode('utf-8')
        detected_language = detect_language(sentence)
        assert language == detected_language, "Classified '{}...' as {}, but should be {}".format(sentence[:40], detected_language, language)


def test_english_detection():
    from serapis.language import is_english
    with open("serapis/tests/data/language_detection.csv") as f:
        test_cases = list(csv.reader(f))
    for language, sentence in test_cases:
        sentence = sentence.decode('utf-8')
        detected_english = is_english(sentence)
        if 'english' == language:
            assert detected_english, "Falsely classified '{}...' as non-English".format(sentence[:40])
        else:
            assert not detected_english, "Falsely classified '{}...' as English".format(sentence[:40])


def test_duckduckgo():
    from serapis.search import search_duckduckgo
    result = search_duckduckgo("egregore")
    assert result
