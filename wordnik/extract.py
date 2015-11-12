#!/usr/bin/env python3
# coding=utf-8
"""
Sentence extraction module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

from textblob import TextBlob
from objects import Term


def extract(term: Term):
    """Extracts and yields sentences mentioning a word from the body text.
    """
    blob = TextBlob(term.document)
    for sentence in blob.sentences:
        if term.term.lower() in sentence.lower():
            result = term.copy()
            result.sentence = sentence
            yield result
