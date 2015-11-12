#!/usr/bin/env python3
# coding=utf-8
"""
Search result qualification module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import datetime
from objects import Term


def qualify(term: Term) -> bool:
    """Decides whether a search result is relevant."""
    # Dummy: Only process results that are newer than October
    return term.date > datetime.date(2015, 10, 1)
