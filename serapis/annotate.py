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

from nltk import pos_tag, word_tokenize, pos_tag_sents
from .readability import Readability


def batch_tag_sentences(message_dict):
    """Uses a more efficient way of tagging all sentences for a given
    message at once."""
    num_sentences = [len(page['sentences']) for page in message_dict['urls']]
    all_sentences = [word_tokenize(s['s_clean']) for page in message_dict['urls'] for s in page['sentences']]
    all_tags = pos_tag_sents(all_sentences)

    for page_index, slice_length in enumerate(num_sentences):
        slice_start = sum(num_sentences[:page_index])
        slice_end = slice_start + slice_length
        for sentence_index, tags in enumerate(all_tags[slice_start:slice_end]):
            pos_tags = ['/'.join(b) for b in tags]
            message_dict['urls'][page_index]['sentences'][sentence_index]['pos_tags'] = ' '.join(pos_tags)


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


def readability_score(url_object):
    """
    Calculates the Fleisch Reading Ease (https://simple.wikipedia.org/wiki/Flesch_Reading_Ease)
    for a document and saves it as 'readability_score' into the url_object

    Args:
        url_object: dict
    """
    scores = Readability(url_object['doc'])
    url_object['readability_score'] = scores.fleisch_reading_ease()
