#!/usr/bin/env python
# coding=utf-8
"""
DOC
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from unidecode import unidecode

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-24"
__email__ = "manuel@summer.ai"

import re
import serapis.patterns

patterns = serapis.patterns.compile()
for rule, pattern in patterns.items():
    patterns[rule] = re.compile(pattern, re.IGNORECASE)


def match(sentence, term):
    """Returns all rules that match the sentence. E.g.

        match("A tattoo of Donald Trump, or, in other words, a Trump Stamp.", "Trump Stamp")

    Returns [u'KO16', u'KO3']
    """
    clean = unidecode(sentence).lower().replace(",", "").replace(unidecode(term).lower(), "_term_").replace("'_term_'", "_term_")
    return [rule for rule, pattern in patterns.items() if pattern.search(clean)]
