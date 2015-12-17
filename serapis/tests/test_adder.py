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
__date__ = "2015-12-17"
__email__ = "manuel@summer.ai"

from serapis.qualify_word import clean_and_qualify
import codecs


def test_qualify():
    with codecs.open("serapis/tests/data/words_qualified.txt", 'r', 'utf-8') as wordlist:
        for word in wordlist.readlines():
            assert clean_and_qualify(word), "Word '{}' falsely marked as invalid".format(word.strip())


def test_disqualify():
    with codecs.open("serapis/tests/data/words_disqualified.txt", 'r', 'utf-8') as wordlist:
        for word in wordlist.readlines():
            assert not clean_and_qualify(word), "Word '{}' falsely marked as valid".format(word.strip())
