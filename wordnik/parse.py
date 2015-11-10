#!/usr/bin/env python3
# coding=utf-8
"""
Search result parser module
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

from config import fixtures


def parse(searchresult: dict):
    """Parses a search result and extracts the body text. Yields dictionaries
    of results like this:

        {
            'url': '...',
            'date': '...',
            'body': '...',
            'author': '...'
        }
    """
    result = searchresult.copy()
    parsed_data = fixtures["parser"][result['url']]
    result.update(parsed_data)
    return result
