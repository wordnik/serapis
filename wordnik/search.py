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
from typing import Optional, Callable
from objects import Term


def search(term: Term, domains: Optional[list]=None, filter: Optional[Callable]=None):
    """Searches the Internet for a word. Yields dictionaries
    of results like this:

        {
            'url': '...',
            'date': '...'
        }

    The filter argument can be a method that should return True for all results
    that are qualified.
    """
    domains = domains or config.domains
    # Search for term.term
    for search_result in fixtures["search"]:
        result = term.copy()
        result.url = search_result['url']
        result.domain = search_result['domain']
        result.date = search_result['date']
        result.title = search_result['title']
        result.summary = search_result['summary']

        if not filter or filter(result):
            yield result
