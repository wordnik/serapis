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
from lxml import etree
from .config import config  # Make sure to use absolute imports here
import html2text
from serapis.util import squashed
from serapis.util import collect_variants
from serapis.util import multiple_replace
import re
import logging
from nltk.tokenize import sent_tokenize


log = logging.getLogger('serapis.extract')
html_parser = html2text.HTML2Text()
html_parser.ignore_links = html_parser.ignore_images = html_parser.ignore_emphasis = True
html_parser.body_width = 0


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

    def extract_sentences(self, page_text):
        """Finds all sentences that contain the term or a spelling variants.
        Sets self.sentences ans self.variants.

        Args:
            page_text: str
        Returns
            str -- cleaned page text.
        """
        def qualify_paragraph(p):
            if len(p) > 30 and \
               p.count("\n") < 3 and \
               p.count("---") < 3:
                return True

        doc = []
        for paragraph in page_text.split('\n\n'):
            if qualify_paragraph(paragraph):
                for sentence in sent_tokenize(paragraph):
                    sentence = sentence.strip(" *#")
                    doc.append(sentence)
                    variants = collect_variants(sentence, self.term)
                    if variants:
                        self.variants.update(variants)
                        s_clean = multiple_replace(sentence, {v: "_TERM_" for v in variants})
                        self.sentences.append({
                            's': sentence,
                            's_clean': s_clean
                        })
        return " ".join(doc)

    def get_meta(self):
        """
        Scan meta tags for keys: 'title', 'author', 'date'

        If 'parsely-page' attribute exists, use those values

        Currently arbitrarily returns the first found value for each key

        TODO
        - Metadata is sometimes in XML <PageMap> object

        """
        # Common ways to encode authorship information
        prop_names = {
            "name": "author",  # W3C
            "property": "og:author",  # Facebook OG
            "property": "article:author",  # Pinterest and Twitter meta
        }
        authors = []

        tree = etree.HTML(self.response.text)  # TODO may change this to response.content, access as bytes
        for prop, value in prop_names.items():
            tags = tree.xpath("//meta[@{}='{}']".format(prop, value))
            authors.extend([tag.attrib.get('content') for tag in tags])

        # Pick the first author that looks reasonable
        authors = filter(lambda author: author and not author.startswith("http"), authors)
        author = authors[0] if authors else None

        title_tags = tree.xpath("//title")
        title = title_tags[0].text if title_tags else None

        return {
            'author': author,
            'title': title
        }

    def get_html_features(self, html):
        """Detects whether the search term exists is highlighted (bolded, emphasised) or
        in quotes. Needs to be called after self.request_page.

        Returns:
            dict -- dict of bools for different features.
        """
        if not self.term:
            return None

        minimal_html = squashed(html, keep='<>/&;')
        minimal_term = squashed(self.term)

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

        html = self.response.text
        self.text = self.extract_sentences(html_parser.handle(html))
        self.features = self.get_html_features(html)

        self.structured = {
            "term": self.term,
            "url": self.url,
            "doc": self.text,
            "features": self.features,
            "variants": list(self.variants),  # Sets are not JSON serializable
            "sentences": self.sentences
        }

        self.structured.update(self.get_meta())

        if config.save_html:
            self.structured["html"] = html

        return self.structured

    def __init__(self, url, term):
        self.url = url
        self.term = term
        self.variants = set()
        self.sentences = []
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
