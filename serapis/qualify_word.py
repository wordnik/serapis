#!/usr/bin/env python
# coding=utf-8
"""
DOC
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-30"
__email__ = "manuel@summer.ai"

from unidecode import unidecode
import re


def qualify(term):
    """Decides whether a word is a potential candidate.

    Returns:
        bool -- True if the word qualifies
    """
    # Comments are how many disqualified words out of 10k the rule caught
    # Ordered it in descending order (fast failure mode)
    if any(len(word) > 15 for word in term.split()):  # 51%
        return False
    if len(term.split()) > 5:  # 28%
        return False
    if any(c in term for c in "█,!?:"):  # 18%
        return False
    if sum(ord(c) > 255 for c in term) > 2:  # 0.8%
        return False
    parts = term.split()
    short_parts = sum([len(w) < 3 for w in parts])
    if short_parts == len(parts):
        return False
    if len(parts) > 2 and short_parts >= len(parts) - 1:
        return False
    num_letters = len(re.findall("[a-zA-Z]", term))
    num_numbers = len(re.findall("[0-9]", term))
    if num_numbers > num_letters:
        return False
    decoded = unidecode(term)
    unicode_letters = len(term) - sum(term[n] == decoded[n] for n in range(len(term)))
    if unicode_letters > len(term) / 2:
        return False
    return True


def qualify_raw_term(term):
    """Does some qualification on the unprocessed term.
    """
    if "__" in term:  # 0.6%
        return False
    if "--" in term:  # 0.6%
        return False
    return True


def clean_and_qualify(term):
    """Returns a cleaned version of the term or False if it's rubbish."""
    if not qualify_raw_term(term):
        return False
    cleaned = clean(term)
    return qualify(cleaned) and cleaned
    

def clean(term):
    if not isinstance(term, unicode):
        term = term.decode('utf-8')

    term = term.strip(" \n[](),.!?`'\"")
    term = re.sub(r"[_\\%|@]", " ", term)
    term = re.sub(r"[()\[\]'\".!?`]", "", term)
    term = " ".join(term.split())  # Replace multiple white space
    return term
