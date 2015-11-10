#!/usr/bin/env python3
# coding=utf-8
"""
Search module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

from config import config, fixtures
from typing import Optional


def search(word: str, domains: Optional[list]=None):
    """Searches the Internet for a word. Yields dictionaries
    of results like this:

        {
            'url': '...',
            'date': '...'
        }
    """
    domains = domains or config.domains
    for result in fixtures["search"]:
        yield result
