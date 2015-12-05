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

print config.keys

class DiffbotRequest:
    """
    Request for single page from Diffbot

    takes
    `url`

    Diffbot API returns json object

    Instance???

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

class DiffbotBatchRequest(object):
    """
    STUB

    Diffbot batch

    """
    def __init__(self):
        self.name = None
