#!/usr/bin/env python
# coding=utf-8
"""
Annotate module
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-12-07"
__email__ = "clare@summer.ai"

import re
from nltk import pos_tag, word_tokenize, pos_tag_sents


def get_snippets(word, doc):
    """
    Given word and doc
    Returns any snippets from doc containing word

    NB: Does not always properly deal with em-dashes (u'\u2014')

    """
    locations = [m.start() for m in re.finditer(word, doc)]

    snippets = []

    for loc in locations:
        start = loc - 200
        end = loc + len(word) + 200
        tokenized = sent_tokenize(doc[start:end])
        for i in tokenized:
            if i.lower().find(word.lower()) > -1:
                snippets.append(i)

    return snippets


def find_word(doc, word):
    """
    Given (doc, word)
    Returns sentences containing word and position

    """
    sentence = doc
    positions = [i for i, x in enumerate(sentence.split()) if x == word]
    position = positions[0] or None
    return sentence, position

def annotate_sentence(sentence_dict, term):
    """Annotates a sentence object from a message with Penn Treebank POS tags.

    Args:
        sentence_dict: dict -- Must contain 's' and 's_clean', which is the
                       sentence with all occurrences of the search term
                       replaced with '_TERM-'
    Returns:
        dict -- updated sentence_dict with 'pos_tags' field.
    """
    tags = pos_tag(word_tokenize(sentence_dict['s_clean']))
    pos_tags = ['/'.join(b) for b in tags]
    sentence_dict['pos_tags'] = " ".join(pos_tags)
    sentence_dict['features'] = {}
    return sentence_dict
