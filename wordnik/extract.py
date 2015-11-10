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


def extract(body: str, word: str):
    """Extracts and yields sentences mentioning a word from the body text.
    """
    blob = TextBlob(body)
    for sentence in blob.sentences:
        if word.lower() in sentence.lower():
            yield sentence
