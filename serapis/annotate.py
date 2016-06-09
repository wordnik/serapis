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
import logging

log = logging.getLogger('serapis.annotate')


def batch_tag_sentences(message_dict):
    """
    Uses a more efficient way of tagging all sentences for a given
    message at once.

    """
    num_sentences = [len(page['sentences']) for page in message_dict['urls']]
    all_sentences = [word_tokenize(s['s_clean']) for page in message_dict['urls'] for s in page['sentences']]
    all_tags = pos_tag_sents(all_sentences)

    for page_index, slice_length in enumerate(num_sentences):
        slice_start = sum(num_sentences[:page_index])
        slice_end = slice_start + slice_length
        for sentence_index, tags in enumerate(all_tags[slice_start:slice_end]):
            pos_tags = ['/'.join(b) for b in tags]
            message_dict['urls'][page_index]['sentences'][sentence_index]['pos_tags'] = ' '.join(pos_tags)


def annotate_single_sentence(sentence):
    tags = pos_tag(word_tokenize(sentence))
    pos_tags = ['/'.join((b[0].lower(), b[1])) for b in tags]
    return " ".join(pos_tags)


def annotate_pos_with_term(sentence, term):
    """POS-tag single sentence while preserving _TERM_ using the original term"""
    try:
        pos_term = []

        # replace term if necessary
        if '_term_' not in sentence.lower():
            sentence_term = sentence.lower().replace(term.lower(), '_TERM_')
        else:
            sentence_term = sentence.lower()

        tok = word_tokenize(sentence_term)
        tags = pos_tag(tok)

        for tag in tags:
            if '_TERM_' in tag[0].upper():
                pos_term.append('_TERM_')
            else:
                pos_term.append(tag[1])

        return ' '.join(pos_term)
    except Exception, e:
        log.error('POS annotation error: %s', e)
        return None


def get_pos_term_context(sentence, ngrams=5):
    """
    Returns just POS tags while preserving _TERM_

    Returns substring context around _TERM_
    as defined by number of `ngrams` preceding and following _TERM_

    """
    s = sentence.split()
    try:
        loc = s.index("_TERM_")
    except Exception, e:
        return -1
        log.warning("_TERM_ not found in pos tags. %s", e)
    back = loc - ngrams + 1
    if back < 0:  # we don't want negative indicies
        back = 0
    forward = loc + ngrams - 1
    return ' '.join(s[back:forward])


def annotate_sentence(sentence_dict, term):
    """
    Annotates a sentence object from a message with Penn Treebank POS tags.

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
    if not url_object.get('doc'):
        url_object['readability_score'] = None
        return
    scores = Readability(url_object['doc'])
    url_object['readability_score'] = scores.fleisch_reading_ease()
