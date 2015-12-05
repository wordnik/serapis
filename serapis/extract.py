#!/usr/bin/env python
# coding=utf-8
"""
Extract module
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-20"
__email__ = "clare@summer.ai"

import requests
import json
from .config import config  # Make sure to use absolute imports here
from lxml.html.clean import Cleaner
from lxml import etree

class PageRequest:
    """
    Request for single page

    initialize with param
    `url`

    returns attributes
    .response
    .structured

        'url'
        'html'
        'text'
        'title' - TODO
        'author' - TODOD

    """
    def request_page(self):
        try:
            self.response = requests.get(self.url)
            return self.response
        except:
            print("Failed to return page")
            raise Exception

    def parse_from_unicode(self, unicode_str):
        utf8_parser = etree.HTMLParser(encoding='utf-8')
        s = unicode_str.encode('utf-8')
        return etree.fromstring(s, parser=utf8_parser)

    def get_text(self, html):
        t = self.parse_from_unicode(html)
        paragraphs = t.xpath('//p')
        return [unicode(el.text).strip('\n') for el in paragraphs \
            if el.text and len(el.text.strip('\n')) > 8] # lists of paragraph text

    def get_structured_page(self):
        text_cleaner = Cleaner(page_structure=False, links=False, \
            scripts=False, javascript=False)
        header_cleaner = Cleaner(page_structure=True)

        if not self.response:
            self.response = self.request_page()

        text = self.get_text(text_cleaner.clean_html(self.response.text))

        self.structured = {
            "url": self.url,
            "html": self.response.text,
            "text": text,
            "title": None,
            "author": None,
        }
        return self.structured

    def __init__(self, url):
        self.url = url
        self.response = None
        self.structured = None


class DiffbotRequest:
    """
    Request for single page from Diffbot

    takes
    `url`

    Diffbot API returns json object

    """
    def get_article(self, url):
        self.params['url'] = url
        self.response = requests.get(self.diff_article_api, params=self.params).json()
        if not self.response.get('objects'):
            if self.response.get('error'):
                print("Response Error '{}' (code: {})".format(self.response['error'], self.response['errorCode']))
            else:
                print("NO RESULTS")
                raise Exception

        return self.response

    def get_structured_response(self, url):
        self.params['url'] = url
        self.response = self.get_article(url)

        results = list()
        for object in self.response.get('objects', []):
            if object.get('text'):
                result = {
                    "title": object.get('title'),
                    "url": object.get('pageUrl'),
                    "author": object.get('author'),
                    "html": object.get('html'),
                    "tags": object.get('tags'),
                    "doc": object.get('text'),
                    # "date": parse_date(object.get('date', '')).isoformat(),
                }
                results.append(result)
        self.structured = results
        return results

    def __init__(self):
        self.response = None
        self.structured = None
        self.diff_article_api = 'http://api.diffbot.com/v3/article'
        self.params = {
            'token': config.credentials['diffbot'],
            'url': None
        }


