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


def match(sentence):
    clean = sentence.lower().replace(",", "").replace("'_term_'", "_term_")
    return {rule: bool(pattern.search(clean)) for rule, pattern in patterns.items()}
