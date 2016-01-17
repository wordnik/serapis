#!/usr/bin/env python
# coding=utf-8
"""
DOC
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-24"
__email__ = "manuel@summer.ai"

import re
import serapis.patterns

patterns = serapis.patterns.compile()
for rule, pattern in patterns.items():
    patterns[rule] = re.compile(pattern, re.IGNORECASE)


def match_wordnik_rules(s_clean):
    """Returns all rules that match the sentence. E.g.

        match_wordnik_rules("A tattoo of Donald Trump, or, in other words, a Trump Stamp.", "Trump Stamp")

    Returns [u'KO16', u'KO3']
    """
    s_clean = s_clean.replace("'_TERM_'", "_TERM_").replace(",", "").lower()
    return [rule for rule, pattern in patterns.items() if pattern.search(s_clean.lower())]
