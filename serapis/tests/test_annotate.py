#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-25"
__email__ = "clare@summer.ai"


test_text = 'A kalyptic culture is typified by peacefulness, tolerance and individualism.'
test_term = 'kalyptic'
test_output = {
    u's': 'A kalyptic culture is typified by peacefulness, tolerance and individualism.',
    u's_clean': u'A _TERM_ culture is typified by peacefulness, tolerance and individualism.',
    u'pos_tags': u'A/DT _TERM_/JJ culture/NN is/VBZ typified/VBN by/IN peacefulness/NN tolerance/NN and/CC individualism/NN',
    u'features': {},
}


def test_page_structure():
    from serapis.annotate import annotate_sentence
    s = {
        's': test_text,
        's_clean': u'A _TERM_ culture is typified by peacefulness, tolerance and individualism.'
    }
    output = annotate_sentence(s, test_term)

    for key in test_output.keys():
        assert output[key] == test_output[key]
