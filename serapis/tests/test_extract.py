#!/usr/bin/env python
# coding=utf-8
"""
Collection of tests.

Tests methods need to start with "test_", otherwise you're free to do
whatever you want here.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-25"
__email__ = "clare@summer.ai"


test_response = {
    'url': 'http://nytimes.com/2015/10/04/technology/scouring-the-web-to-make-new-words-lookupable.html',
    'title': u'Scouring the Web to Make New Words \u2018Lookupable\u2019',
    'date': None,
    'author': 'Natasha Singer'
}


def test_page_request():
    from serapis.extract import PageRequest
    p = PageRequest('http://nytimes.com/2015/10/04/technology/scouring-the-web-to-make-new-words-lookupable.html')
    print p.response
    assert p.response


def test_page_structure():
    from serapis.extract import PageRequest
    p = PageRequest('http://nytimes.com/2015/10/04/technology/scouring-the-web-to-make-new-words-lookupable.html')

    assert p.structured['title'] == test_response['title']
    assert p.structured['url'] == test_response['url']
    assert len(p.structured['text_list']) > 0
    assert p.structured['author'] == test_response['author']
    assert len(p.structured['html']) > 0
    assert len(p.structured['text']) > 0
    assert p.structured['date'] == test_response['date']
