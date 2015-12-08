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
from unidecode import unidecode
import re
import logging


log = logging.getLogger('serapis.extract')


class PageRequest(object):
    """
    Request for single page

    initialize with param
    `url` and `term`

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

    OPENING_QUOTE = '|'.join(("\"", "'", "&quot;", "“", "&ldquo;", "‘", "&lsquo;", "«", "&laquo;", "‹", "&lsaquo;", "„", "&bdquo;", "‚", "&sbquo;"))
    CLOSING_QUOTE = '|'.join(("'", "&quot;", "”", "&rdquo;", "’", "&rsquo;", "»", "&raquo;", "›", "&rsaquo;", "“", "&ldquo;", "‘", "&lsquo;"))

    def request_page(self):
        """
        Returns a utf-8 encoded string

        """
        try:
            self.response = requests.get(self.url, timeout=3)
            return self.response
        except:
            log.error("Failed to return page for url: %s" % self.url)
            return None

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
        - Metadata is sometimes in XML <PageMap> object

        """
        meta_html = self.parse_from_unicode(self.response.text)

        paragraphs = meta_html.xpath('//meta')
        meta_values = [{'name': m.attrib.get('property') or m.attrib.get('name'),
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
                values = [v['value'] for v in meta_values if v['name'] and v['name'] == key or v['name'] == 'og:' + key]
                meta_structured[key] = values[0] if values else None

        return meta_structured

    def get_html_features(self):
        """Detects whether the search term exists is highlighted (bolded, emphasised) or
        in quotes. Needs to be called after self.request_page.

        Returns:
            dict -- dict of bools for different features.
        """
        minimal_html = unidecode(self.response.text).replace("-", "").replace(" ", "")
        minimal_term = unidecode(self.term).replace("-", "").replace(" ", "")

        highlight_re = r"<(em|i|b|strong|span)[^>]*> *{}[ ,:]*</\1>".format(minimal_term)
        quote_re = r"<({})[^>]*> *{}[ ,:]*</({})>".format(self.OPENING_QUOTE, minimal_term, self.CLOSING_QUOTE)

        features = {
            "highlighted": bool(re.search(highlight_re, minimal_html, re.IGNORECASE)),
            "quotes": bool(re.search(quote_re, minimal_html, re.IGNORECASE)),
        }
        return features
        
    def get_structured_page(self):
        """
        Returns elements extracted from html

        """
        if not self.response:
            return None

        text = " ".join(self.get_text())
        metadata = self.get_meta()

        self.structured = {
            "url": self.url,
            "html": self.response.text,
            "doc": text,
            "date": metadata.get('date'),
            "features": self.get_html_features(),
            "title": metadata.get('title'),
            "author": metadata.get('author')
        }

        if config.save_html:
            self.structured["html"] = self.response.text

        return self.structured

    def __init__(self, url, term):
        self.url = url
        self.term = term
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
