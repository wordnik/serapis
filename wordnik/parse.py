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
from objects import Term
from typing import Generator


def parse(term: Term):
    """Parses a search result and extracts the body text. Yields dictionaries
    of results like this:

        {
            'url': '...',
            'date': '...',
            'body': '...',
            'author': '...'
        }
    """
    result = term.copy()
    parsed_data = fixtures["parser"][result.url]
    result.document = parsed_data['body']
    result.author = parsed_data['author']
    return result


def parse_batch(terms: list) -> Generator:
    for term in terms:
        result = term.copy()
        parsed_data = fixtures["parser"][result.url]
        result.document = parsed_data['body']
        result.author = parsed_data['author']
        yield result
