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


class PageRequest(object):
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
        'title'
        'author'
        'date'

    """
    def request_page(self):
        """
        Returns a utf-8 encoded string

        """
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

    def get_text(self):
        """
        Returns
        List of paragraph texts

        """
        text_cleaner = Cleaner(page_structure=False, links=False, scripts=False, javascript=False)

        self.unicode_html = self.parse_from_unicode(text_cleaner.clean_html(self.response.text))

        paragraphs = self.unicode_html.xpath('//p')
        return [unicode(el.text).strip('\n') for el in paragraphs if el.text and len(el.text.strip('\n')) > 8]

    def get_meta(self):
        """
        Scan meta tags for keys: 'title', 'author', 'date'

        If 'parsely-page' attribute exists, use those values

        Currently arbitrarily returns the first found value for each key

        TODO
        - Date may not always resolve to the same form
        - Metadata is sometimes in XML <PageMap> object

        """
        meta_html = self.parse_from_unicode(self.response.text)

        paragraphs = meta_html.xpath('//meta')
        meta_values = [{'name': m.attrib.get('name') or m.attrib.get('property'),
                        'value': m.attrib.get('content')} for m in paragraphs]

        meta_structured = {
            'author': None,
            'title': None,
            'date': None
        }

        parsely_key = [v for v in meta_values if v['name'] == 'parsely-page']

        try:
            parsley_dict = json.loads(parsely_key[0].get('value'))
            meta_structured['author'] = parsley_dict.get('author')
            meta_structured['title'] = parsley_dict.get('title')
            meta_structured['date'] = parsley_dict.get('pub_date')
        except:
            for key in meta_structured.keys():
                values = [v['value'] for v in meta_values if v['name'] and v['name'].find(key) > -1]
                meta_structured[key] = values[0] if values else None

        return meta_structured

    def get_structured_page(self):
        """
        Returns elements extracted from html

        """
        if not self.response:
            self.response = self.request_page()

        text = self.get_text()
        metadata = self.get_meta()

        self.structured = {
            "url": self.url,
            "html": self.response.text,
            "text_list": text,
            "text": " ".join(text),
            "date": metadata.get('date'),
            "title": metadata.get('title'), 
            "author": metadata.get('author') 
        }
        return self.structured

    def __init__(self, url):
        self.url = url
        self.response = self.request_page()
        self.structured = self.get_structured_page()


class DiffbotRequest:
    """
    Request for single page from Diffbot

    takes
    `url`

    Diffbot API returns json object

    """
    def get_article(self):
        self.params['url'] = self.url
        self.response = requests.get(self.diff_article_api, params=self.params).json()
        if not self.response.get('objects'):
            if self.response.get('error'):
                print("Response Error '{}' (code: {})".format(self.response['error'], self.response['errorCode']))
            else:
                print("NO RESULTS")
                raise Exception

        return self.response

    def get_structured_response(self):
        self.params['url'] = self.url
        self.response = self.get_article(self.url)

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

    def __init__(self, url):
        self.url = url
        self.response = None
        self.structured = None
        self.diff_article_api = 'http://api.diffbot.com/v3/article'
        self.params = {
            'token': config.credentials['diffbot'],
            'url': self.url
        }
