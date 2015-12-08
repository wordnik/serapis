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
    u'features': None,
    u'pos': [u'A/DT',
             u'_TERM_',
             u'culture/NN',
             u'is/VBZ',
             u'typified/VBN',
             u'by/IN',
             u'peacefulness/NN',
             u'tolerance/NN',
             u'and/CC',
             u'individualism/NN'],
    u'pos_tags': u'A/DT kalyptic/JJ culture/NN is/VBZ typified/VBN by/IN peacefulness/NN tolerance/NN and/CC individualism/NN',
    u's': 'A kalyptic culture is typified by peacefulness, tolerance and individualism.',
    u's_clean': u'A _TERM_ culture is typified by peacefulness, tolerance and individualism.'
}


def test_page_structure():
    from serapis.annotate import structure_sentence
    output = structure_sentence(test_text, test_term)

    for key in test_output.keys():
        assert output[key] == test_output[key]
