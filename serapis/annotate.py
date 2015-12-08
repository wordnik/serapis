#!/usr/bin/env python
# coding=utf-8
"""
Search module
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-12-07"
__email__ = "clare@summer.ai"

from textblob import TextBlob


def find_word(text, word):
    """
    Given (text, word)
    Returns sentence containing word and position  TODO

    """
    sentence = text
    positions = [i for i, x in enumerate(sentence.split()) if x == word]
    position = positions[0] or None
    return sentence, position


def structure_sentence(text, word):
    """
    Given (text, word)

    get sentence with word
    Stripped of all punctuation & accents, lower case, target term replaced with _TERM_
    Tokenised and POS-Tagged (Penn Treebank)
    Single feature marker for sentences, such as number of sub-clauses (os something that actually makes sense)
    
    Returns
    {   "s":         ...,
        "s_clean":   ...,
        "pos_tags": ...,
        "pos":       ...,
        "features":  ...  }
    """
    sentence, position = find_word(text, word)
    blob = TextBlob(sentence)
    pos = blob.pos_tags

    pos_tags = ['/'.join([b[0], b[1]]) for b in pos]
    pos = list(pos_tags)
    pos[position] = '_TERM_'

    structured = {
        's': sentence,  # need to extract the sentence
        's_clean': sentence.replace(word, '_TERM_'),
        'pos_tags': ' '.join(pos_tags),
        'pos': pos,
        'features': None
    }
    return structured
